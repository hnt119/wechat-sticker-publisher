# Install the publishing skill

Install the Python CLI using the [quick start](../README.md#install-the-cli), then verify `wechat-sticker --version` in the shell used to launch the agent. Both the wheel and source distribution contain the canonical skill and its three references. The CLI handles album files. A skill installer supplies instructions to the host.

## Choose an installer

Use the bundled installer below for local installation without Node.js or network access. If you already manage skills with the Vercel CLI, use it instead from the creator workspace. The tests used skills 1.9.0 on Node.js 24.22.3. That installer requires Node.js 22.20 or later.

```sh
npx skills@1.9.0 add hnt119/wechat-sticker-publisher --list
npx skills@1.9.0 add hnt119/wechat-sticker-publisher --skill wechat-sticker-publisher --agent claude-code
```

To pin the source, append a published tag or full commit to the repository name, such as `hnt119/wechat-sticker-publisher@v0.2.1` once that tag is available. The upstream CLI can create shared copies, links and its own lockfile. Manage that installation with the same installer. Installing by GitHub repository works independently of a skills.sh directory listing. The external installer can need network access and does not install the Python CLI. [Upstream CLI](https://github.com/vercel-labs/skills)

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

## Upgrade from v0.2.0

Install the new CLI with the same tool manager, using the reviewed wheel path or release URL. With uv, use `uv tool install --reinstall WHEEL`; with pipx, use `pipx install --force WHEEL`. Replace `WHEEL` with the chosen file or URL. Run `wechat-sticker --version` and `wechat-sticker skill doctor --agent codex` to check the active installation. v0.2.1 diagnostics include the CLI, interpreter and dependency versions.

An unchanged, native-installer-managed v0.2.0 skill can be updated separately. Use the same agent, scope and project you used originally.

```sh
wechat-sticker skill uninstall --agent codex --scope project --dry-run
wechat-sticker skill uninstall --agent codex --scope project
wechat-sticker skill install --agent codex --scope project
```

If the preview reports a modification or ownership conflict, keep the copy. Back up custom instructions outside every discovery root before choosing whether to replace them. An upstream-managed link or copy should be updated by its own installer. The CLI upgrade and skill installer operate independently of artwork, manifests and existing release directories.

## Try it in an album

Open the directory containing `publishing-config/` in the host. Reload the skill catalog or start a new session and ask **“Package my stickers for WeChat publishing.”** Name `wechat-sticker-publisher` explicitly if automatic selection misses it. Approve workspace reads, shell execution and writes according to your host policy. Look for `release-summary.md`, each album’s report and the ZIP in the release directory printed by the CLI.

If your host cannot start a model session or run a shell command, run `wechat-sticker validate` and `wechat-sticker build --offline` yourself in the album folder. The optional image provider is only needed when you choose to generate missing artwork. [Creator guide](creator-guide.md) · [Host paths, versions and evidence](agent-compatibility.md) · [DeepSeek Harness guide](deepseek-harness.md)

## Other Agent Skills clients

A host implementing the Agent Skills format can load the entire `wechat-sticker-publisher/` directory from its configured skill root. Preserve its name and relative references. The canonical source is under `.agents/skills/` in this repository. General-purpose tools such as Vercel’s `skills` CLI can install repository skills across agents. The built-in installer also works from a locally installed Python distribution, including on an offline computer. [Agent Skills specification](https://agentskills.io/specification) · [Vercel skills CLI](https://github.com/vercel-labs/skills)
