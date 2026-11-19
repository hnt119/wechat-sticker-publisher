# Creator guide

[Project home](../README.md) · [简体中文](creator-guide.zh-CN.md)

## Installation on Windows or an offline computer

Use Python 3.10 or later. From the repository directory in PowerShell, run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .
```

For an air-gapped machine, run `python -m pip wheel . --wheel-dir wheelhouse` on a connected machine with the same Python version, operating system and architecture. Copy the wheelhouse to the offline machine and run `python -m pip install --no-index --find-links wheelhouse wechat-sticker-publisher` in its virtual environment.

## Prepare your own album

1. In your working folder, run `wechat-sticker init`. It creates `publishing-config/album.json` and two artwork folders. To start a named motion album, run `wechat-sticker init --pack waves --type animated`.
2. Open the JSON file in a text editor and fill in your title, introduction, appreciation line and character identifiers. Keep the quotation marks. The field guide below explains what goes in each entry.
3. Copy one image per reaction into `artwork/album/stickers/`. Zero-pad filenames such as `01-wave.png`, `02-cheer.png` and `10-goodnight.png` for a predictable display order. Keep alternate captions, working files and high-resolution variants outside this discovery folder.
4. Put the five supporting images in `artwork/album/supplementary/`. Name each file with the stem in the image table below, for example `banner.jpg` and `icon.png`.
5. Run the following commands from the same folder. For a named album substitute its ID for `album` in the paths above.

```sh
wechat-sticker inventory
wechat-sticker validate
wechat-sticker build --offline
```

Use `validate` to inspect the sources as supplied. A large approved master can fail a size check and still produce a valid export. Run `build` for the verdict on the actual upload files. You can build with missing art. Open the report and artwork briefs, supply the requested images and build again.

## Album manifest

Keep one JSON or YAML manifest per album under `publishing-config/`. Paths are relative to the creator project root, which contains that folder.

| Field | What to enter |
| --- | --- |
| `id`, `type` | A stable album identifier such as `waves` and either `static` or `animated`. |
| `name` | 表情名称. Up to eight characters. Five or fewer are preferred. Omit spaces and punctuation. Check availability in the platform dashboard. |
| `description` | 表情介绍. Up to 80 characters. Describe a personality, moment or running joke. |
| `appreciation` | 赞赏引导语. A short message of 5–15 characters. |
| `characters`, `status` | A list of character identifiers and the creator's editorial status. The build reports technical readiness separately. |
| `sticker_directory` or `stickers` | Discover images from a folder, or remove `sticker_directory` and list ordered entries such as `{"id": "wave", "path": "drawings/wave.png"}` under `stickers`. |
| `supplementary` | Role-to-path mapping for supporting artwork; use this to point to existing approved masters. The starter also supports discovering files by role in its supplementary folder. |
| `references` | Optional list of approved character-art paths for an explicitly requested artwork workflow. |

Use the generated file as your editable template. The example project shows a filled manifest. `上架文案.md` in the export contains copy-ready Chinese fields.

## Supported images

The versioned rules packaged with the toolkit apply offline. Each album contains 8–24 different stickers, all static or all animated. Keep one rendition of each design. This workflow checks all five supporting images, including the two illustrations for appreciation.

| Image or filename stem | Export size | Format | Target |
| --- | --- | --- | --- |
| Sticker | 240 × 240 | PNG, JPEG or single-frame GIF for static albums; animated GIF for motion albums | ≤500 KB |
| `banner` | 750 × 400 | JPEG or PNG | ≤500 KB, opaque |
| `cover` | 240 × 240 | PNG | ≤500 KB, transparent surround |
| `icon` | 50 × 50 | PNG | ≤100 KB, transparent surround |
| `appreciation-guide` | 750 × 560 | PNG or GIF | ≤500 KB, opaque |
| `appreciation-thanks` | 750 × 750 | PNG or GIF | ≤500 KB, opaque |

Here 1 KB is 1,000 bytes. JPEG appreciation masters can be supplied for conversion to the published formats. The toolkit decodes the files to check format, dimensions, byte size and transparency. Motion checks include frame count, visible changes, timings and continuous looping. Valid files can be reused byte for byte. The exporter can resize and optimize supported masters while preserving proportions and retaining original files. Review animated results at normal speed and check the tiny icon against light and dark backgrounds. Check that cover and icon are free of lettering, borders and white outlines, and that the banner tells a clear story without text. Confirm legibility, character consistency, rights and suitability yourself. [Local baseline, sources and verification date](../.agents/skills/wechat-sticker-publisher/references/wechat-specifications.md)

## Command guide

Use `--project DIR` to work in another creator folder. Album commands process all manifests by default. Use `--pack ID` for one album or `--all` for the whole project. Run any command with `--help` for its options.

| Command | Result |
| --- | --- |
| `wechat-sticker init [--pack ID] [--type static\|animated]` | Create an editable starter manifest and artwork folders. |
| `wechat-sticker inventory --all` | List discovered and declared resources. Use `inventory --scan DIR` to scan a project-relative folder independently of the manifests. |
| `wechat-sticker validate --pack ID` | Inspect the source manifest, sticker count, duplicates and actual image files. |
| `wechat-sticker assets missing --all` | List required artwork still to supply. |
| `wechat-sticker assets briefs --pack ID` | Get production instructions for missing artwork. |
| `wechat-sticker report --all` | Read a project assessment without creating a new release. |
| `wechat-sticker build --all --offline` | Export available artwork, technical results, copy, checklists, previews and album ZIPs. |
| `wechat-sticker build --pack ID --release review-1` | Build with a human-readable release label. The default is the local date. |
| `wechat-sticker build --pack ID --generate-missing --provider NAME` | Request missing supporting images from an installed provider. |

Inspection commands support `--json` for scripts. A successful assessment exits with code 0, an incomplete one with 1, and invalid usage or configuration with 2. A reported incomplete build still saves the usable files.

## Review a release

Under `releases/wechat/<release>/`, open `release-summary.md`, the previews and each album's `validation-report.md`. One album directory contains `stickers/`, `supplementary/`, `metadata.json`, `上架文案.md` and `submission-checklist.md`. A ZIP accompanies each directory. An incomplete archive has an `-INCOMPLETE.zip` suffix and its `artwork-briefs.json` lists work to finish. Rebuilding a label such as `review-1` creates `review-1-02`, then `review-1-03`. Archive entries use stable ordering and timestamps for reproducibility with the same inputs, settings and software versions.

`TECHNICAL_PASS` means the exported images and manifest passed the local baseline. `INCOMPLETE` lists the remaining issues. The WeChat dashboard is where you check title availability, account eligibility, copyright attribution, a short meaning keyword for each sticker, the current submission instructions and the platform's final decision. Upload the individual files after reviewing them.

## Agent-assisted packaging and optional generation

Install the CLI and activate its Python environment. In your creator project run `wechat-sticker skill list`, then `wechat-sticker skill install --agent codex --scope project`, substituting your agent ID. For a personal installation use `--scope user`. Open the album folder in a new session and ask “Package my stickers for WeChat publishing.” Review the same release summary, ZIP and briefs described above. [Installation and troubleshooting](agent-installation.md) · [Compatibility matrix](agent-compatibility.md) · [DeepSeek Harness walkthrough](deepseek-harness.md)

For the optional OpenAI Images adapter, install the extra from the toolkit checkout with `python -m pip install '.[openai]'`. Set `OPENAI_API_KEY` and `WECHAT_STICKER_IMAGE_MODEL` in your local environment, then run `wechat-sticker build --pack ID --generate-missing --provider openai-images`. This opt-in command can send approved references to the service and incur charges. Other installed providers can be selected with `--provider NAME` or `WECHAT_STICKER_PROVIDER` plus `--generate-missing`. Without a configured provider, the build records the missing resources, keeps the offline exports and supplies manual briefs. [Provider setup and adapter interface](artwork-providers.md)

## Troubleshooting

- **Command missing.** Activate the environment used at installation. `python -m pip show wechat-sticker-publisher` displays its install location.
- **Album or image missing.** Point `--project` at the directory containing `publishing-config/`. Check filename case, role stems and artwork paths relative to the project root.
- **A cover fails transparency.** Export a clean PNG cutout with visible artwork and transparent surrounding pixels. An opaque white canvas and a painted checkerboard both count as opaque.
- **A motion album is short.** Count distinct reactions. Export another completed action before marking the album ready. Review visual similarity manually, including alternate captions that change pixels without changing the action.
- **A large GIF still fails.** Reduce visual noise, frame count or palette complexity in the animation master while retaining readable movement and pacing. Rebuild and review the actual GIF.
