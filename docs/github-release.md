# WeChat Sticker Publisher v0.1.0

The first release packages static and animated WeChat sticker albums from local files. The CLI and Codex skill share the same validation and export code. Each build writes upload files, Chinese submission copy, previews, a checklist and an album ZIP. If an image is missing, the report describes what to supply and the other exports remain available.

The GitHub release includes a Python wheel, a source distribution with the Chestnut Walk example and SHA-256 checksums. The offline format checks use the WeChat guide reviewed on 19 November 2026. Creators check account eligibility, ownership and name availability in the portal and review their artwork before uploading.

## Roadmap

1. Collect creator feedback on installation, GIF playback and validation messages.
2. Track changes in WeChat's guide and update the local rules and tests together.
3. Extend artwork provider support and localized reports as creators contribute examples.

[Sample and drawing source](../examples/sample-album/) · [Specification reference](../.agents/skills/wechat-sticker-publisher/references/wechat-specifications.md) · [Public-release audit](public-release-audit.md)
