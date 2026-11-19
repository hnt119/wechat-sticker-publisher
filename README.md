# WeChat Sticker Publisher

[简体中文](README.zh-CN.md) · [v0.1.1 release](https://github.com/hnt119/wechat-sticker-publisher/releases/tag/v0.1.1)

Turn illustrations or animated GIFs into a WeChat sticker album ready for manual review and upload. The CLI exports correctly sized artwork, Chinese submission copy, previews and one ZIP per album. **After installation, packaging works offline. No API key, subscription or cloud account is required.**

<img src="examples/sample-album/preview.png" width="560" alt="Eight illustrations from the Chestnut Walk sample album, including a wave, a sprint and a nap">

## Try the sample

With Git and Python 3.10+ installed, run the following in a macOS or Linux terminal. The sample contains eight static stickers and all five supplementary images. [Windows and offline installation](docs/creator-guide.md)

```sh
git clone https://github.com/hnt119/wechat-sticker-publisher.git
cd wechat-sticker-publisher
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .

wechat-sticker --project examples/sample-album build --offline --release first-look
```

Open `examples/sample-album/releases/wechat/first-look/release-summary.md`. The sample should show **TECHNICAL_PASS**. The same directory contains the album ZIP, unpacked upload files, previews and submission checklist. [Sample drawings and source](examples/sample-album/)

## Package your own stickers

1. Run `wechat-sticker init` in your creator folder. Fill in the title, introduction and appreciation message in `publishing-config/album.json`, and add your character identifiers.
2. Place 8–24 different reactions in `artwork/album/stickers/`. Choose a static or animated album. Put the banner, cover, chat icon and two appreciation illustrations in `artwork/album/supplementary/`.
3. Run `wechat-sticker validate` to check the sources, then `wechat-sticker build` to export. A build with missing artwork saves a partial package and a production brief for each missing image. Rebuild after supplying it.

The creator guide covers image filenames, GIF timing and loops, metadata, ordering, CLI options and troubleshooting. Check name availability and account eligibility in the WeChat creator portal before manual upload. [Creator guide](docs/creator-guide.md) · [Dated WeChat specifications](.agents/skills/wechat-sticker-publisher/references/wechat-specifications.md)

## Use with Codex

With the CLI installed, copy `.agents/skills/wechat-sticker-publisher/` into `~/.agents/skills/`. In a new session in your creator project, ask **“Package my stickers for WeChat.”** The skill runs the same CLI. You can also explicitly request missing artwork through a configured image provider. [Agent skill](.agents/skills/wechat-sticker-publisher/SKILL.md) · [Optional artwork providers](docs/artwork-providers.md)

## License and project

MIT covers the toolkit and its synthetic demo assets, including the preview and icon. Creators retain ownership of their artwork and generated packages, subject to third-party rights. Private character artwork and unpublished albums remain under their creators’ own rights. This is an independent project with no official affiliation with WeChat or Tencent. [License](LICENSE) · [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Public-release audit](docs/public-release-audit.md)
