"""Command-line entry point. All processing is local unless a provider is opted into."""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import date
from pathlib import Path

from . import __version__


def _location(p: argparse.ArgumentParser) -> None:
    p.add_argument("--project", default=argparse.SUPPRESS, type=Path, metavar="DIR", help="Creator project (default: current directory).")


def _select(p: argparse.ArgumentParser) -> None:
    _location(p)
    group = p.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="Process all albums (default).")
    group.add_argument("--pack", metavar="ID", help="Select one manifest by album ID.")
    p.add_argument("--json", action="store_true", help="Print machine-readable results.")


def parser() -> argparse.ArgumentParser:
    from . import skills

    p = argparse.ArgumentParser(prog="wechat-sticker", description="Inventory, validate and package sticker albums locally.")
    _location(p)
    p.add_argument("--version", action="version", version=__version__)
    commands = p.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create a manifest and empty artwork directories.")
    _location(init)
    init.add_argument("--pack", default="album", metavar="ID")
    init.add_argument("--type", choices=("static", "animated"), default="static")
    for name, help_text in (("inventory", "Inspect source files and artwork properties."),
                            ("validate", "Validate the original files against the local baseline."),
                            ("report", "Print detailed source validation reports."),
                            ("build", "Prepare, revalidate and archive exports in a new release.")):
        sub = commands.add_parser(name, help=help_text)
        _select(sub)
        if name == "inventory":
            sub.add_argument("--scan", metavar="DIR", help="Inspect all PNG, JPG and GIF files under a project-relative directory.")
        if name == "build":
            mode = sub.add_mutually_exclusive_group()
            mode.add_argument("--offline", action="store_true", help="Local processing (default).")
            mode.add_argument("--generate-missing", action="store_true", help="Ask the selected provider for missing supplementary art.")
            sub.add_argument("--provider", metavar="NAME", help="Installed artwork entry point. Requires --generate-missing.")
            sub.add_argument("--release", default=date.today().isoformat(), metavar="LABEL", help="Snapshot label (default: local date).")
    assets = commands.add_parser("assets", help="Locate absent resources and produce manual artwork briefs.")
    _location(assets)
    views = assets.add_subparsers(dest="view", required=True)
    for name in ("missing", "briefs"):
        _select(views.add_parser(name))
    skill = commands.add_parser("skill", help="List, inspect or install the portable Agent Skill.")
    _location(skill)
    actions = skill.add_subparsers(dest="action", required=True)
    for action in ("list", "doctor", "install", "uninstall"):
        sub = actions.add_parser(action)
        _location(sub)
        change = action in ("install", "uninstall")
        sub.add_argument("--agent", choices=[*skills.AGENTS, *skills.ALIASES], required=change)
        sub.add_argument("--json", action="store_true", help="Print machine-readable results.")
        if change:
            sub.add_argument("--scope", choices=("user", "project"), required=True)
            sub.add_argument("--layout", choices=("auto", "native", "shared"), default="auto",
                             help="Reuse an existing compatible layout or choose a specific location.")
            sub.add_argument("--dry-run", action="store_true", help="Preview the operation without writing.")
    return p


def _emit(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        from .imaging import inspect_image
        from .metadata import EXTENSIONS, ConfigError, albums, initialize, project_path
        from .packaging import build, markdown_report
        from .workflow import compare_albums, evaluate
    except ModuleNotFoundError as exc:
        dependency = {"PIL": "Pillow", "yaml": "PyYAML"}.get(exc.name)
        if dependency is None:
            raise
        print(f"wechat-sticker: Missing {dependency} in {sys.executable}. "
              "Reinstall the toolkit with its dependencies using the tool or environment "
              "that installed it. For offline setup, use your local wheelhouse.", file=sys.stderr)
        return 2
    root = getattr(args, "project", Path.cwd()).resolve()
    try:
        if args.command == "skill":
            return _skill(args, root)
        if args.command == "init":
            path = initialize(root, args.pack, args.type)
            print(f"Edit {path}, then add your stickers and supplementary images in artwork/{args.pack}/.")
            return 0
        if args.command == "inventory" and args.scan:
            directory = project_path(root, args.scan)
            if not directory.is_dir():
                raise ConfigError("--scan needs an existing directory inside the project.")
            rows = []
            for path in sorted(directory.rglob("*")):
                if path.is_file() and path.suffix.lower() in EXTENSIONS:
                    relative = path.relative_to(root).as_posix()
                    rows.append({"path": relative, **inspect_image(project_path(root, relative))})
            if args.json:
                _emit(rows)
            else:
                _print_scan(rows)
            return int(any("error" in row for row in rows))
        selection = albums(root, args.pack)
        destination = None
        if args.command == "build":
            if args.provider and not args.generate_missing:
                raise ConfigError("--provider requires --generate-missing.")
            destination, reports = build(root, selection, args.release, args.generate_missing,
                                         args.provider or os.getenv("WECHAT_STICKER_PROVIDER"))
        else:
            reports = [evaluate(root, album) for album in selection]
            compare_albums(reports)
        if args.command == "assets":
            for r in reports:
                if args.view == "missing":
                    r["assets"] = [a for a in r["assets"] if a["action"] == "REQUEST"]
            key = "assets" if args.view == "missing" else "briefs"
            _emit({r["album"]: r[key] for r in reports})
        elif args.json:
            _emit(dict(release=str(destination) if destination else None, albums=reports))
        elif args.command in ("report", "inventory"):
            for r in reports:
                print(markdown_report(r))
                if args.command == "inventory":
                    for row in r["assets"]:
                        print(f"{row['id']}  {row['source']}")
        else:
            if destination:
                print(destination)
            for r in reports:
                print(f"{r['album']}  {r['status']}  {r['stickers']} stickers, {r['supplementary_available']}/5 supplementary")
                for issue in r["issues"]:
                    print(f"  - {issue}")
        return int(any(r["issues"] for r in reports))
    except (ConfigError, OSError) as exc:
        print(f"wechat-sticker: {exc}", file=sys.stderr)
        return 2


def _skill(args: argparse.Namespace, project: Path) -> int:
    from . import skills

    agent = skills.ALIASES.get(args.agent, args.agent)
    if args.action in ("install", "uninstall"):
        result = skills.change(agent, args.scope, project, args.layout, args.dry_run, args.action == "uninstall")
        if args.json:
            _emit(result)
        else:
            prefix = "Dry run: " if args.dry_run else ""
            print(f"{prefix}{result['action']} {result['path']}")
        return 0
    doctor = args.action == "doctor"
    rows = [skills.inspect(name, project, doctor) for name in ([agent] if agent else skills.AGENTS)]
    report = {"agents": rows}
    if doctor:
        from PIL import __version__ as pillow_version
        from yaml import __version__ as yaml_version

        report["runtime"] = {"publisher": __version__, "python": platform.python_version(),
                             "executable": sys.executable, "Pillow": pillow_version, "PyYAML": yaml_version}
        report["skill_resources"] = sorted(skills.skill_files())
    if args.json:
        _emit(report)
    else:
        if doctor:
            info = report["runtime"]
            print(f"wechat-sticker {info['publisher']} · Python {info['python']} ({info['executable']})")
            print(f"Pillow {info['Pillow']} · PyYAML {info['PyYAML']}")
        for row in rows:
            print(row["agent"])
            for location in row["locations"]:
                print(f"  {location['scope']} {location['layout']}  {location['path']}")
            if doctor:
                print(f"  executable  {row['runtime'] or 'not found on PATH'}")
                for path in row["candidates"]:
                    print(f"  filesystem candidate  {path}")
                if "scope_note" in row:
                    print(f"  first standard candidate  {row['first_standard_candidate'] or 'undetermined or absent'}")
                    print(f"  {row['scope_note']}")
    return 0


def _print_scan(rows: list[dict]) -> None:
    for r in rows:
        print(r["path"], r.get("error") or f"{r['format']}  {r['width']}×{r['height']}  {r['bytes']} B  {r['frames']} frame(s)")


if __name__ == "__main__":
    raise SystemExit(main())
