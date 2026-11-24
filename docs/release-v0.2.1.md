# WeChat Sticker Publisher v0.2.1 — Distribution & Developer Experience

Version 0.2.1 makes the offline publishing workflow easier to install and diagnose. Install its wheel with uv or pipx to get the `wechat-sticker` command without cloning the project. The release workflow supplies the matching wheel, source archive and checksums for each verified commit.

- The English and Chinese quick starts cover your first album, the complete Chestnut Walk example and where to find its ZIP, reports and previews.
- The Vercel skills CLI can discover the canonical skill by GitHub repository and install it by tag or commit. The skill checks for the separate Python CLI and offers an installation route when it is missing. The bundled seven-agent installer still works offline.
- `wechat-sticker skill doctor` identifies the active interpreter, CLI, Pillow and PyYAML versions. The CLI explains how to repair missing dependencies. Installer diagnostics explain how to preserve customized or independently managed copies.
- Both Python distributions include package-index metadata, the canonical instructions, three skill references and the MIT license. The CI review workflow builds twice from the proposed commit and verifies the collected distributions. Production publication uses a separate protected job and PyPI Trusted Publishing.
- The v0.2.0 publishing commands, album format, optional artwork providers and deterministic output are preserved. Codex and OpenCode have completed end-to-end album packaging. Other runtime results remain individually documented. [Compatibility matrix](agent-compatibility.md)

## Verify the distribution

Use the wheel, source archive and `SHA256SUMS` from the same CI run. After verifying their hashes, install the wheel from its local path with `uv tool install ./wechat_sticker_publisher-0.2.1-py3-none-any.whl` or `pipx install ./wechat_sticker_publisher-0.2.1-py3-none-any.whl`. Run `wechat-sticker --version` and `wechat-sticker skill doctor`. From the source archive’s `examples/sample-album/` directory, run `wechat-sticker validate` and `wechat-sticker build --offline --release review`.

With Python 3.12, Pillow 12.3.0 and PyYAML 6.0.3, the expected eight-sticker, five-supplementary album ZIP has SHA-256 `a05bcbe9d32860c168e7ce7ad990eb075874b9f4874e0c4913955f388e59b36e`. The release directory contains the ZIP, its unpacked files, two preview contact sheets and a release summary.

## Publication and discovery

As of 24 November 2026, the official PyPI project and Simple endpoints returned 404. A repository install with the skills CLI succeeded. The matching owner/repository/skill entry was absent from the public skills.sh directory. Recheck both services before adding badges. See the [Trusted Publishing runbook](trusted-publishing.md) for owner configuration, approval and anonymous post-publication tests.

The proposed GitHub About description is “Offline-first Python CLI and portable Agent Skill for preparing, validating, and packaging WeChat sticker albums.” Keep the current WeChat and image-processing topics and add `agent-skills`, `python-cli`, `claude-code`, `opencode` and `deepseek-harness` when updating the listing. The existing `codex-skill` topic still describes a supported adapter.

After an approved publication, verify bare-name uv and pipx installs from production PyPI before promoting them in both READMEs and the skill reference. Check the new tag with the external installer and refresh the sample source link against the published assets. [Installation guide](agent-installation.md) · [Changelog](../CHANGELOG.md)
