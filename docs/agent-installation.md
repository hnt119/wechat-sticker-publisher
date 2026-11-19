# Install the publishing skill

Install the v0.2.0 CLI from its wheel, source archive or checkout using `python -m pip install <path>` in a Python 3.10+ virtual environment. Activate that environment before launching the host so it can run `wechat-sticker`. The CLI carries the skill and all three references. Installation uses local files and requires no model, API key or agent SDK.

## Choose the scope

Run one command for the host you use. Project scope installs for the creator workspace. User scope makes the skill available to your own projects. The installer reuses a matching visible copy within the requested scope. An explicit user install can therefore coexist with a project copy. Open a terminal in the intended workspace, or pass `--project DIR` before `skill`.

| Host | Example |
| --- | --- |
| OpenAI Codex | `wechat-sticker skill install --agent codex --scope user` |
| Claude Code | `wechat-sticker skill install --agent claude-code --scope user` |
| Gemini CLI | `wechat-sticker skill install --agent gemini-cli --scope user` |
| Cursor | `wechat-sticker skill install --agent cursor --scope project` |
| OpenCode | `wechat-sticker skill install --agent opencode --scope project` |
| GitHub Copilot CLI | `wechat-sticker skill install --agent github-copilot --scope project` |
| DeepSeek Harness | `wechat-sticker skill install --agent deepseek-harness --scope project` |

Preview the destination and inspect the existing installations before making changes.

```sh
wechat-sticker skill list
wechat-sticker skill install --agent dsh --scope user --dry-run
wechat-sticker skill doctor --agent dsh
wechat-sticker skill uninstall --agent dsh --scope project --dry-run
```

Run the uninstall command without `--dry-run` to remove an unchanged installation owned by the installer. It preserves manually copied, modified or unrelated files. If a name collides, inspect both copies and back up your edits. Where supported, use `--layout shared` to choose a shared directory or `--layout native` for a host-specific one. Check the reported path before changing a shared installation used by several hosts. To migrate a hand-installed v0.1.1 Codex skill, move the old directory to a backup outside every discovery root, then install again. Keep any custom instructions you want to reapply.

The installer checks direct child bundles in the standard roots for the requested scope. Check the host catalog for administrator policy, plugins, custom directories and inherited or nested project skills. Diagnostics can report a symbolic link as a candidate. Install and uninstall require a regular destination.

## Try it in an album

Open the directory containing `publishing-config/` in the host. Reload the skill catalog or start a new session and ask **“Package my stickers for WeChat publishing.”** Name `wechat-sticker-publisher` explicitly if automatic selection misses it. Approve workspace reads, shell execution and writes according to your host policy. Look for `release-summary.md`, each album’s report and the ZIP in the release directory printed by the CLI.

If your host cannot start a model session or run a shell command, run `wechat-sticker validate` and `wechat-sticker build --offline` yourself in the album folder. The optional image provider is only needed when you choose to generate missing artwork. [Creator guide](creator-guide.md) · [Host paths, versions and evidence](agent-compatibility.md) · [DeepSeek Harness guide](deepseek-harness.md)

## Other Agent Skills clients

A host implementing the Agent Skills format can load the entire `wechat-sticker-publisher/` directory from its configured skill root. Preserve its name and relative references. The canonical source is under `.agents/skills/` in this repository. General-purpose tools such as Vercel’s `skills` CLI can install repository skills across agents. The built-in installer also works from a locally installed Python distribution, including on an offline computer. [Agent Skills specification](https://agentskills.io/specification) · [Vercel skills CLI](https://github.com/vercel-labs/skills)
