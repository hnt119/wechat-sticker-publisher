"""Offline inspection, preparation and proof sheets for publishing images."""

from __future__ import annotations

import hashlib
import shutil
import struct
from collections import Counter
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError


@dataclass(frozen=True)
class ImageRule:
    size: tuple[int, int]
    formats: tuple[str, ...]
    max_bytes: int
    alpha: str


INPUT_FORMATS = ("PNG", "JPEG", "GIF")
EXTENSIONS = {"PNG": ".png", "JPEG": ".jpg", "GIF": ".gif"}
RULES = {
    "sticker": ImageRule((240, 240), INPUT_FORMATS, 500_000, "any"),
    "banner": ImageRule((750, 400), ("JPEG", "PNG"), 500_000, "opaque"),
    "cover": ImageRule((240, 240), ("PNG",), 500_000, "transparent"),
    "icon": ImageRule((50, 50), ("PNG",), 100_000, "transparent"),
    "appreciation-guide": ImageRule((750, 560), ("PNG", "GIF"), 500_000, "opaque"),
    "appreciation-thanks": ImageRule((750, 750), ("PNG", "GIF"), 500_000, "opaque"),
}


def _edges(image: Image.Image) -> tuple[Image.Image, ...]:
    width, height = image.size
    return (
        image.crop((0, 0, width, 1)), image.crop((0, height - 1, width, height)),
        image.crop((0, 0, 1, height)), image.crop((width - 1, 0, width, height)),
    )


def inspect_image(path: Path) -> dict[str, Any]:
    """Read displayed pixels of every frame, including GIF disposal/compositing."""
    try:
        with Image.open(path, formats=INPUT_FORMATS) as image:
            width, height = image.size
            image_format = image.format
            orientation = image.getexif().get(274, 1)
            loop = image.info.get("loop")
            count = getattr(image, "n_frames", 1)
            sequence = hashlib.sha256(struct.pack(">II", width, height))
            durations: list[int] = []
            previous = None
            unique: set[bytes] = set()
            minimum_alpha, maximum_alpha = 255, 0
            clear_edge = False
            for index in range(count):
                image.seek(index)
                rgba = image.convert("RGBA")
                # Clear hidden RGB under zero alpha so palette and metadata changes
                # cannot disguise two identical sticker illustrations.
                displayed = Image.alpha_composite(Image.new("RGBA", rgba.size), rgba)
                frame_hash = hashlib.sha256(displayed.tobytes()).digest()
                if previous != frame_hash:
                    sequence.update(frame_hash)
                previous = frame_hash
                unique.add(frame_hash)
                alpha = rgba.getchannel("A")
                low, high = alpha.getextrema()
                if low == 0 and not clear_edge:
                    clear_edge = any(edge.getextrema()[0] == 0 for edge in _edges(alpha))
                minimum_alpha = min(minimum_alpha, low)
                maximum_alpha = max(maximum_alpha, high)
                durations.append(int(image.info.get("duration", 0)))

        return {
            "format": image_format,
            "width": width,
            "height": height,
            "bytes": path.stat().st_size,
            "frames": count,
            "distinct_frames": len(unique),
            "durations_ms": durations,
            "duration_ms": sum(durations),
            "loop": loop,
            "min_alpha": minimum_alpha,
            "max_alpha": maximum_alpha,
            "clear_edge": clear_edge,
            "transparent": minimum_alpha < 255,
            "visible": maximum_alpha > 0,
            "visual_hash": sequence.hexdigest(),
            "orientation": orientation,
        }
    except FileNotFoundError:
        return {"error": "File is missing. Supply the source image at its manifest path."}
    except UnidentifiedImageError:
        return {"error": "Unrecognized image. Supply a readable PNG, JPG or GIF."}
    except (OSError, ValueError, EOFError, SyntaxError, Image.DecompressionBombError):
        return {"error": "Image could not be fully decoded. Re-export the artwork as PNG, JPG or GIF."}


def _content_issues(info: dict[str, Any], role: str, album_type: str) -> list[str]:
    """Conditions that resizing or compression cannot fix faithfully."""
    issues = []
    frames = info["frames"]
    if not info["visible"]:
        issues.append("The artwork is entirely transparent.")
    rule = RULES[role]
    if rule.alpha == "transparent" and not info["clear_edge"]:
        issues.append("Supply artwork with a transparent background reaching the outer edge of the canvas.")
    if rule.alpha == "opaque" and info["transparent"]:
        issues.append("Supply an approved composition with a fully opaque background.")
    if frames > 1 and ("GIF" not in rule.formats or info["format"] != "GIF"):
        issues.append("This role does not accept this animation format.")
    if role == "sticker":
        if album_type == "static" and frames != 1:
            issues.append("Static albums require single-frame stickers.")
        if album_type == "animated":
            if info["format"] != "GIF" or info["distinct_frames"] < 2:
                issues.append("Animated stickers require a GIF with at least two visually distinct frames.")
            if frames > 1 and min(info["durations_ms"]) <= 0:
                issues.append("Give every motion frame a positive display duration.")
    return issues


def _validation(info: dict[str, Any], role: str, album_type: str) -> list[str]:
    if "error" in info:
        return [info["error"]]
    rule = RULES[role]
    issues = _content_issues(info, role, album_type)
    if (info["width"], info["height"]) != rule.size:
        issues.append(f"Expected {rule.size[0]}×{rule.size[1]} px, got {info['width']}×{info['height']}.")
    if info["bytes"] > rule.max_bytes:
        issues.append(f"File has {info['bytes']} bytes. Limit is {rule.max_bytes} bytes.")
    if info["format"] not in rule.formats:
        issues.append(f"Accepted formats for {role} are {', '.join(rule.formats)}.")
    if role == "sticker" and album_type == "animated" and info["loop"] != 0:
        issues.append("Animated stickers must loop continuously (GIF loop=0).")
    if info["orientation"] != 1:
        issues.append("Bake the EXIF orientation into the image before upload.")
    return issues


def assess_source(path: Path, role: str, album_type: str) -> dict[str, Any]:
    """Distinguish a derivable master from artwork that needs replacement."""
    info = inspect_image(path)
    issues = _validation(info, role, album_type)
    action = "REUSE"
    if issues:
        action = "BLOCK" if "error" in info or _content_issues(info, role, album_type) else "DERIVE"
    return {"action": action, "file": None, "info": info, "issues": issues}


def validate_image(path: Path, role: str, album_type: str) -> list[str]:
    """Validate the exact input file without converting it."""
    return _validation(inspect_image(path), role, album_type)


def _fit(frame: Image.Image, size: tuple[int, int], clear: bool) -> Image.Image:
    fitted = ImageOps.contain(frame, size, Image.Resampling.LANCZOS)
    if fitted.size == size:
        return fitted
    background = (0, 0, 0, 0)
    if not clear:
        # Sample the dominant edge colour so fitted opaque artwork keeps its ground.
        samples = []
        for edge in _edges(frame):
            small = edge.resize((16, 1) if edge.height == 1 else (1, 16), Image.Resampling.NEAREST)
            samples.extend(small.getpixel((x, y)) for x in range(small.width) for y in range(small.height))
        background = Counter(samples).most_common(1)[0][0]
    canvas = Image.new("RGBA", size, background)
    canvas.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
    return canvas


def _encode(frame: Image.Image, fmt: str, **options: Any) -> bytes:
    # Do not propagate a master's EXIF orientation, thumbnails or comments.
    frame.info.clear()
    output = BytesIO()
    frame.save(output, fmt, **options)
    return output.getvalue()


def _encode_static(frame: Image.Image, rule: ImageRule, clear: bool) -> tuple[bytes, str]:
    pixels = frame if clear else frame.convert("RGB")
    data = _encode(pixels, "PNG", optimize=True)
    if len(data) <= rule.max_bytes:
        return data, "PNG"
    if not clear and "JPEG" in rule.formats:
        for quality in (95, 88, 80, 70, 58):
            data = _encode(pixels, "JPEG", quality=quality, optimize=True)
            if len(data) <= rule.max_bytes:
                return data, "JPEG"
    for colors in (256, 128, 64):
        data = _encode(pixels.quantize(colors=colors), "PNG", optimize=True)
        if len(data) <= rule.max_bytes:
            return data, "PNG"
    raise ValueError("Could not reach the byte limit. Supply simpler or pre-optimized artwork.")


def _palette_frame(frame: Image.Image, colors: int, clear: bool) -> Image.Image:
    indexed = frame.convert("RGB").quantize(colors=colors)
    if clear:
        # Index 255 is reserved in every local palette for the transparent matte.
        indexed.paste(255, mask=frame.getchannel("A").point(lambda alpha: 255 if alpha < 128 else 0))
        indexed.info["transparency"] = 255
    return indexed


def _encode_gif(
    frames: list[Image.Image], info: dict[str, Any], rule: ImageRule, loop: int | None
) -> bytes:
    clear = info["transparent"]
    options = {"loop": loop} if loop is not None else {}
    if clear:
        options.update(transparency=255, background=255)
    for colors in (255, 128, 64, 32):
        indexed = [_palette_frame(frame, colors, clear) for frame in frames]
        data = _encode(
            indexed[0], "GIF", save_all=True, append_images=indexed[1:],
            duration=info["durations_ms"], disposal=2, optimize=False, **options,
        )
        if len(data) <= rule.max_bytes:
            return data
    raise ValueError("GIF exceeds the byte limit after palette optimization. Supply a simpler animation.")


def _derive(source: Path, info: dict[str, Any], role: str, album_type: str) -> tuple[bytes, str]:
    rule = RULES[role]
    with Image.open(source, formats=INPUT_FORMATS) as image:
        if info["frames"] == 1:
            frame = ImageOps.exif_transpose(image).convert("RGBA")
            frame = _fit(frame, rule.size, info["transparent"])
            return _encode_static(frame, rule, info["transparent"])
        frames = []
        for index in range(info["frames"]):
            image.seek(index)
            frame = image.convert("RGBA")
            frames.append(_fit(frame, rule.size, info["transparent"]))
    loop = 0 if role == "sticker" and album_type == "animated" else info["loop"]
    return _encode_gif(frames, info, rule, loop), "GIF"


def process_image(source: Path, dest_dir: Path, stem: str, role: str, album_type: str) -> dict[str, Any]:
    """Copy compliant sources byte-for-byte, otherwise derive and revalidate an export."""
    if not stem or stem in (".", "..") or Path(stem).name != stem or "\\" in stem:
        raise ValueError("Export stem must be a single filename without directory components.")
    info = inspect_image(source)
    issues = _validation(info, role, album_type)
    blocked = {"action": "BLOCK", "file": None, "issues": issues, "info": info}
    if "error" in info or _content_issues(info, role, album_type):
        return blocked
    action = "DERIVE" if issues else "REUSE"
    try:
        data, fmt = _derive(source, info, role, album_type) if issues else (None, info["format"])
    except (OSError, ValueError) as exc:
        blocked["issues"] = [*issues, str(exc)]
        return blocked
    dest_dir.mkdir(parents=True, exist_ok=True)
    destination = dest_dir / (stem + EXTENSIONS[fmt])
    with destination.open("xb") as output:
        try:
            if data is None:
                with source.open("rb") as original:
                    shutil.copyfileobj(original, output)
            else:
                output.write(data)
        except OSError:
            destination.unlink()
            raise

    exported = inspect_image(destination)
    issues = _validation(exported, role, album_type)
    if info["frames"] > 1 and exported.get("duration_ms") != info["duration_ms"]:
        issues.append("Derived GIF changed the cycle duration. Supply a pre-optimized version.")
    if issues:
        destination.unlink()
        return {"action": "BLOCK", "file": None, "issues": issues, "info": exported}
    return {"action": action, "file": destination.name, "issues": [], "info": exported}


def preview(paths: list[Path], target: Path) -> None:
    """Write a manifest-order contact sheet with three sampled poses for animations."""
    cell_width, cell_height = 212, 138
    columns = min(4, max(1, len(paths)))
    rows = max(1, (len(paths) + columns - 1) // columns)
    sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), "#f4f4f2")
    draw = ImageDraw.Draw(sheet)
    if not paths:
        draw.text((10, 10), "No available artwork", fill="#242524")
    for number, path in enumerate(paths):
        left = (number % columns) * cell_width
        top = (number // columns) * cell_height
        with Image.open(path, formats=INPUT_FORMATS) as image:
            count = getattr(image, "n_frames", 1)
            indices = list(dict.fromkeys([0, count // 2, count - 1])) if count > 1 else [0]
            width = (cell_width - 12) // len(indices)
            for slot, index in enumerate(indices):
                image.seek(index)
                rgba = image.convert("RGBA")
                rgba.thumbnail((width - 6, 104), Image.Resampling.LANCZOS)
                x = left + 6 + slot * width
                draw.rectangle((x, top + 5, x + width - 2, top + 112), fill="#e1e4e5")
                sheet.paste(rgba, (x + (width - rgba.width) // 2, top + 6 + (104 - rgba.height) // 2), rgba)
            label = path.stem + (f"    {count} frames" if count > 1 else "")
            draw.text((left + 8, top + 117), label, fill="#242524")
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target, "PNG", optimize=True)
