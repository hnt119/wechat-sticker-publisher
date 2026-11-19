"""Use one validation pipeline for source reports, prepared files and agents."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

from .artwork import ArtworkProvider, artwork_brief
from .imaging import assess_source, process_image
from .metadata import Album, Item

BASELINE = "wechat-album-2026-11-19"


def _prepare(album: Album, item: Item, source: Path, target: Path, index: int) -> dict:
    group = "stickers" if item.role == "sticker" else "supplementary"
    dest = target / group
    dest.mkdir(parents=True, exist_ok=True)
    stem = f"{index:02d}" if item.role == "sticker" else item.role
    result = process_image(source, dest, stem, item.role, album.type)
    if result["file"]:
        result["file"] = group + "/" + result["file"]
    return result


def evaluate(root: Path, album: Album, target: Path | None = None, *,
             generate: bool = False, provider: ArtworkProvider | None = None,
             provider_problem: str = "") -> dict:
    results = []
    issues = album.issues()
    briefs = []
    seen: dict[str, str] = {}
    with TemporaryDirectory(prefix="sticker-art-") as temp:
        for i, item in enumerate(album.items, 1):
            source = item.path
            brief = artwork_brief(root, album, item)
            generated = False
            notes = []
            if not source.is_file() and generate and item.role != "sticker":
                if provider is None:
                    notes.append(provider_problem)
                elif any(not ref.is_file() for ref in album.references):
                    notes.append("An approved reference is missing. Correct references before generation.")
                else:
                    destination = Path(temp) / f"{item.role}.png"
                    try:
                        provider.generate(brief, list(album.references), destination)
                        if destination.is_file() and not destination.is_symlink():
                            source = destination
                            generated = True
                        else:
                            notes.append("Provider returned without a usable image.")
                    except Exception as exc:
                        notes.append(f"Provider failed ({type(exc).__name__}). Supply the image manually.")
            if not source.is_file():
                result = dict(action="REQUEST", file=None, info={}, issues=["Missing file. See artwork brief."])
            elif target is None:
                result = assess_source(item.path, item.role, album.type)
            else:
                result = _prepare(album, item, source, target, i)
                if generated and result["file"]:
                    result["action"] = "GENERATE"
            result.update(id=item.id, role=item.role, source=brief["supply_at"])
            result["issues"].extend(notes)
            if result["action"] in ("REQUEST", "BLOCK"):
                briefs.append(brief)
            fingerprint = result["info"].get("visual_hash")
            if item.role == "sticker" and fingerprint:
                if fingerprint in seen:
                    result["issues"].append(f"Duplicate rendered sticker, matches {seen[fingerprint]}.")
                seen[fingerprint] = item.id
            issues.extend(f"{item.role} {item.id}: {error}" for error in result["issues"])
            results.append(result)
    listed = sum(item.role == "sticker" for item in album.items)
    if listed < 8:
        briefs.append(dict(role="additional-stickers", album=album.id, number_needed=8 - listed,
                           album_type=album.type, size_px=[240, 240], instructions=
                           "Add distinct finished designs to your ordered manifest or sticker_directory and rebuild."))
    return dict(album=album.id, name=album.name, creator_status=album.status, baseline=BASELINE,
                scope="exports" if target else "sources", status="INCOMPLETE" if issues else "TECHNICAL_PASS",
                stickers=listed, supplementary_available=sum(r["role"] != "sticker" and not r["issues"] for r in results),
                actions=dict(Counter(r["action"] for r in results)), issues=issues, assets=results, briefs=briefs)


def compare_albums(reports: list[dict]) -> None:
    """Cross-check the names, covers and icons in this invocation."""
    seen: dict[tuple[str, str], dict] = {}
    for report in reports:
        keys = [("album name", report["name"])]
        keys.extend((asset["role"], asset["info"].get("visual_hash", "")) for asset in report["assets"]
                    if asset["role"] in ("cover", "icon"))
        for kind, value in keys:
            if not value:
                continue
            key = kind, value.casefold()
            if key in seen:
                other = seen[key]
                for first, second in ((report, other), (other, report)):
                    first["issues"].append(f"Duplicate {kind} across selected albums: {second['album']}.")
                    first["status"] = "INCOMPLETE"
            else:
                seen[key] = report
