# Public-release audit

This audit records the local review of the initial v0.1.0 candidate (`c78808e`) on 2026-11-19. The shareable unit is this standalone toolkit repository. The creator workspace, original character references, working artwork and private publishing packages are outside its root.

## Source and artwork checks

| Check | Result |
| --- | --- |
| Candidate contents | Enumerated tracked and nonignored untracked files with `git ls-files --cached --others --exclude-standard`. At the source-content check, 47 files comprised 32 UTF-8 text files and 15 PNGs, including this report. The list contained no symlinks, environments, credential files, private documents, release ZIPs or GIFs. |
| Private file separation | Compared public SHA-256 hashes with same-size files across 1,555 private workspace files and 930 entries from 17 private archives. No identical file or archive entry appeared in the candidate. |
| Private pixel separation | Inspected 1,240 private image files. For the 377 with dimensions matching a public image, decoded all 1,272 corresponding frames and compared hashes of visible RGBA pixels. No match. |
| Public image origin | Ran the sample drawing script alone in an empty directory. It recreated all 15 published images byte for byte, including the eight stickers, five supplementary images, project icon and preview. The script draws shapes from coordinates and uses Pillow. |
| Embedded data | Parsed each PNG's chunks through its final byte. Only IHDR, IDAT and IEND appeared. There were no appended bytes, text comments, EXIF, creator names, thumbnails or location records. |
| Source and fixtures | Scanned public text and filenames for creator identifiers, private asset names, machine paths and common live-key, bearer-token, embedded-password and private-key patterns. No matches. Inspected the optional provider tests, which use a synthetic credential string and mocked client. The README names environment variables for local setup. |
| Documentation | Checked repository-relative Markdown links. All repository-relative links resolved at the source-content check. Web links identified the official WeChat guide, its Tencent-hosted application bundle and the provider documentation. |
| Initial repository history | The isolated local repository had an unborn default branch, zero Git objects, zero refs and zero configured remotes before the initial candidate commit. |

Exact-file and pixel comparisons establish separation from the inspected collection. Independent regeneration also establishes the origin of images even when a different encoder might change their file bytes. Credential scans cover recognizable patterns.

## Integration evidence

| Test | Observed result |
| --- | --- |
| A · Offline sample | The synthetic sample passed validation and built under an operating-system network-denial policy. There were eight sticker exports, all five supporting images, Chinese copy, checklists and a ZIP. A separate clean virtual environment installed the toolkit and both runtime dependencies using only a prepared wheelhouse and `pip --no-index`, then completed the documented quick start. |
| B · Missing artwork | Removing the banner from a scratch copy produced an incomplete result, a brief with dimensions and delivery path, and an archive containing the other work. The offline regression run guarded network access. Restoring the source allowed a fresh complete build. |
| C · Optional provider unavailable | Explicit generation with missing provider configuration produced a new incomplete snapshot and recorded the missing resource. The previous complete archive remained intact. Provider integration tests used mocks. No paid request was made. |
| D · Separate creator project | Two private albums passed technical checks. A third had seven distinct animations, one short of the minimum. All fifteen existing supplementary images were present. Each of the 67 exported artwork files across the three ZIPs matched its selected private source byte for byte. Only aggregate evidence is published here. |

## Licensing and release scope

The MIT copyright notice is **Copyright (c) 2026 hnt119 and WeChat Sticker Publisher contributors**. MIT covers the toolkit and public synthetic demo assets, including the preview and icon. Creators retain ownership of their uploaded artwork and generated publishing packages, subject to third-party rights. Private original artwork and character references are outside the public license. The required Python dependencies are installed separately. [License](../LICENSE) · [Sample provenance](../examples/sample-album/README.md)

These tests covered the local candidate. The repository’s Actions page records subsequent CI runs. Paid image generation and official platform review were outside this audit.

## Distribution checks

Python 3.12.7, Pillow 12.3.0 and PyYAML 6.0.3 passed all 32 local tests, including file-size boundaries, partial-release recovery, concurrent builds and archive reproducibility. The optional adapter was also exercised with the real SDK and a mocked HTTP transport. The skill passed its structural validator and a separate creator workflow trial covering a missing image, oversized master, manual repair and a successful rebuild.

Both the wheel and source archive declare the SPDX expression `MIT` and include the repository's license verbatim. Compared the permission, notice condition and warranty paragraphs against the standard MIT text after normalizing line wrapping. The source archive contains the public sample, skill, CI configuration, tests and bilingual documentation. The wheel contains the Python implementation and packaging metadata, with the optional SDK declared under an extra. Archive inspection checked each file against the clean source tree or the expected packaging metadata. [SPDX MIT text](https://spdx.org/licenses/MIT.txt)

The initial candidate was a single root commit. The v0.1.0 tag identifies the final source used for the release downloads. SHA256SUMS accompanies the wheel and source distribution on the release page.
