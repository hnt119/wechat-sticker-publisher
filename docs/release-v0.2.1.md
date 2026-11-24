# WeChat Sticker Publisher v0.2.1 — Distribution & Developer Experience

Released 24 November 2026. Install the offline CLI from PyPI with `uv tool install wechat-sticker-publisher` or `pipx install wechat-sticker-publisher`. Run `wechat-sticker --version` to see the installed version. [PyPI project](https://pypi.org/project/wechat-sticker-publisher/0.2.1/) · [GitHub Release](https://github.com/hnt119/wechat-sticker-publisher/releases/tag/v0.2.1)

## What changed

- The English and Chinese quick starts cover the first album, the complete Chestnut Walk example, and where to find its ZIP, reports and previews.
- The external skills CLI installs the canonical skill from the GitHub tag. The skill asks before installing a missing Python CLI. The seven bundled adapters still install offline. [Agent installation](agent-installation.md)
- `wechat-sticker skill doctor` reports the active interpreter, CLI, Pillow and PyYAML versions. Diagnostics explain how to repair missing dependencies and preserve customized skills.
- The v0.2.0 album format, publishing commands, optional artwork providers and deterministic output are preserved. Codex and OpenCode have packaged the sample end to end. [Evidence for each host](agent-compatibility.md)

## Downloads and provenance

Download the wheel or source archive together with the checksum file. On macOS, run `shasum -a 256 -c SHA256SUMS` in a directory with all three files. On Linux, use `sha256sum -c SHA256SUMS`. On Windows, use `Get-FileHash -Algorithm SHA256` on each distribution and compare the results below. [SHA256SUMS](https://github.com/hnt119/wechat-sticker-publisher/releases/download/v0.2.1/SHA256SUMS)

| Download | SHA-256 | PyPI provenance |
| --- | --- | --- |
| [Python wheel](https://github.com/hnt119/wechat-sticker-publisher/releases/download/v0.2.1/wechat_sticker_publisher-0.2.1-py3-none-any.whl) | `1c808c86a5b812c430a53cac9f4e586e838974d64778dd8ded922f68167c40b0` | [Wheel attestation](https://pypi.org/integrity/wechat-sticker-publisher/0.2.1/wechat_sticker_publisher-0.2.1-py3-none-any.whl/provenance) |
| [Source archive with sample](https://github.com/hnt119/wechat-sticker-publisher/releases/download/v0.2.1/wechat_sticker_publisher-0.2.1.tar.gz) | `b9e3f94973765b278df488eb37b477f4fc33728d0eb9dc28654a24181cc71212` | [Source attestation](https://pypi.org/integrity/wechat-sticker-publisher/0.2.1/wechat_sticker_publisher-0.2.1.tar.gz/provenance) |

The protected release workflow built the distributions twice from `eb523e7f5e2dc1b28f08b454be92830be9fe9403`. Public downloads from GitHub and PyPI matched the verified workflow artifact byte-for-byte. Both Sigstore attestations passed verification against this repository. They identify `release.yml`, the release commit and workflow run 45384240002. PyPI records the publisher environment as `pypi`. [Production workflow](https://github.com/hnt119/wechat-sticker-publisher/actions/runs/45384240002) · [CI on the release tag](https://github.com/hnt119/wechat-sticker-publisher/actions/runs/45384214832)

## Public installation checks

On 24 November 2026, uv 0.13.9 and pipx 1.19.1 each installed version 0.2.1 from production PyPI in separate, empty environments. Both passed dependency checks. From the extracted source archive’s `examples/sample-album/` directory, each installation ran:

```sh
wechat-sticker validate
wechat-sticker build --offline --release review
```

Both reported eight stickers and five supplementary images. Each generated album ZIP had SHA-256 `a05bcbe9d32860c168e7ce7ad990eb075874b9f4874e0c4913955f388e59b36e`, matching v0.2.0.

The external `skills@1.9.0` installer discovered `hnt119/wechat-sticker-publisher@v0.2.1` and installed the tagged `SKILL.md` and all three references byte-for-byte. The skills.sh directory and search did not list this repository on the verification date. Use the GitHub tag for external installation. [Commands and scopes](agent-installation.md)
