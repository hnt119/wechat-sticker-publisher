"""Exercise request and privacy boundaries without installing or calling the SDK."""

import base64
import os
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PIL import Image, PngImagePlugin

from wechat_sticker_publisher.artwork import ProviderSetupError
from wechat_sticker_publisher.optional_openai import OpenAIImages


class OpenAIImagesTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.output = self.folder / "output.png"
        self.brief = dict(
            role="cover", album_name="春日", description="春日里嬉戏", characters=["sprout"],
            direction="Draw a sprout.", size_px=[240, 240], background="transparent",
            references=["sensitive/private-reference.png"], supply_at="private/path.png",
        )
        buffer = BytesIO()
        Image.new("RGB", (20, 20), "green").save(buffer, format="PNG")
        self.data = buffer.getvalue()
        self.client = Mock()
        answer = SimpleNamespace(data=[SimpleNamespace(b64_json=base64.b64encode(self.data).decode("ascii"))])
        self.client.images.edit.return_value = answer
        self.client.images.generate.return_value = answer
        self.constructor = Mock(return_value=self.client)
        module = SimpleNamespace(OpenAI=self.constructor)
        self.enter_patch(patch.dict(sys.modules, {"openai": module}))
        self.enter_patch(patch.dict(os.environ, {"OPENAI_API_KEY": "local-test-value",
                                                "WECHAT_STICKER_IMAGE_MODEL": "fixture-model"}))

    def enter_patch(self, manager):
        manager.start()
        self.addCleanup(manager.stop)

    def test_without_references_sends_only_art_direction_and_one_generation(self):
        OpenAIImages().generate(self.brief, [], self.output)
        self.constructor.assert_called_once_with(api_key="local-test-value", max_retries=0,
                                                 base_url="https://api.openai.com/v1")
        self.client.images.edit.assert_not_called()
        self.client.images.generate.assert_called_once()
        options = self.client.images.generate.call_args.kwargs
        self.assertEqual(options["model"], "fixture-model")
        self.assertEqual(options["n"], 1)
        self.assertEqual(options["size"], "1024x1024")
        self.assertEqual(options["background"], "transparent")
        self.assertEqual(options["output_format"], "png")
        self.assertIn("Draw a sprout.", options["prompt"])
        self.assertNotIn("private", options["prompt"])
        self.assertEqual(self.output.read_bytes(), self.data)

    def test_edits_include_only_approved_pixels_without_filenames_or_metadata(self):
        approved = self.folder / "private-original.png"
        notes = PngImagePlugin.PngInfo()
        notes.add_text("internal", "embedded private note")
        Image.new("RGBA", (20, 20), (25, 50, 75, 200)).save(approved, pnginfo=notes)
        second = self.folder / "private-master.jpg"
        Image.new("RGB", (20, 10), "blue").save(second)
        (self.folder / "unrequested.png").write_bytes(self.data)
        self.brief.update(role="banner", size_px=[750, 400], background="opaque")
        OpenAIImages().generate(self.brief, [approved, second], self.output)
        self.client.images.generate.assert_not_called()
        self.client.images.edit.assert_called_once()
        options = self.client.images.edit.call_args.kwargs
        self.assertEqual(options["size"], "1536x1024")
        self.assertEqual(options["background"], "opaque")
        files = options["image"]
        self.assertEqual([item[0] for item in files], ["reference-1.png", "reference-2.png"])
        with Image.open(BytesIO(files[0][1])) as image:
            self.assertEqual(image.getpixel((1, 1)), (25, 50, 75, 200))
            self.assertNotIn("internal", image.info)
        self.assertNotIn("private", options["prompt"])

    def test_configuration_failure_is_actionable_without_starting_sdk(self):
        with patch.dict(os.environ, {"WECHAT_STICKER_IMAGE_MODEL": ""}):
            with self.assertRaisesRegex(ProviderSetupError, "WECHAT_STICKER_IMAGE_MODEL"):
                OpenAIImages()
        with patch.dict(sys.modules, {"openai": None}):
            with self.assertRaisesRegex(ProviderSetupError, "pip install"):
                OpenAIImages()
        self.constructor.assert_not_called()

    def test_malformed_response_fails_without_writing_output(self):
        self.client.images.generate.return_value = SimpleNamespace(data=[SimpleNamespace(b64_json=None)])
        with self.assertRaisesRegex(ValueError, "base64"):
            OpenAIImages().generate(self.brief, [], self.output)
        self.assertFalse(self.output.exists())
