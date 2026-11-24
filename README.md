# WeChat Sticker Publisher

[![PyPI](https://img.shields.io/pypi/v/wechat-sticker-publisher)](https://pypi.org/project/wechat-sticker-publisher/) [![GitHub Release](https://img.shields.io/github/v/release/hnt119/wechat-sticker-publisher?label=GitHub%20Release)](https://github.com/hnt119/wechat-sticker-publisher/releases/latest) · [简体中文](https://github.com/hnt119/wechat-sticker-publisher/blob/main/README.zh-CN.md)

An offline-first CLI and portable Agent Skill for preparing, validating, and packaging WeChat sticker albums. Turn illustrations or animated GIFs into upload files, Chinese submission copy, previews and an album ZIP for manual review.

![Eight stickers from Chestnut Walk, including a wave, a sprint and a nap](https://raw.githubusercontent.com/hnt119/wechat-sticker-publisher/main/examples/sample-album/preview.png)

## Install the CLI

Use Python 3.10+ and uv to install from PyPI. You can package an album without a Git checkout or an AI account. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

```sh
uv tool install wechat-sticker-publisher
wechat-sticker --version
```

For pipx, run `pipx install wechat-sticker-publisher` (pipx itself requires Python 3.11+). If your shell cannot find the command, run `uv tool update-shell` or `pipx ensurepath` and reopen the terminal. Packaging works offline after installation. [Install pipx](https://pipx.pypa.io/stable/how-to/install-pipx.html) · [Windows and offline setup](https://github.com/hnt119/wechat-sticker-publisher/blob/main/docs/creator-guide.md) · [Manual downloads and checksums](https://github.com/hnt119/wechat-sticker-publisher/blob/main/docs/release-v0.2.1.md)

## Package your stickers

1. Open a new album folder and run `wechat-sticker init`. Edit the title, introduction, appreciation message and character identifiers in `publishing-config/album.json`.
2. Put 8–24 distinct stickers in `artwork/album/stickers/`. Use one type per album, static or animated. Put the banner, cover, chat icon and two appreciation illustrations in `artwork/album/supplementary/`.
3. Check the inputs and build the upload files.

```sh
wechat-sticker validate
wechat-sticker build --offline --release first-look
```

Read `releases/wechat/first-look/release-summary.md`. Its directory contains the album ZIP, previews and unpacked album with the validation report and submission checklist. If an image is missing, the build saves a partial package and a brief describing what to supply. [Creator guide and expected filenames](https://github.com/hnt119/wechat-sticker-publisher/blob/main/docs/creator-guide.md)

## Use with an agent

Install the CLI above so your agent can run `wechat-sticker`. From the album folder, choose **one** way to install the skill instructions.

| Installer | Command |
| --- | --- |
| Bundled with the Python CLI, works offline | `wechat-sticker skill install --agent codex --scope project` |
| Vercel skills CLI, downloads from GitHub | `npx skills@1.9.0 add hnt119/wechat-sticker-publisher@v0.2.1 --skill wechat-sticker-publisher --agent claude-code` |

The external skill installer installs instructions and references. The Python CLI provides the publishing engine. Open the album folder in your agent and ask **“Package my stickers for WeChat publishing.”**

The native installer supports Codex, Claude Code, Gemini CLI, Cursor, OpenCode, GitHub Copilot CLI and DeepSeek Harness. Codex and OpenCode have packaged the sample end to end. [Installation, scopes and upgrades](https://github.com/hnt119/wechat-sticker-publisher/blob/main/docs/agent-installation.md) · [Evidence for each host](https://github.com/hnt119/wechat-sticker-publisher/blob/main/docs/agent-compatibility.md)

## Try the complete example

Extract the v0.2.1 source archive and run the two quick-start commands above in its `examples/sample-album` folder. Chestnut Walk should report **TECHNICAL_PASS** for eight stickers and all five supplementary images. [Download the sample archive](https://github.com/hnt119/wechat-sticker-publisher/releases/download/v0.2.1/wechat_sticker_publisher-0.2.1.tar.gz)

## Privacy and license

MIT covers the toolkit and its original synthetic demo assets. Creators retain ownership of their artwork and packages, subject to third-party rights. Private character designs and unpublished albums stay with their creators. An optional image provider can process approved references when you explicitly request generation. Review and upload finished albums manually. This independent project has no official affiliation with WeChat or Tencent. [License](https://github.com/hnt119/wechat-sticker-publisher/blob/main/LICENSE) · [Public-release audit](https://github.com/hnt119/wechat-sticker-publisher/blob/main/docs/public-release-audit.md)
