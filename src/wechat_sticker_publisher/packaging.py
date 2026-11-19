"""Prepare a complete snapshot in staging before making a new release visible."""
from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from .artwork import load_provider
from .imaging import preview
from .metadata import Album, project_path, safe_label, write_json
from .workflow import compare_albums, evaluate


def markdown_report(report: dict) -> str:
    lines = [f"# {report['name']} · {report['status']}", "",
             f"Baseline `{report['baseline']}` · {report['scope']} · "
             f"{report['stickers']} listed stickers · {report['supplementary_available']}/5 supplementary images",
             "", f"Creator status · {report['creator_status']}", "", "## Findings", ""]
    lines.extend(f"- {issue}" for issue in report["issues"])
    if not report["issues"]:
        lines.append("All automated checks passed for the selected inputs.")
    lines.extend(["", "## Files", "", "| Role | ID | Action | Pixels | Bytes | Frames | Loop |",
                  "| --- | --- | --- | --- | ---: | ---: | --- |"])
    for row in report["assets"]:
        i = row["info"]
        size = f"{i['width']}×{i['height']}" if "width" in i else "—"
        lines.append(f"| {row['role']} | {row['id']} | {row['action']} | {size} | "
                     f"{i.get('bytes', '—')} | {i.get('frames', '—')} | {i.get('loop') if i.get('loop') is not None else '—'} |")
    return "\n".join(lines) + "\n"


def finish_album(root: Path, album: Album, report: dict) -> None:
    dest = root / album.folder
    assets = report["assets"]
    metadata = {k: getattr(album, k) for k in ("id", "name", "type", "characters", "description", "appreciation", "status")}
    metadata.update(technical_status=report["status"], specification=report["baseline"],
                    stickers=[{"id": r["id"], "path": r["file"]} for r in assets if r["role"] == "sticker"],
                    supplementary={r["role"]: r["file"] for r in assets if r["role"] != "sticker"})
    write_json(dest / "metadata.json", metadata)
    write_json(dest / "validation-report.json", report)
    write_json(dest / "artwork-briefs.json", report["briefs"])
    (dest / "validation-report.md").write_text(markdown_report(report), encoding="utf-8")
    copy = (f"# 表情名称\n\n{album.name}\n\n## 表情介绍\n\n{album.description}\n\n"
            f"## 赞赏引导语\n\n{album.appreciation}\n")
    (dest / "上架文案.md").write_text(copy, encoding="utf-8")
    findings = "\n".join(f"- [ ] {s}" for s in report["issues"])
    checklist = (f"# {album.name} · 提交前核对\n\nLocal technical status · {report['status']}\n\n"
                 f"创作者记录　{album.status}\n\n{findings}\n\n"
                 "- [ ] 在官方后台核名，确认账号可开通赞赏。\n"
                 "- [ ] 确认作品权属、署名（最多 10 字）、每张的中文释义（最多 4 字）与排列顺序。\n"
                 "- [ ] 在聊天大小、明暗背景下查看轮廓、文字与动作差异。动态 GIF 需实际检查循环衔接。\n"
                 "- [ ] 查看横幅留白与背景，核实封面、图标的透明边缘、无字、无白边与专辑辨识度。\n"
                 "- [ ] 核对两张赞赏图与引导语，逐字校对所有配字。\n"
                 "- [ ] 对照当期平台规范与后台反馈，选择通过检查的文件手动上传。\n")
    (dest / "submission-checklist.md").write_text(checklist, encoding="utf-8")
    for group in ("stickers", "supplementary"):
        paths = [dest / a["file"] for a in assets if a["file"] and a["file"].startswith(group + "/")]
        preview(paths, root / "previews" / f"{album.id}-{group}.png")
    suffix = "-INCOMPLETE" if report["issues"] else ""
    with zipfile.ZipFile(root / f"{album.folder}{suffix}.zip", "x") as archive:
        for path in sorted(dest.rglob("*")):
            if path.is_file():
                entry = zipfile.ZipInfo(path.relative_to(dest).as_posix(), (1980, 1, 1, 0, 0, 0))
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, path.read_bytes())


def commit_release(staging: Path, directory: Path, label: str) -> Path:
    sequence = 0
    while True:
        sequence += 1
        name = label if sequence == 1 else f"{label}-{sequence:02d}"
        destination = directory / name
        if destination.exists() or destination.is_symlink():
            continue
        reservation = directory / f".reserve-{name}"
        try:
            reservation.mkdir()
        except FileExistsError:
            continue
        try:
            if destination.exists() or destination.is_symlink():
                continue
            staging.rename(destination)
            return destination
        finally:
            reservation.rmdir()


def build(root: Path, albums: list[Album], label: str, generate: bool, provider_name: str | None) -> tuple[Path, list[dict]]:
    safe_label(label)
    directory = project_path(root, "releases/wechat")
    directory.mkdir(parents=True, exist_ok=True)
    needs_art = any(item.role != "sticker" and not item.path.is_file() for album in albums for item in album.items)
    provider, problem = load_provider(provider_name) if generate and needs_art else (None, "")
    with tempfile.TemporaryDirectory(prefix=".build-", dir=directory) as tmp:
        staging = Path(tmp) / "release"
        staging.mkdir()
        reports = []
        for album in albums:
            dest = staging / album.folder
            for group in ("stickers", "supplementary"):
                (dest / group).mkdir(parents=True, exist_ok=True)
            reports.append(evaluate(root, album, dest, generate=generate, provider=provider, provider_problem=problem))
        compare_albums(reports)
        for album, report in zip(albums, reports):
            finish_album(staging, album, report)
        summary = ["# WeChat publishing packages", "", f"Release `{label}`", "",
                   "| Album | Local checks | Listed stickers | Supplementary | Creator status |", "| --- | --- | ---: | ---: | --- |"]
        for r in reports:
            summary.append(f"| {r['name']} ({r['album']}) | {r['status']} | {r['stickers']} | {r['supplementary_available']}/5 | {r['creator_status']} |")
        summary += ["", "Each album includes upload files, Chinese copy, the validation report and a manual submission checklist.",
                    "Previews use manifest order. The account holder verifies name availability, rights and eligibility in the platform."]
        (staging / "release-summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
        return commit_release(staging, directory, label), reports
