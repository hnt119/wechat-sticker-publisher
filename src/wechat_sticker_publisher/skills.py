"""Install the packaged Agent Skill using the harnesses' filesystem conventions."""
from __future__ import annotations

import hashlib
import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
import shutil
import stat
import tempfile

import yaml

from .metadata import ConfigError

NAME = "wechat-sticker-publisher"
RECEIPT = ".wechat-sticker-install.json"
FILES = ("SKILL.md", "references/agent-compatibility.md", "references/publishing-workflow.md",
         "references/wechat-specifications.md")
BUNDLE_ENTRIES = frozenset((*FILES, "references", RECEIPT))
# Project native directory, user native directory, executable names.
AGENTS = {
    "codex": (".agents", ".agents", ("codex",)),
    "claude-code": (".claude", ".claude", ("claude",)),
    "gemini-cli": (".gemini", ".gemini", ("gemini",)),
    "cursor": (".cursor", ".cursor", ("cursor-agent", "agent", "cursor")),
    "opencode": (".opencode", ".config/opencode", ("opencode",)),
    "github-copilot": (".github", ".copilot", ("copilot",)),
    "deepseek-harness": (".dsh", ".dsh", ("dsh",)),
}
ALIASES = {"dsh": "deepseek-harness"}


def skill_files() -> dict[str, bytes]:
    source = resources.files("wechat_sticker_publisher").joinpath("skill_data")
    if not source.is_dir():
        module = Path(__file__).resolve()
        checkout = module.parents[2]
        if module.parents[1].name != "src" or not (checkout / "pyproject.toml").is_file():
            raise ConfigError("Missing packaged skill. Reinstall wechat-sticker-publisher.")
        source = checkout / ".agents" / "skills" / NAME
    try:
        return {name: source.joinpath(*name.split("/")).read_bytes() for name in FILES}
    except FileNotFoundError as exc:
        raise ConfigError("Incomplete skill resources. Reinstall wechat-sticker-publisher.") from exc


def _linked(path: Path) -> bool:
    if os.name != "nt":
        return path.is_symlink()
    # Junctions and other Windows reparse points can redirect writes too.
    try:
        return bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except FileNotFoundError:
        return False


@dataclass(frozen=True)
class Root:
    scope: str
    layout: str
    path: Path
    anchor: Path

    def check(self) -> None:
        # Traversing a link during a write could change files outside the requested scope.
        current = self.anchor
        for part in self.path.relative_to(current).parts:
            current = current / part
            if _linked(current) or (current.exists() and not current.is_dir()):
                raise ConfigError(f"Expected a real directory: {current}")


def roots(agent: str, scope: str, project: Path) -> list[Root]:
    project_dir, user_dir, _ = AGENTS[agent]
    home = Path.home().resolve()
    base = project if scope == "project" else home
    if scope == "project" and agent == "deepseek-harness":
        base = next((p for p in (project, *project.parents) if (p / ".git").exists()), project)
    native = base / (project_dir if scope == "project" else user_dir)
    shared = base / ".agents"
    if scope == "user":
        override = {"claude-code": "CLAUDE_CONFIG_DIR", "deepseek-harness": "DSH_HOME",
                    "opencode": "XDG_CONFIG_HOME"}.get(agent)

        def configured(variable: str, default: Path) -> Path:
            value = os.environ.get(variable, "")
            if not value.strip():
                return default
            if agent == "deepseek-harness":
                if value == "~":
                    return home
                if value.startswith(("~/", "~\\")):
                    value = str(home / value[2:])
            else:
                value = os.path.expanduser(value)
            return Path(os.path.abspath(value))

        if override:
            if agent == "opencode":
                native = configured(override, home / ".config") / "opencode"
            else:
                native = configured(override, native)
        if agent == "deepseek-harness":
            shared = configured("DSH_AGENTS_HOME", shared)

    def root(layout: str, directory: Path) -> Root:
        if not directory.is_absolute() or ".." in directory.parts:
            raise ConfigError(f"Use an absolute configuration directory: {directory}")
        anchor = base if directory.is_relative_to(base) else directory.parent
        return Root(scope, layout, directory / "skills", anchor)

    result = [root("native", native)]
    if agent in ("claude-code", "codex"):
        return result
    shared_root = root("shared", shared)
    if agent == "gemini-cli":  # .agents wins within the same scope.
        result.insert(0, shared_root)
    else:
        result.append(shared_root)
    if agent in ("opencode", "cursor") or (agent == "github-copilot" and scope == "project"):
        result.append(root("claude", base / ".claude"))
    if agent == "cursor":
        result.append(root("codex", base / ".codex"))
    return result


def _frontmatter(path: Path) -> dict:
    # Only read an entry's metadata. A linked skill can shadow the requested name,
    # even though the installer never writes through it.
    if not path.is_file():
        return {}
    with path.open("rb") as stream:
        if stream.readline(6).rstrip(b"\r\n") != b"---":
            return {}
        limit = 1024 * 1024
        header = bytearray()
        while len(header) < limit:
            line = stream.readline(limit - len(header))
            if line.rstrip(b"\r\n") == b"---":
                break
            if not line:
                return {}
            header.extend(line)
        else:
            raise ConfigError(f"Cannot safely inspect the large YAML header in {path}")
    try:
        data = yaml.safe_load(bytes(header))
    except (yaml.YAMLError, RecursionError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _candidates(agent: str, root: Root) -> list[Path]:
    root.check()
    if not root.path.is_dir():
        return []
    candidates = []
    for item in sorted(root.path.iterdir()):
        if item.name == NAME:
            candidates.append(item)  # Also reserve invalid, unrelated or dangling destinations.
            continue
        if agent == "deepseek-harness" and root.scope == "user" and root.layout == "native" and item.name == ".system":
            continue
        if item.is_dir():
            entry = item / "SKILL.md"
        elif agent in ("deepseek-harness", "opencode") and item.suffix == ".md":
            if item.stem == NAME:
                candidates.append(item)
                continue
            entry = item
        else:
            continue
        if _frontmatter(entry).get("name") == NAME:
            candidates.append(item)
    return candidates


def _digests(files: dict[str, bytes]) -> dict[str, str]:
    return {name: hashlib.sha256(contents).hexdigest() for name, contents in files.items()}


def _matches(path: Path, digest: dict[str, str]) -> bool:
    if _linked(path) or not path.is_dir():
        return False
    for name in FILES:
        item = path / name
        if _linked(item.parent) or _linked(item) or not item.is_file():
            return False
        # Avoid loading an arbitrarily large modified file into memory.
        with item.open("rb") as stream:
            value = hashlib.sha256()
            for block in iter(lambda: stream.read(65536), b""):
                value.update(block)
        if value.hexdigest() != digest.get(name):
            return False
    return True


def _bundle_entries(path: Path) -> set[str]:
    # Check the two expected levels without descending into extra directories.
    entries = {item.name for item in path.iterdir()}
    entries.update("references/" + item.name for item in (path / "references").iterdir())
    return entries


def _owned(path: Path, agent: str, scope: str) -> None:
    receipt = path / RECEIPT
    if _linked(path) or _linked(receipt) or not receipt.is_file():
        raise ConfigError(f"Leaving unmanaged skill in place: {path}")
    try:
        with receipt.open("rb") as stream:
            record = json.loads(stream.read(8193)) if receipt.stat().st_size <= 8192 else None
    except (ValueError, RecursionError):
        record = None
    if not isinstance(record, dict) or (record.get("installer"), record.get("agent"), record.get("scope")) != (
        NAME + "/1", agent, scope
    ):
        raise ConfigError(f"Leaving skill in place; no matching installation receipt: {path}")
    digest = record.get("files")
    if not isinstance(digest, dict) or set(digest) != set(FILES) or not _matches(path, digest):
        raise ConfigError(f"Leaving modified skill in place: {path}")
    if _bundle_entries(path) != BUNDLE_ENTRIES:
        raise ConfigError(f"Leaving skill with additional files or directories in place: {path}")


@contextmanager
def _lock(directory: Path):
    # The OS releases either kind of lock if this process exits unexpectedly.
    if os.name == "nt":
        try:
            fd = os.open(directory / f".{NAME}.lock", os.O_CREAT | os.O_EXCL | os.O_TEMPORARY | os.O_RDWR)
        except FileExistsError as exc:
            raise ConfigError(f"Concurrent skill operation in {directory}; retry.") from exc
    else:
        import fcntl
        fd = os.open(directory, os.O_RDONLY)
    try:
        if os.name != "nt":
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ConfigError(f"Concurrent skill operation in {directory}; retry.") from exc
        yield
    finally:
        os.close(fd)


def _install(path: Path, files: dict[str, bytes], agent: str, scope: str) -> None:
    # Only expose a complete bundle. Staged SKILL.md is below the direct discovery depth.
    with tempfile.TemporaryDirectory(dir=path.parent, prefix=".wechat-sticker-") as stage:
        bundle = Path(stage) / "bundle"
        for name, data in files.items():
            item = bundle / name
            item.parent.mkdir(parents=True, exist_ok=True)
            item.write_bytes(data)
        record = {"installer": NAME + "/1", "agent": agent, "scope": scope, "files": _digests(files)}
        (bundle / RECEIPT).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        if os.path.lexists(path):
            raise ConfigError(f"Destination already exists: {path}")
        bundle.rename(path)


def _uninstall(path: Path, agent: str, scope: str) -> None:
    _owned(path, agent, scope)
    # Move out of discovery before removing anything. Recheck the moved directory.
    stage = Path(tempfile.mkdtemp(dir=path.parent, prefix=".wechat-sticker-"))
    bundle = stage / "bundle"
    try:
        path.rename(bundle)
        try:
            _owned(bundle, agent, scope)
        except (ConfigError, OSError):
            if os.path.lexists(path):
                raise ConfigError(f"Changed files preserved for recovery at {bundle}")
            bundle.rename(path)
            raise
        shutil.rmtree(bundle)
    finally:
        if not os.path.lexists(bundle):
            stage.rmdir()


def _target(agent: str, scope: str, project: Path, layout: str, files: dict[str, bytes],
            uninstall: bool) -> tuple[Root, str]:
    locations = roots(agent, scope, project)
    if layout == "shared" and agent == "codex":
        layout = "native"  # Codex uses .agents natively.
    possible = [r for r in locations if r.layout == layout or layout == "auto"]
    if not possible:
        raise ConfigError(f"{agent} has no {layout} installation layout in {scope} scope.")
    default = next((r for r in possible if r.layout == "native"), possible[0])
    found = {path: r for r in reversed(locations) for path in _candidates(agent, r)}
    if not found:
        return default, "absent" if uninstall else "install"
    if len(found) > 1:
        raise ConfigError("Multiple same-name skill candidates; inspect with skill doctor: " +
                          ", ".join(map(str, found)))
    path, location = next(iter(found.items()))
    if location.path not in {r.path for r in possible} or path.name != NAME:
        raise ConfigError(f"Existing skill name or layout collision: {path}")
    if uninstall:
        _owned(path, agent, scope)
        return location, "uninstall"
    if not _matches(path, _digests(files)) or _bundle_entries(path) - BUNDLE_ENTRIES:
        raise ConfigError(f"Existing skill differs from the packaged skill: {path}")
    return location, "reuse"


def change(agent: str, scope: str, project: Path, layout: str, dry_run: bool, uninstall: bool) -> dict:
    if scope == "project" and not project.is_dir():
        raise ConfigError(f"Choose an existing project directory: {project}")
    files = skill_files()
    root, action = _target(agent, scope, project, layout, files, uninstall)
    path = root.path / NAME
    if not dry_run and action in ("install", "uninstall"):
        # All layouts in this scope share a lock, including DSH's native and shared roots.
        lock_dir = root.anchor if scope == "project" else Path.home()
        with _lock(lock_dir):
            # A concurrent installer may have completed between inspection and locking.
            latest, action = _target(agent, scope, project, layout, files, uninstall)
            if latest != root:
                raise ConfigError("Skill locations changed during installation; retry.")
            if action == "install":
                root.check()
                root.path.mkdir(parents=True, exist_ok=True)
                _install(path, files, agent, scope)
            elif action == "uninstall":
                _uninstall(path, agent, scope)
    return {"agent": agent, "scope": scope, "action": action, "path": str(path), "dry_run": dry_run}


def inspect(agent: str, project: Path, doctor: bool) -> dict:
    result = {"agent": agent}
    locations = [root for scope in ("project", "user") for root in roots(agent, scope, project)]
    result["locations"] = [{"scope": r.scope, "layout": r.layout, "path": str(r.path)} for r in locations]
    if doctor:
        result["runtime"] = next((path for exe in AGENTS[agent][2] if (path := shutil.which(exe))), None)
        distinct = {root.path: root for root in reversed(locations)}
        by_root = [_candidates(agent, root) for root in locations if distinct[root.path] == root]
        result["candidates"] = [str(path) for paths in by_root for path in paths]
        if agent == "deepseek-harness":
            # Equal-rank ties or invalid manifests need resolution by the real harness.
            winner = None
            for paths in by_root:
                if paths:
                    if len(paths) == 1:
                        path = paths[0]
                        entry = path / "SKILL.md" if path.is_dir() else path
                        metadata = _frontmatter(entry)
                        if metadata.get("name") == NAME and isinstance(metadata.get("description"), str):
                            winner = str(path)
                    break
            result["first_standard_candidate"] = winner
            result["scope_note"] = (
                "Project native, project shared, custom, user native, user shared, bundled. "
                "Custom, bundled and runtime providers require the DSH catalog."
            )
    return result
