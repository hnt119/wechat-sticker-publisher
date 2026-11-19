# WeChat sticker album specifications

Baseline **2026-11-19**, checked against the public WeChat Sticker Open Platform guide on that date. Its album and appreciation sections are separate. The English labels below describe the Chinese fields used by the creator portal. The locally shipped profile covers an album with appreciation enabled. Builds work offline.

## Official artifact requirements

| Role | Dimensions in pixels | Upload formats | Maximum shown in guide | Background |
| --- | --- | --- | --- | --- |
| Static sticker | 240 × 240 | PNG, JPG or single-frame GIF | 500 KB | No universal transparency requirement stated |
| Animated sticker | 240 × 240 | GIF | 500 KB | No universal transparency requirement stated |
| Detail banner | 750 × 400 | JPG or PNG | 500 KB | WeChat advises against transparency and white backgrounds |
| Cover | 240 × 240 | PNG | 500 KB | Transparent background required |
| Chat panel icon | 50 × 50 | PNG | 100 KB | Transparent background required |
| Appreciation guide | 750 × 560 | PNG or GIF | 500 KB | WeChat advises against transparency |
| Appreciation thanks | 750 × 750 | PNG or GIF | 500 KB | WeChat advises against transparency |

An album may contain any integer count from 8 through 24. All stickers share one type. Motion should loop smoothly. Stickers in the same album should look related and express different actions or meanings. Check framing, pacing, recognizability and Chinese lettering in previews and by playing the exported GIFs. The chat icon should read at its actual 50 px size. The guide discourages square borders and white outlines on the cover and icon. Use an album-specific cover and icon. Create a bright, text-free banner related to the stickers. Appreciation artwork should suit the character and remain legible against the platform background.

## Copy and online checks

| Creator field | Guide |
| --- | --- |
| 表情名称 | Up to 8 Chinese characters. Five or fewer are recommended for display. Avoid punctuation, spaces and duplicate album names. |
| 表情介绍 | Up to 80 Chinese characters. Describe the character or story. |
| 赞赏引导语 | 5–15 Chinese characters. Relate the invitation to the character. |
| 版权信息 | Up to 10 Chinese characters. Supply copyright details or the artist/studio name as applicable. |
| 表情含义词 | A Mandarin meaning keyword of up to 4 Chinese characters per sticker. Avoid duplicates and punctuation. |

The authenticated portal is needed to check names, fill in rights details and meaning keywords, and verify appreciation eligibility. Account and payout setup, creator attestations, the decision to submit, and WeChat review belong to the creator. A local check can determine technical readiness only.

## Decisions specific to this toolkit

- Preparing all five supplementary roles is the requested publishing profile. WeChat describes appreciation as an account-dependent feature.
- JPEG is a supported **source** for appreciation artwork. The upload file must be converted to PNG because both appreciation sections of the official guide list only GIF and PNG.
- The guide prints “KB” without an exact byte definition. The toolkit uses conservative decimal ceilings of 500,000 and 100,000 bytes. Frame decoding, positive motion timings and an infinite-loop marker are deterministic local checks. A live portal may apply additional checks.
- The profile uses opaque banner and appreciation exports. The wording in the guide is a design recommendation to avoid transparent backgrounds. Cover and icon transparency is explicit.
- The guide gives limits in Chinese characters. Local text length checks are a reproducible approximation of the portal counter for mixed scripts and composed characters.

## Verification and updates

The public guide is a JavaScript application. An HTTP success response containing only its HTML shell does not verify a rule. Inspect the album and appreciation sections after rendering, or verify their rendered text in the bundle linked by the official shell. On the date above the shell referenced build `26052800`, guide module `index.f84d77217115a9c8a0ed.js`. Its SHA-256 was `9d16725d109eb65349369ceeda6212015d70af4f8121c34be92396bfe754cd78`. This records the evidence behind this version. If the platform changes, update the local constraints, tests and verification date together.

[Official album and appreciation guide](https://sticker.weixin.qq.com/cgi-bin/mmemoticon-bin/readtemplate?t=guide/index.html#/makingSpecifications) · [Dated official guide bundle](https://res.wx.qq.com/t/wx_fed/base/sticker_platform/26052800/static/js/pages/guide/index.f84d77217115a9c8a0ed.js)
