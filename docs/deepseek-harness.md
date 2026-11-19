# DeepSeek Harness

DeepSeek Harness (DSH) discovers this project’s portable skill and loads it into a DSH session. The skill uses the same `wechat-sticker` executable as the standalone workflow. DSH is a distinct agent runtime, with its own workspace, permissions and model settings. Installation, catalog discovery and instruction loading were verified in developer preview **0.2.2-rc.5**. Model-driven album packaging remains **BLOCKED** in the release-candidate tests. [Official DSH site](https://www.deepseek.com/harness/en/) · [DSH source at the tested release](https://github.com/deepseek-ai/deepseek-harness/tree/dsh-v0.2.2-rc.5) · [Compatibility matrix](agent-compatibility.md)

## Start in an album

Install the toolkit, activate its Python environment, and open a terminal in the directory containing the album’s `publishing-config/`. To try the public example from the toolkit checkout, use `cd examples/sample-album`. The project installer uses the nearest Git root, so a sample inside the checkout can already use its canonical shared skill. [CLI installation](../README.md#try-the-sample) · [Public sample album](../examples/sample-album/)

Choose one scope. These commands show the project installation and how to preview a user installation for all your workspaces.

```sh
wechat-sticker skill install --agent deepseek-harness --scope project
wechat-sticker skill install --agent dsh --scope user --dry-run
```

For a user installation, repeat the second command without `--dry-run`. Use `--layout shared` to select the corresponding `.agents/skills` root explicitly. To check local paths and the executable, run `wechat-sticker skill doctor --agent dsh`. A cached `npx` launcher may work even when the doctor cannot find a `dsh` executable on `PATH`. [Installer and uninstall commands](agent-installation.md)

With Node.js **24.9.0 or newer** and npm installed, launch the pinned version. The first launch can download DSH.

```sh
npx @deepseek-ai/dsh@0.2.2-rc.5 --version
npx @deepseek-ai/dsh@0.2.2-rc.5 web
```

1. In the Web UI, click **Choose workspace**, add the album directory, and select it. A fresh Web UI needs a selection even when launched in that directory. Configure an authorized model under **Settings → Models** for a live conversation.
2. In a new session, ask **“Use wechat-sticker-publisher to validate and package this album for WeChat.”** You can also start the message with `/wechat-sticker-publisher` to request the instructions explicitly.
3. Allow the shell to run the installed CLI, read the selected artwork and write the release in that workspace. The current DSH permission policy controls which operations need approval. Packaging needs no image-generation plugin.
4. Open `releases/wechat/<release-name>/release-summary.md`, inspect the contact sheets and the album ZIP. A complete public sample reports `TECHNICAL_PASS`, eight stickers and five supplementary assets. For a partial package, read the reported missing roles and their briefs before preparing replacements.

The default Web server uses loopback and opens the browser. Use `web --no-open` to open the local URL yourself. Treat the tokenized startup URL as private. [Web UI guide](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.2-rc.5/docs/user/guide/index.md) · [Official model configuration](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.2-rc.5/docs/user/guide/providers.md)

## Where DSH finds the skill

In the shipped filesystem provider, the first readable entry with the same frontmatter name wins in this order. The catalog exposes the winning description and loads its body on request. Other provider layers or profile settings can affect the result. [Pinned skill discovery reference](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.2-rc.5/docs/subsystems/skills.md)

| Priority | Root |
|---|---|
| 1 | `<projectRoot>/.dsh/skills/` |
| 2 | `<projectRoot>/.agents/skills/` |
| 3 | Configured custom skill directories |
| 4 | `$DSH_HOME/skills/`, default `~/.dsh/skills/` |
| 5 | `$DSH_AGENTS_HOME/skills/`, default `~/.agents/skills/` |
| 6 | Configured bundled directory |

The project root is the nearest ancestor containing `.git`, or the session working directory when no Git root exists. DSH scans direct skill bundles and flat Markdown entries, using `name` and `description` in YAML frontmatter. Keep the whole `wechat-sticker-publisher/` directory together so references resolve. DSH’s two user roots are independent. Explicit DSH profile root settings can override the corresponding environment variables; blank environment values use the defaults. [Filesystem provider](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.2-rc.5/packages/skill/skill-filesystem/src/index.ts) · [Home directory resolution](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.2-rc.5/packages/util/home-paths/src/index.ts)

If discovery fails, confirm the selected workspace, inspect the effective roots for a duplicate frontmatter name, then open a fresh session. The installer can reuse an identical shared installation. If DSH loads older instructions, look first for a project-native entry shadowing the shared one. Inspect any modified copy before removing it. If DSH cannot run the CLI, launch it from a terminal with the toolkit environment activated. A missing model credential still allows these offline commands in the album directory.

```sh
wechat-sticker validate --all
wechat-sticker build --all --offline --release reference
```

## Release-candidate evidence

Checked on **2026-11-19**, **macOS 26.6.2 arm64**, **Node 24.22.3**, **DSH 0.2.2-rc.5**. The Web launcher answered unauthenticated loopback HTTP with 401 and shut down after the check. The test used a copy of the public sample with its own Git root, isolated DSH and shared-agent homes, and the candidate CLI on the process path.

| Level | Result | Observation |
|---|---|---|
| A · Installation | INSTALLER-TESTED | Installed and uninstalled through the candidate CLI for each of the four project/user × native/shared combinations. |
| B · Discovery and loading | VERIFIED | The real SDK profile’s `ctx.skills.list({cwd})` returned one matching entry per installation. A live DSH agent’s registered `skill` tool returned the complete canonical instructions and the resource directory of the winning installation. Four overlapping test fixtures confirmed the four standard roots’ relative priority. |
| C · Agent execution | BLOCKED | The real headless profile received the natural-language request. Its session catalog contained the skill. Inference stopped with `MISSING_CREDENTIAL` before a model could run the CLI. A separate explicit invocation loaded the instructions before the same stop. There is no DSH-produced ZIP to compare. |

A sanitized excerpt from the checks follows. The body hash covers UTF-8 Markdown after parsing the frontmatter and trimming surrounding whitespace.

```text
catalog matches per installed layout       1
winning roots as each higher copy retired project-dsh → project-agents → user-dsh → user-agents
canonical body SHA-256                    687b517fc1f4883e0c3f08b732d8eaea4e2fa51a6dbc51f462e93262aa25c593
explicit invocation in saved session      entire canonical body inside <skill_instructions>
natural-language headless run             exit 1, MISSING_CREDENTIAL
standalone reference and repeat ZIP       a05bcbe9d32860c168e7ce7ad990eb075874b9f4874e0c4913955f388e59b36e
```

To repeat the session-level checks, run each command in a disposable copy of the public album with the skill installed. These commands invoke the real harness and may use a configured model. The headless profile uses its own documented credential rules. Read its JSON events for tool executions and its final status. Its persisted session under `$DSH_HOME/sessions/` records the skill catalog and, for the slash invocation, the injected instructions. Keep raw session logs private. The standalone ZIP hash above came from two CLI builds in the recorded environment. [Headless profile](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.2-rc.5/packages/bundle/headless/README.md) · [Model-facing skill tool](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.2-rc.5/packages/skill/tool-skill/src/index.ts)

```sh
npx @deepseek-ai/dsh@0.2.2-rc.5 --profile headless --json \
  "/wechat-sticker-publisher Validate and package this sample for WeChat."
npx @deepseek-ai/dsh@0.2.2-rc.5 --profile headless --json \
  "Use wechat-sticker-publisher to validate and package this album for WeChat."
```

For an end-to-end comparison, start with identical inputs and the same CLI and dependencies. Build a standalone reference in a second copy, check both release summaries for the same asset counts and compare the album ZIP bytes with `cmp`.
