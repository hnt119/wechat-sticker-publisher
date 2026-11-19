"""Image validation and export regression tests using generated artwork."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw, PngImagePlugin

from wechat_sticker_publisher.imaging import inspect_image, preview, process_image, validate_image


class ImageWorkflowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.output = self.root / "exports"

    def drawing(self, name="drawing.png", size=(240, 240), clear=True):
        canvas = Image.new("RGBA", size, (0, 0, 0, 0) if clear else "white")
        ImageDraw.Draw(canvas).ellipse((0, 0, size[0] // 2, size[1] // 2), fill="#7b2591")
        path = self.root / name
        canvas.save(path)
        return path

    def motion(self, size=(240, 240), loop=0, durations=(100, 70, 120), clear=False):
        frames = []
        # Reserve palette entry zero for the matte where transparency is tested.
        for i in range(3):
            frame = Image.new("P", size, 0)
            frame.putpalette([255, 255, 255, 47, 85, 125] + [0] * (768 - 6))
            x = (size[0] // 4) * i
            ImageDraw.Draw(frame).rectangle((x, 5, x + 18, 25), fill=1)
            frames.append(frame)
        options = {"loop": loop} if loop is not None else {}
        if clear:
            options["transparency"] = 0
        path = self.root / "motion.gif"
        frames[0].save(path, save_all=True, append_images=frames[1:], disposal=2,
                       duration=durations, optimize=False, **options)
        return path

    def test_compliant_copy_and_exact_dimensions(self):
        source = self.drawing()
        self.assertEqual(validate_image(source, "sticker", "static"), [])
        result = process_image(source, self.output, "one", "sticker", "static")
        self.assertEqual(result["action"], "REUSE")
        self.assertEqual((self.output / result["file"]).read_bytes(), source.read_bytes())
        self.assertTrue(validate_image(source, "icon", "static"))

    def test_file_size_boundary_is_inclusive(self):
        source = self.drawing(size=(50, 50))
        with source.open("ab") as stream:
            stream.write(bytes(100_000 - source.stat().st_size))
        self.assertEqual(validate_image(source, "icon", "static"), [])
        with source.open("ab") as stream:
            stream.write(b"!")
        self.assertTrue(any("100000" in error for error in validate_image(source, "icon", "static")))
        result = process_image(source, self.output, "icon", "icon", "static")
        self.assertEqual(result["action"], "DERIVE")
        self.assertLess(result["info"]["bytes"], 100_000)

    def test_transparency_is_checked_on_pixels(self):
        opaque = self.drawing(clear=False)
        self.assertTrue(validate_image(opaque, "cover", "static"))
        # An RGBA container can be perfectly opaque.
        self.assertFalse(inspect_image(opaque)["transparent"])
        self.assertTrue(validate_image(self.drawing(size=(750, 400)), "banner", "static"))
        self.assertEqual(validate_image(self.drawing(size=(750, 560), clear=False),
                                        "appreciation-guide", "static"), [])
        blank = self.root / "blank.png"
        Image.new("RGBA", (240, 240)).save(blank)
        self.assertEqual(process_image(blank, self.output, "empty", "cover", "static")["action"], "BLOCK")

    def test_aspect_ratio_is_preserved_and_master_is_intact(self):
        source = self.drawing(size=(400, 200))
        master = source.read_bytes()
        result = process_image(source, self.output, "cover", "cover", "static")
        self.assertEqual(result["action"], "DERIVE")
        with Image.open(self.output / result["file"]) as image:
            self.assertEqual(image.size, (240, 240))
            left, top, right, bottom = image.getchannel("A").getbbox()
        self.assertAlmostEqual((right - left) / (bottom - top), 2, delta=0.08)
        self.assertEqual(source.read_bytes(), master)

    def test_appreciation_jpeg_imported_but_exported_as_png(self):
        source = self.root / "drawing.jpg"
        Image.new("RGB", (750, 560), "grey").save(source)
        self.assertTrue(validate_image(source, "appreciation-guide", "static"))
        self.assertEqual(process_image(source, self.output, "thanks", "appreciation-guide", "static")
                         ["info"]["format"], "PNG")

    def test_visual_hash_ignores_container_metadata_and_hidden_rgb(self):
        p1 = self.drawing()
        p2 = self.root / "alternate.png"
        with Image.open(p1) as image:
            image.putpixel((239, 239), (18, 210, 19, 0))
            metadata = PngImagePlugin.PngInfo()
            metadata.add_text("test", "different metadata")
            image.save(p2, pnginfo=metadata)
        self.assertNotEqual(p1.read_bytes(), p2.read_bytes())
        self.assertEqual(inspect_image(p1)["visual_hash"], inspect_image(p2)["visual_hash"])

    def test_motion_requirements_and_timing(self):
        source = self.motion()
        info = inspect_image(source)
        self.assertEqual((info["frames"], info["distinct_frames"], info["loop"]), (3, 3, 0))
        self.assertEqual(info["duration_ms"], 290)
        self.assertEqual(validate_image(source, "sticker", "animated"), [])
        self.assertTrue(validate_image(source, "sticker", "static"))
        self.assertTrue(validate_image(self.drawing(), "sticker", "animated"))
        self.assertTrue(validate_image(self.motion(loop=None), "sticker", "animated"))
        self.assertTrue(validate_image(self.motion(durations=(0, 70, 120)), "sticker", "animated"))

    def test_motion_resize_preserves_timing_alpha_and_displayed_motion(self):
        source = self.motion(size=(120, 120), loop=2, clear=True)
        result = process_image(source, self.output, "motion", "sticker", "animated")
        self.assertEqual(result["action"], "DERIVE")
        self.assertEqual(result["info"]["durations_ms"], [100, 70, 120])
        self.assertEqual(result["info"]["loop"], 0)
        self.assertEqual(result["info"]["distinct_frames"], 3)
        with Image.open(self.output / result["file"]) as gif:
            for i in range(3):
                gif.seek(i)
                frame = gif.convert("RGBA")
                self.assertEqual(frame.getpixel((60 * i + 10, 20))[-1], 255)
                self.assertEqual(frame.getpixel((60 * ((i + 1) % 3) + 10, 20))[-1], 0)

    def test_repeated_poses_do_not_pass_as_motion(self):
        # Construct two displayed frames with identical RGB but different palette
        # indices. Adding source frames alone would let Pillow coalesce them.
        source = self.motion(clear=False)
        data = source.read_bytes().replace(bytes((47, 85, 125)), bytes((255, 255, 255)))
        source.write_bytes(data)
        info = inspect_image(source)
        self.assertGreater(info["frames"], 1)
        self.assertEqual(info["distinct_frames"], 1)
        self.assertTrue(validate_image(source, "sticker", "animated"))

    def test_unreadable_input_is_reported_and_export_names_do_not_clobber(self):
        corrupt = self.root / "corrupt.jpg"
        corrupt.write_bytes(b"broken")
        self.assertEqual(process_image(corrupt, self.output, "one", "sticker", "static")["action"], "BLOCK")
        source = self.drawing()
        process_image(source, self.output, "one", "sticker", "static")
        with self.assertRaises(FileExistsError):
            process_image(source, self.output, "one", "sticker", "static")
        with self.assertRaises(ValueError):
            process_image(source, self.output, "../outside", "sticker", "static")
        self.assertFalse((self.root / "outside.png").exists())

    def test_contact_sheet_is_deterministic(self):
        paths = [self.drawing(), self.motion()]
        first = self.root / "preview.png"
        second = self.root / "preview2.png"
        preview(paths, first)
        preview(paths, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with Image.open(first) as sheet:
            self.assertGreater(sheet.width, 240)
            self.assertEqual(sheet.format, "PNG")

    def test_contact_sheet_labels_keep_exported_ids_after_missing_inputs(self):
        source = self.drawing(name="02.png")
        cover = self.drawing(name="cover.png")
        with patch.object(ImageDraw.ImageDraw, "text", autospec=True) as text:
            preview([source, cover], self.root / "incomplete.png")
        self.assertEqual([call.args[2] for call in text.call_args_list], ["02", "cover"])

    def test_clear_interior_hole_is_not_a_transparent_background(self):
        path = self.root / "hole.png"
        for role, size in (("cover", (240, 240)), ("icon", (50, 50))):
            canvas = Image.new("RGBA", size, "teal")
            canvas.putpixel((12, 15), (0, 0, 0, 0))
            canvas.save(path)
            self.assertTrue(validate_image(path, role, "static"))
            canvas.putpixel((0, 15), (0, 0, 0, 0))
            canvas.save(path)
            self.assertEqual(validate_image(path, role, "static"), [])

    def test_non_square_opaque_export_extends_the_original_ground(self):
        path = self.root / "colored-master.png"
        canvas = Image.new("RGB", (300, 200), "#6ab8c1")
        ImageDraw.Draw(canvas).ellipse((80, 35, 200, 155), fill="purple")
        canvas.save(path)
        result = process_image(path, self.output, "banner", "banner", "static")
        self.assertEqual(result["action"], "DERIVE")
        with Image.open(self.output / result["file"]) as banner:
            self.assertEqual(banner.getpixel((0, banner.height // 2)), (106, 184, 193))
