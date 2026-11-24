# Changelog

## 0.2.1 · Distribution & Developer Experience (release candidate)

- Document no-clone CLI installation from a published GitHub wheel using uv or pipx, and repository-based skill installation with the Vercel skills CLI.
- Guide skill-first users through locating or installing the separate Python runtime with their permission. Add runtime details to `skill doctor` and actionable errors for missing dependencies.
- Add Python package index metadata and a protected, manually approved Trusted Publishing workflow. Registry publication requires account setup and a separate release decision.
- Preserve the v0.2.0 album configuration, publishing commands, offline outputs and seven native installation adapters.

## 0.2.0 · Universal Agent Skills Support · 2026-11-19

- Bundle one MIT-licensed Agent Skill with the offline CLI in the wheel and source archive.
- Add project and user installation, inspection and safe removal for Codex, Claude Code, Gemini CLI, Cursor, OpenCode, GitHub Copilot CLI and DeepSeek Harness (`dsh`).
- Document native and shared skill locations, duplicate handling and real-host test results. See the [compatibility matrix](docs/agent-compatibility.md) and [candidate release notes](docs/release-v0.2.0.md).
- Existing album manifests, image processing, optional providers and publishing commands retain their v0.1.1 behavior.

## 0.1.1 · 2026-11-19

- CI maintenance release. Pin checkout v7.0.1 and setup-python v7.1.0 to their Node.js 24 release commits. Checkout discards its Git credentials before the package steps.
- The Python 3.10, 3.12 and 3.13 jobs continue to run the test suite, build distributions and package the offline sample. The CLI and Codex skill retain their v0.1.0 publishing behavior.

## 0.1.0 · 2026-11-19

- Inventory, validate and package static or motion albums with the offline `wechat-sticker` command and the matching agent skill.
- Read ordered JSON/YAML manifests or discover artwork in dedicated directories.
- Preserve valid upload files, derive size-constrained exports and inspect rendered frames, transparency, GIF timing, looping and duplicates.
- Prepare five supplementary roles, Chinese submission copy, previews, machine-readable findings, human checklists and one repeatable ZIP per album.
- Build partial releases with actionable artwork briefs. Support explicitly configured provider adapters for missing supplementary art.
- Include the original, reproducible Chestnut Walk example, bilingual documentation and automated workflow tests.
