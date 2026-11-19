"""Explicitly selected OpenAI Images adapter; the SDK is an optional extra."""

from __future__ import annotations

import base64
import os
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

from .artwork import ProviderSetupError


def _reference(path: Path, index: int) -> tuple[str, bytes, str]:
    """Upload displayed artwork under an anonymous filename without embedded metadata."""
    with Image.open(path, formats=("PNG", "JPEG")) as image:
        if getattr(image, "n_frames", 1) != 1:
            raise ValueError("Supply single-frame PNG or JPEG character references.")
        pixels = ImageOps.exif_transpose(image).convert("RGBA")
        pixels.info.clear()
        buffer = BytesIO()
        pixels.save(buffer, format="PNG")
    if buffer.tell() >= 50_000_000:
        raise ValueError("Reduce the reference dimensions to keep each PNG upload below 50 MB.")
    return (f"reference-{index}.png", buffer.getvalue(), "image/png")


class OpenAIImages:
    """Generate one supplementary composition per explicit provider invocation."""

    def __init__(self) -> None:
        self.model = os.getenv("WECHAT_STICKER_IMAGE_MODEL", "").strip()
        key = os.getenv("OPENAI_API_KEY", "").strip()
        if not self.model or not key:
            raise ProviderSetupError("Configure OPENAI_API_KEY and WECHAT_STICKER_IMAGE_MODEL for openai-images.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderSetupError("Install the openai extra with pip install '.[openai]' from the toolkit checkout.") from exc
        self.client = OpenAI(api_key=key, base_url="https://api.openai.com/v1", max_retries=0)

    def generate(self, brief: dict[str, Any], references: list[Path], destination: Path) -> None:
        width, height = brief["size_px"]
        size = "1024x1024"
        if width > height:
            size = "1536x1024"
        elif height > width:
            size = "1024x1536"
        prompt = (
            f"Create one {brief['role']} illustration for a sticker album. "
            f"Album title: {brief['album_name']}. Album story: {brief['description']}. "
            f"Characters: {', '.join(brief['characters'])}. "
            f"Art direction: {brief['direction']} "
            f"Compose for final dimensions {width} by {height} pixels. "
            "Keep important artwork inside the frame. Preserve the design of any supplied characters."
        )
        params = dict(model=self.model, prompt=prompt, size=size, n=1,
                      output_format="png", background=brief["background"])
        if references:
            if len(references) > 16:
                raise ValueError("Select up to 16 approved references for this image request.")
            images = [_reference(path, index) for index, path in enumerate(references, 1)]
            reply = self.client.images.edit(image=images, **params)
        else:
            reply = self.client.images.generate(**params)
        if not reply.data or not reply.data[0].b64_json:
            raise ValueError("Image provider returned no base64 image.")
        data = base64.b64decode(reply.data[0].b64_json, validate=True)
        with Image.open(BytesIO(data), formats=("PNG",)) as image:
            image.verify()
        with destination.open("xb") as output:
            output.write(data)
