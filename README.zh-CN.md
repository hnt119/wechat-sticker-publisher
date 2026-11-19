# 微信表情专辑打包工具

[English](README.md) · [v0.1.1 发布说明](https://github.com/hnt119/wechat-sticker-publisher/releases/tag/v0.1.1)

把现有插画或动态 GIF 整理成微信表情专辑。命令行工具会按上架尺寸导出图片，生成中文上架文案、预览图和每张专辑的 ZIP，供创作者检查并手动上传。**安装后可离线打包，无需 API 密钥、付费订阅或云端账号。**

<img src="examples/sample-album/preview.png" width="560" alt="「栗子巡游」的八张示例表情，包括挥手、奔跑和打盹">

## 试做示例专辑

安装 Git 和 Python 3.10 或更高版本后，在 macOS 或 Linux 终端运行以下命令。示例包含八张静态表情和全部五张发布配图。[Windows 及离线安装说明](docs/creator-guide.zh-CN.md)

```sh
git clone https://github.com/hnt119/wechat-sticker-publisher.git
cd wechat-sticker-publisher
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .

wechat-sticker --project examples/sample-album build --offline --release first-look
```

打开 `examples/sample-album/releases/wechat/first-look/release-summary.md`，示例应显示 **TECHNICAL_PASS**。同一目录还包含专辑 ZIP、可逐个上传的成品、预览图和提交核对清单。[示例素材与绘图源码](examples/sample-album/)

## 打包自己的表情

1. 在自己的创作目录中运行 `wechat-sticker init`。打开 `publishing-config/album.json`，填写专辑名称、介绍、赞赏引导语和角色标识。
2. 将 8–24 个不同动作放入 `artwork/album/stickers/`，整张专辑使用统一的静态或动态类型。将横幅、封面、聊天图标和两张赞赏配图放入 `artwork/album/supplementary/`。
3. 运行 `wechat-sticker validate` 检查源文件，再运行 `wechat-sticker build` 导出。缺图时也会保存可用的成品，列出缺少的图片及制作要求。补齐后再打包即可。

创作者指南包含图片命名、GIF 帧时长和循环、专辑清单、排序、命令用法及常见问题。手动上传前，请在微信表情开放平台后台核名并确认账号资格。[创作者指南](docs/creator-guide.zh-CN.md) · [已核对的微信制作规范](.agents/skills/wechat-sticker-publisher/references/wechat-specifications.md)

## 在 Codex 中使用

安装命令行工具后，将 `.agents/skills/wechat-sticker-publisher/` 复制到 `~/.agents/skills/`。在创作项目中启动新的 Codex 会话，输入**“帮我打包微信表情”**即可调用同一套工具。需要补图时，也可明确要求使用已配置的作图服务。[技能说明](.agents/skills/wechat-sticker-publisher/SKILL.md) · [可选作图服务](docs/artwork-providers.md)

## 许可与项目资料

MIT 许可证涵盖工具本身和公开的合成示例素材，包括预览图及项目图标。创作者保留对自己画作及生成发布包的所有权，并须尊重第三方权利。私人角色原画与未发布专辑的权利仍归创作者所有。本项目由独立开发者维护，与微信、腾讯无官方关联。[许可证](LICENSE) · [贡献指南](CONTRIBUTING.md) · [更新日志](CHANGELOG.md) · [公开发布审计](docs/public-release-audit.md)
