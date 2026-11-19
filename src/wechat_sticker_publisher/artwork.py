"""Offline production briefs and opt-in, locally installed artwork adapters."""
from __future__ import annotations

from importlib.metadata import entry_points
from pathlib import Path
from typing import Any, Protocol

from .imaging import RULES
from .metadata import Album, Item


class ProviderSetupError(ValueError):
    """An actionable configuration message safe to display to the creator."""


class ArtworkProvider(Protocol):
    def generate(self, brief: dict[str, Any], references: list[Path], destination: Path) -> None:
        """Write the requested original supplementary image to destination (PNG)."""


def load_provider(name: str | None) -> tuple[ArtworkProvider | None, str]:
    if not name:
        return None, "No artwork provider selected. Supply the files manually or configure --provider NAME."
    try:
        matches = list(entry_points(group="wechat_sticker_publisher.artwork", name=name))
        if len(matches) == 1:
            return matches[0].load()(), ""
        return None, f"Expected one installed artwork provider named {name!r}; found {len(matches)}."
    except ProviderSetupError as exc:
        return None, str(exc)
    except Exception as exc:
        return None, f"Artwork provider {name!r} could not start ({type(exc).__name__})."


DIRECTION = {
    "banner": "Draw a lively scene relevant to the album on an opaque non-white ground. Omit text.",
    "cover": "Compose a distinctive half- or full-body character on transparency, without lettering or white outline.",
    "icon": "Use a simple recognizable face on transparency. Inspect at 50 px. Omit lettering, frame and white outline.",
    "appreciation-guide": "Show a playful invitation to support the creator on a colored ground. Proofread any caption.",
    "appreciation-thanks": "Show the character acknowledging support on a colored ground. Proofread any caption.",
    "sticker": "Supply a distinct expressive pose consistent with the album. Check lettering at chat size.",
}


def artwork_brief(root: Path, album: Album, item: Item) -> dict:
    rule = RULES[item.role]
    formats = ["GIF"] if item.role == "sticker" and album.type == "animated" else sorted(rule.formats)
    return {
        "album": album.id, "album_name": album.name, "album_type": album.type, "characters": album.characters,
        "description": album.description, "role": item.role, "id": item.id,
        "size_px": list(rule.size), "formats": formats, "max_bytes": rule.max_bytes,
        "background": rule.alpha, "direction": DIRECTION[item.role],
        "references": [p.relative_to(root).as_posix() for p in album.references],
        "supply_at": item.path.relative_to(root).as_posix(),
        "instructions": "Place an approved image at supply_at or update its manifest path, then run build again.",
    }
