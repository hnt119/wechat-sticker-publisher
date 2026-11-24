# Running the skill in an agent

The project or user installation supplies these same instructions to Codex, Claude Code, Gemini CLI, Cursor, OpenCode, GitHub Copilot CLI and DeepSeek Harness. A compatible Agent Skills client can also load this directory intact. Use a host with filesystem and shell access for the actual export.

## Locate the publishing CLI

Run `wechat-sticker --help` in the shell the agent uses. If it is missing, ask whether the creator already has a tool installation or virtual environment. Start the host with that executable on its path.

For a fresh v0.2.1 installation with uv and Python 3.10+, offer the following command from the folder containing the verified wheel. Get the wheel and `SHA256SUMS` from the same v0.2.1 entry in [GitHub Releases](https://github.com/hnt119/wechat-sticker-publisher/releases) once listed, or from the [Release distributions run](https://github.com/hnt119/wechat-sticker-publisher/actions/workflows/release.yml) for the selected commit. Ask the creator before downloading files, installing software or fetching dependencies.

```sh
uv tool install ./wechat_sticker_publisher-0.2.1-py3-none-any.whl
```

With a creator-provided local wheelhouse, a configured Python environment can instead use `python -m pip install --no-index --find-links WHEELHOUSE wechat-sticker-publisher==0.2.1`. Replace `WHEELHOUSE` with its local directory. Retry `wechat-sticker --help` before working on the album. The packaged CLI handles validation, briefs and exports offline.

## Choose one skill installer

1. If the creator already installed this skill with the external `skills` CLI, use that manager for updates and removal. It can place a real directory or a link in the host's skill root and record it in a lockfile. Leave those files under its control.
2. To install through the Python CLI, from the album workspace run `wechat-sticker skill list` to find the adapter ID. Run `wechat-sticker skill install --agent ID --scope project --dry-run` to preview, then run it without `--dry-run`. Use `--scope user` for personal installation across projects.
3. Open the creator workspace in the host. Refresh its skill catalog or restart the session. Ask “Package my stickers for WeChat publishing.” If needed, explicitly name `wechat-sticker-publisher`.
4. If the skill is absent or shadowed, run `wechat-sticker skill doctor --agent ID` from that project. Check which installed path the host actually loads. Use the ordinary CLI from the project shell if the host cannot run commands.

Project policy, tool permissions and model availability belong to the host. Offline CLI packaging and missing-art briefs work independently. For tested harness versions and known limitations, open `docs/agent-compatibility.md` in the matching source archive or [repository revision](https://github.com/hnt119/wechat-sticker-publisher).

## License for the distributed skill

MIT License

Copyright (c) 2026 hnt119 and WeChat Sticker Publisher contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
