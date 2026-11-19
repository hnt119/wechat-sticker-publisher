---
name: wechat-sticker-publisher
description: Prepare, validate, optimize, and package static or animated WeChat sticker albums using an offline Python CLI.
license: MIT
---

Use this skill when the creator asks to package stickers for WeChat, check an album or prepare missing artwork briefs. Work in the creator project containing `publishing-config/`. You need permission to read the selected inputs, run shell commands and write the release in that project.

Run `wechat-sticker --help` in the project shell. If it is unavailable, locate the creator’s installed virtual environment or report the missing CLI (Python 3.10+). For project or user installation and harness discovery, consult [agent compatibility](references/agent-compatibility.md).

Select the requested album with `--pack ID`; use `--all` when preparing the collection.

- Read the album manifests and any existing selection/approval notes. Preserve the ordered selection, approved masters, captions, release status and private references. A planned pose, another caption or a recolor is insufficient evidence of a new motion.
- Run `wechat-sticker inventory --json` and `wechat-sticker validate` in the creator root. For a previously unconfigured project, inspect the actual files and use `init` to create the manifest. Use the creator’s copy when supplied. Keep unconfirmed editorial choices in the manifest status.
- For packaging, run `wechat-sticker build --offline` even if the source report flags dimensions, weight or absent files. Build validates the actual exports and produces usable partial packages. Exit 1 means inspect the release report and its briefs. Exit 2 means repair the input configuration or filesystem problem.
- For an explicit artwork request, run `wechat-sticker assets briefs`. Inspect the intended role and approved references before using a supported host image tool or a creator-configured optional provider. Confirm that the chosen tool is authorized for the references and cost. Place selected host-tool outputs inside the creator project at the specified input paths, inspect the rendered text and alpha, then rebuild. Leave briefs for missing resources when generation is unavailable. Never replace an approved asset as part of filling a missing role.
- Inspect the contact sheets, tiny icon and any exported animation at chat size. Give the creator the release directory, ZIPs, passed checks and exact remaining blockers. Distinguish technical validation from artist selection, official name availability, account eligibility and platform review. Packaging ends at the local release.

For project setup, interpreting reports and manual checks, read [publishing workflow](references/publishing-workflow.md). Consult the [dated specification baseline](references/wechat-specifications.md) for format disputes or a requested rules refresh.
