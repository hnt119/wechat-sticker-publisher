"""Read local album definitions and resolve approved inputs inside the project."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROLES = ("banner", "cover", "icon", "appreciation-guide", "appreciation-thanks")
EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}


class ConfigError(ValueError):
    """A manifest or user-supplied path cannot be used safely."""


def safe_label(value: str) -> str:
    if (not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", value)
            or re.fullmatch(r"CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9]", value, re.I)):
        raise ConfigError("Choose a 1–64 character album ID or release label using letters, digits, - and _.")
    return value


def project_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value.strip() or Path(value).is_absolute():
        raise ConfigError("Use a non-empty project-relative path for each file or directory.")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ConfigError(f"Path leaves the project: {value!r}")
    return path


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class Item:
    id: str
    role: str
    path: Path


@dataclass
class Album:
    id: str
    name: str
    description: str
    appreciation: str
    type: str
    characters: list[str]
    status: str
    items: list[Item]
    references: list[Path]

    @property
    def folder(self) -> str:
        return f"{self.id}-{self.name}" if 1 <= len(self.name) <= 8 and self.name.isalnum() else f"{self.id}-_draft"

    def issues(self) -> list[str]:
        errors = []
        if not (1 <= len(self.name) <= 8 and self.name.isalnum()):
            errors.append("Provide a 1–8 character album name using letters or digits without spaces or punctuation.")
        if not (1 <= len(self.description) <= 80 and self.description.strip()):
            errors.append("Provide an album description of 1–80 characters, including punctuation.")
        if not (5 <= len(self.appreciation) <= 15 and self.appreciation.strip()):
            errors.append("Provide an appreciation message of 5–15 characters.")
        if not self.characters or any(not c.strip() for c in self.characters):
            errors.append("Provide at least one non-empty character identifier.")
        if not self.status.strip():
            errors.append("Provide a creator release status.")
        stickers = [item.id for item in self.items if item.role == "sticker"]
        if not 8 <= len(stickers) <= 24:
            errors.append(f"Album lists {len(stickers)} stickers; supply 8–24 distinct designs.")
        if any(not s.strip() for s in stickers):
            errors.append("Sticker IDs must be non-empty.")
        if len(set(stickers)) != len(stickers):
            errors.append("Duplicate sticker IDs. Give each design its own ID.")
        return errors


def _strings(data: dict, key: str) -> list[str]:
    values = data.get(key, [])
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise ConfigError(f"{key} must be a list of strings.")
    return values


def read_manifest(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as stream:
            data = json.load(stream) if path.suffix == ".json" else yaml.safe_load(stream)
        if not isinstance(data, dict):
            raise ConfigError("Expected a mapping at the top level.")
        return data
    except (ValueError, OSError, yaml.YAMLError) as exc:
        raise ConfigError(f"{path.name}: {exc}") from exc


def load_album(root: Path, path: Path, data: dict | None = None) -> Album:
    try:
        if data is None:
            data = read_manifest(path)
        album_id = safe_label(data.get("id", ""))
        album_type = data.get("type")
        if album_type not in ("static", "animated"):
            raise ConfigError("type must be static or animated.")
        fields = {k: data.get(k, "") for k in ("name", "description", "appreciation", "status")}
        if not all(isinstance(v, str) for v in fields.values()):
            raise ConfigError("Copy fields and status must be text.")
        rows = data.get("stickers", [])
        if not isinstance(rows, list):
            raise ConfigError("stickers must be an ordered list.")
        if "sticker_directory" in data:
            if rows:
                raise ConfigError("Choose either the ordered stickers list or sticker_directory.")
            directory = project_path(root, data["sticker_directory"])
            if directory.exists() and not directory.is_dir():
                raise ConfigError(f"Expected a sticker directory: {data['sticker_directory']}")
            rows = [{"id": p.stem, "path": str(p.relative_to(root))} for p in sorted(directory.glob("*"))
                    if p.is_file() and p.suffix.lower() in EXTENSIONS and not p.name.startswith(".")]
        items = []
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                raise ConfigError("Each sticker needs a text id and a relative path.")
            items.append(Item(row["id"], "sticker", project_path(root, row.get("path", ""))))
        mappings = data.get("supplementary", {})
        if not isinstance(mappings, dict) or set(mappings) - set(ROLES):
            raise ConfigError("Use only the five documented supplementary role names.")
        directory = project_path(root, data.get("supplementary_directory", f"artwork/{album_id}/supplementary"))
        for role in ROLES:
            if role in mappings:
                source = project_path(root, mappings[role])
            else:
                matches = sorted(p for p in directory.glob(f"{role}.*") if p.suffix.lower() in EXTENSIONS)
                if len(matches) > 1:
                    raise ConfigError(f"Multiple sources for {role}; select one in supplementary.")
                source = project_path(root, str((matches[0] if matches else directory / f"{role}.png").relative_to(root)))
            items.append(Item(role, role, source))
        return Album(album_id, **fields, type=album_type, characters=_strings(data, "characters"),
                     items=items, references=[project_path(root, p) for p in _strings(data, "references")])
    except (ValueError, OSError, yaml.YAMLError, RuntimeError) as exc:
        raise ConfigError(f"{path.name}: {exc}") from exc


def albums(root: Path, selected: str | None) -> list[Album]:
    directory = project_path(root, "publishing-config")
    files = sorted(p for p in directory.glob("*") if p.suffix in (".json", ".yaml", ".yml"))
    loaded = []
    for p in files:
        try:
            data = read_manifest(project_path(root, str(p.relative_to(root))))
        except ConfigError:
            if selected and p.stem != selected:
                continue
            raise
        if selected is None or data.get("id") == selected:
            loaded.append(load_album(root, p, data))
    if selected and not loaded:
        raise ConfigError(f"No album has ID {selected!r}. Run inventory --all.")
    if not loaded:
        raise ConfigError("No albums found. Run wechat-sticker init in your project.")
    ids = [album.id.casefold() for album in loaded]
    if len(set(ids)) != len(ids):
        raise ConfigError("Album IDs must be unique, ignoring case.")
    return loaded


def initialize(root: Path, album_id: str, album_type: str) -> Path:
    safe_label(album_id)
    config = project_path(root, f"publishing-config/{album_id}.json")
    base = f"artwork/{album_id}"
    folders = [project_path(root, f"{base}/{name}") for name in ("stickers", "supplementary")]
    config.parent.mkdir(parents=True, exist_ok=True)
    for path in folders:
        path.mkdir(parents=True, exist_ok=True)
    template = dict(id=album_id, type=album_type, name="", description="", appreciation="",
                    characters=[], status="draft", sticker_directory=f"{base}/stickers",
                    supplementary_directory=f"{base}/supplementary")
    try:
        with config.open("x", encoding="utf-8") as stream:
            json.dump(template, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    except FileExistsError as exc:
        raise ConfigError(f"Manifest already exists: {config.name}. Edit it or choose a new --pack ID.") from exc
    return config
