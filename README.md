# WeChat Sticker Publisher

[简体中文](https://github.com/hnt119/wechat-sticker-publisher/blob/main/README.zh-CN.md) · [Latest stable release](https://github.com/hnt119/wechat-sticker-publisher/releases/latest)

An offline-first CLI and portable Agent Skill for preparing, validating, and packaging WeChat sticker albums. Turn illustrations or animated GIFs into upload files, Chinese submission copy, previews and an album ZIP for manual review.

![Eight stickers from Chestnut Walk, including a wave, a sprint and a nap](https://raw.githubusercontent.com/hnt119/wechat-sticker-publisher/v0.2.0/examples/sample-album/preview.png)

## Install the CLI

With Python 3.10+ and uv, install the published GitHub wheel. uv manages the tool environment. No checkout or AI account is required. [Install uv](https://docs.astral.sh/uv/getting-started/installation/) · [Install pipx](https://pipx.pypa.io/stable/installation/)

```sh
uv tool install https://github.com/hnt119/wechat-sticker-publisher/releases/download/v0.2.0/wechat_sticker_publisher-0.2.0-py3-none-any.whl
wechat-sticker --version
```

Prefer pipx? Replace `uv tool install` with `pipx install` and use the same wheel URL. If your shell cannot find `wechat-sticker`, run `uv tool update-shell` or `pipx ensurepath` and reopen the terminal. After installation the CLI works offline. [Offline and Windows setup](https://github.com/hnt119/wechat-sticker-publisher/blob/main/docs/creator-guide.md) · [Development installation](https://github.com/hnt119/wechat-sticker-publisher/blob/main/CONTRIBUTING.md)

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
| Vercel skills CLI, downloads from GitHub | `npx skills@1.9.0 add hnt119/wechat-sticker-publisher --skill wechat-sticker-publisher --agent claude-code` |

The external skill installer installs instructions and references. The Python CLI provides the publishing engine. Open the album folder in your agent and ask **“Package my stickers for WeChat publishing.”**

The native installer supports Codex, Claude Code, Gemini CLI, Cursor, OpenCode, GitHub Copilot CLI and DeepSeek Harness. Codex and OpenCode have packaged the sample end to end. [Installation, scopes and upgrades](https://github.com/hnt119/wechat-sticker-publisher/blob/main/docs/agent-installation.md) · [Evidence for each host](https://github.com/hnt119/wechat-sticker-publisher/blob/main/docs/agent-compatibility.md)

## Try the complete example

Download and extract the [stable source distribution](https://github.com/hnt119/wechat-sticker-publisher/releases/download/v0.2.0/wechat_sticker_publisher-0.2.0.tar.gz). In its `examples/sample-album` folder, run the two quick-start commands above. Chestnut Walk should report **TECHNICAL_PASS** for eight stickers and all five supplementary images.

## Privacy and license

MIT covers the toolkit and its original synthetic demo assets. Creators retain ownership of their artwork and packages, subject to third-party rights. Private character designs and unpublished albums stay with their creators. An optional image provider can process approved references when you explicitly request generation. Review and upload finished albums manually. This independent project has no official affiliation with WeChat or Tencent. [License](https://github.com/hnt119/wechat-sticker-publisher/blob/main/LICENSE) · [Public-release audit](https://github.com/hnt119/wechat-sticker-publisher/blob/main/docs/public-release-audit.md)
