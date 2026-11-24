# 微信表情专辑打包工具

[English](README.md) · [最新稳定版](https://github.com/hnt119/wechat-sticker-publisher/releases/latest)

离线优先的命令行工具与可移植的智能体技能，用于准备、校验和打包微信表情专辑。把插画或动态 GIF 整理成可上传的图片、中文上架文案、预览图和专辑 ZIP，供创作者检查后手动提交。

![「栗子巡游」的八张示例表情，包括挥手、奔跑和打盹](examples/sample-album/preview.png)

## 安装命令行工具

准备好 Python 3.10 或更高版本及 uv。在 [GitHub Releases](https://github.com/hnt119/wechat-sticker-publisher/releases) 列出 v0.2.1 后，从该版本一并下载 wheel 和 `SHA256SUMS`。如需试用发布前的构建，请在 [Release distributions](https://github.com/hnt119/wechat-sticker-publisher/actions/workflows/release.yml) 中选择对应提交且运行成功的记录，下载并解压构建产物。核对 wheel 的 SHA-256 后，在下载目录中运行以下命令。[安装 uv](https://docs.astral.sh/uv/getting-started/installation/) · [安装 pipx](https://pipx.pypa.io/stable/how-to/install-pipx.html)

```sh
uv tool install ./wechat_sticker_publisher-0.2.1-py3-none-any.whl
wechat-sticker --version
```

也可使用 pipx（需要 Python 3.11 或更高版本）：将 `uv tool install` 换成 `pipx install`，使用同一个本地 wheel 文件。若终端找不到 `wechat-sticker`，请按安装方式运行 `uv tool update-shell` 或 `pipx ensurepath`，再重新打开终端。安装完成后即可离线使用。[离线与 Windows 安装](docs/creator-guide.zh-CN.md) · [开发环境安装](CONTRIBUTING.md)

## 打包自己的表情

1. 在新建的专辑目录运行 `wechat-sticker init`。打开 `publishing-config/album.json`，填写专辑名称、介绍、赞赏引导语和角色标识。
2. 将 8–24 个不同动作放入 `artwork/album/stickers/`。同一张专辑统一使用静态或动态表情。将横幅、封面、聊天图标和两张赞赏配图放入 `artwork/album/supplementary/`。
3. 先检查源文件，再打包发布目录。

```sh
wechat-sticker validate
wechat-sticker build --offline --release first-look
```

打开 `releases/wechat/first-look/release-summary.md` 查看打包结果。同一目录下有专辑 ZIP、预览图和已解包的专辑文件夹，校验报告和提交核对清单在专辑文件夹内。若有缺图，工具会导出现有成品并生成补图说明。[创作者指南与文件命名](docs/creator-guide.zh-CN.md)

## 在智能体中使用

先按上文安装命令行工具，让智能体能够运行 `wechat-sticker`。然后在专辑目录中**任选一种**方式安装技能。

| 安装方式 | 命令 |
| --- | --- |
| Python 工具自带的离线安装器 | `wechat-sticker skill install --agent codex --scope project` |
| Vercel skills CLI，从 GitHub 下载 | `npx skills@1.9.0 add hnt119/wechat-sticker-publisher --skill wechat-sticker-publisher --agent claude-code` |

外部技能安装器提供指令和参考资料，实际打包由单独安装的 Python 工具完成。在智能体中打开专辑目录，输入**“帮我把这些表情打包成微信表情专辑”**。

内置安装器适配 Codex、Claude Code、Gemini CLI、Cursor、OpenCode、GitHub Copilot CLI 和 DeepSeek Harness。Codex 与 OpenCode 已完成实机端到端示例打包。[安装范围与升级](docs/agent-installation.md) · [各智能体验证记录](docs/agent-compatibility.md)

## 试做完整示例

从同一版本或同一次工作流取得源码包 `wechat_sticker_publisher-0.2.1.tar.gz` 并解压，在其中的 `examples/sample-album` 目录运行上文的校验与打包命令。「栗子巡游」示例包含八张表情和五张配图，应显示 **TECHNICAL_PASS**。

## 隐私与许可

MIT 许可证涵盖工具与原创合成示例素材。创作者保留对自己画作及生成发布包的权利，并须尊重第三方权利。私人角色设计和未发布专辑的权利仍归创作者。明确要求生成配图时，可选作图服务可处理已授权的参考图。请人工核对成品后手动上传。本项目独立开发，与微信、腾讯无官方关联。[许可证](LICENSE) · [公开发布审计](docs/public-release-audit.md)
