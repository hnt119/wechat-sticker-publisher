# Publishing workflow

Use `wechat-sticker --project DIR inventory --scan drawings` to survey a source library before it has a manifest. It inspects each candidate as supplied. An explicit ordered manifest is appropriate when a project includes masters, text variants and release editions of the same design. Use actual files to establish which actions exist. Inspect `wechat-sticker --help` and each subcommand’s help for available options.

| Question | Evidence |
| --- | --- |
| What does the creator intend to publish? | One YAML/JSON file per album in publishing-config, its ordered sticker list and creator status |
| Which source files need attention? | inventory, validate, assets missing and assets briefs |
| What will be uploaded? | A new build's numbered stickers and named supplementary files, plus metadata.json mapping IDs to relative export paths |
| Which checks passed? | validation-report.json and validation-report.md in that release |
| What needs a human? | submission-checklist.md, contact sheets under previews, playback of final GIFs, portal checks |

REUSE copies a valid file. DERIVE prepares and validates a new export from the approved source. GENERATE identifies a validated export made using an explicitly selected provider. REQUEST means the source is missing. BLOCK identifies unusable source content. The final technical status also accounts for the count, metadata and duplicates. Report both the album status and the creator's recorded editorial decisions.

For missing art, the structured briefs supply role, size, formats, byte limit, composition, relative destination and references. On a partial build, deliver the existing files and identify the exact missing items. A checksum or contact sheet cannot establish visual originality, editorial approval or WeChat name availability.
