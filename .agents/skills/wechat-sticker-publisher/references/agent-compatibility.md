# Running the skill in an agent

The project or user installation supplies these same instructions to Codex, Claude Code, Gemini CLI, Cursor, OpenCode, GitHub Copilot CLI and DeepSeek Harness. A compatible Agent Skills client can also load this directory intact. Use a host with filesystem and shell access for the actual export.

1. Install the Python distribution and activate its environment in the shell that launches the host. Run `wechat-sticker --help`.
2. From the album workspace, run `wechat-sticker skill list` to find the adapter ID. Run `wechat-sticker skill install --agent ID --scope project --dry-run` to preview, then run it without `--dry-run`. Use `--scope user` for personal installation across projects.
3. Open the creator workspace in the host. Refresh its skill catalog or restart the session. Ask “Package my stickers for WeChat publishing.” If needed, explicitly name `wechat-sticker-publisher`.
4. If the skill is absent or shadowed, run `wechat-sticker skill doctor --agent ID` from that project. Check which installed path the host actually loads. Use the ordinary CLI from the project shell if the host cannot run commands.

Project policy, tool permissions and model availability belong to the host. Offline CLI packaging and missing-art briefs work independently. For the tested harness versions and known limitations, see the [compatibility matrix](https://github.com/hnt119/wechat-sticker-publisher/blob/main/docs/agent-compatibility.md).

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
