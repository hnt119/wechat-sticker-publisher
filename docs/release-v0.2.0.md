# WeChat Sticker Publisher v0.2.0 — Universal Agent Skills Support

This release candidate adds portable installation of the publishing workflow. A creator can install the Python CLI, select an agent, open the album workspace and ask it to package the stickers. The CLI still performs inventory, validation, image processing and deterministic export offline.

- One standard MIT-licensed skill with three references ships in the wheel and source distribution.
- Seven adapters support project or personal installation. Preview paths with `--dry-run`, inspect known copies with `skill doctor` and remove unchanged installer-managed copies with `skill uninstall`.
- DeepSeek Harness has native and shared installation paths, a `dsh` alias and a developer-preview walkthrough. Runtime versions, discovery evidence and limits for each host are recorded in the compatibility matrix.
- Existing creator configurations and Codex projects can keep using the same publishing commands. Existing hand-installed skills are treated as user-owned files. Compare their content and back up any local edits when updating.
- The CLI requires Python 3.10+ and the existing imaging and YAML dependencies. Model access and image generation remain optional. MIT covers the toolkit and its original synthetic demo. Creators retain their rights in other artwork and packages, subject to third-party rights.

[Installation guide](agent-installation.md) · [Compatibility and execution evidence](agent-compatibility.md) · [DeepSeek Harness](deepseek-harness.md) · [Changelog](../CHANGELOG.md)

## Review this candidate

In a clean checkout, fetch and switch to `feat/universal-agent-skills-v0.2`. Create a Python virtual environment, activate it and run the following at the repository root. The package version is `0.2.0`; use the pull request commit to identify the exact candidate.

```sh
python -m pip install '.[test]'
python -m pytest
python -m build
wechat-sticker --project examples/sample-album validate
wechat-sticker --project examples/sample-album build --offline --release review
```

Open the per-album validation report and compare the output with the hashes in the compatibility matrix. Byte comparisons require matching inputs, configuration and dependency versions.
