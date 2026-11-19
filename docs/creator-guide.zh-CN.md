# 创作者指南

[项目首页](../README.zh-CN.md) · [English](creator-guide.md)

## 在 Windows 或离线电脑上安装

请使用 Python 3.10 或更高版本。在仓库目录打开 PowerShell，运行以下命令。

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .
```

若目标电脑完全离线，可在系统、处理器架构和 Python 版本均相同的联网电脑上运行 `python -m pip wheel . --wheel-dir wheelhouse`，将生成的整个目录拷贝至目标电脑，再在虚拟环境内执行 `python -m pip install --no-index --find-links wheelhouse wechat-sticker-publisher`。

## 制作自己的专辑

1. 新建一个工作文件夹，在里面运行 `wechat-sticker init`，即会得到清单 `publishing-config/album.json` 和两个放图的目录。要创建一张编号为 `waves` 的动态专辑，可用 `wechat-sticker init --pack waves --type animated`。
2. 用文本编辑器打开清单，保留 JSON 字符串两边的引号，填写专辑名称、介绍、赞赏引导语和角色标识。各字段含义见下表。
3. 每个动作选择一个版本，将文件放进 `artwork/album/stickers/`。建议用 `01-wave.png`、`02-cheer.png`、`10-goodnight.png` 这样的补零编号控制顺序。其他配字版本和试稿请留在别的目录。
4. 将五幅发布配图放入 `artwork/album/supplementary/`。采用下方图片表中的文件名主体，例如 `banner.jpg` 和 `icon.png`。如使用自定义编号，上述路径中的 `album` 需换成自己的编号。
5. 在工作文件夹运行以下命令。程序会打印检查结果和发布包位置。

```sh
wechat-sticker inventory
wechat-sticker validate
wechat-sticker build --offline
```

`validate` 检查当前源文件。高清母版可能超出上架尺寸，`build` 会尝试导出并重新检查实际上传文件。缺图时也能打包现有素材。按报告里的作图说明补齐缺项，再运行一次构建即可。

## 专辑清单

每张专辑在 `publishing-config/` 下使用一份 JSON 或 YAML 文件。文件路径从含有 `publishing-config/` 的项目根目录算起。

| 字段 | 填写内容 |
| --- | --- |
| `id`、`type` | 固定的内部编号（例如 `waves`）。静态专辑填 `static`，动态专辑填 `animated`。 |
| `name` | 表情名称，最多八字，推荐五字以内。避免空格、标点，重名情况需在平台后台确认。 |
| `description` | 表情介绍，最多八十字，可以写角色的性格、故事或专辑里的日常。 |
| `appreciation` | 赞赏引导语，五至十五字。 |
| `characters`、`status` | 角色标识列表及创作者标注的制作状态。构建时另行报告技术检查结果。 |
| `sticker_directory` 或 `stickers` | 指定自动收集图片的文件夹；要手工排序，可删去 `sticker_directory`，在 `stickers` 中按顺序填写形如 `{"id": "wave", "path": "drawings/wave.png"}` 的对象。 |
| `supplementary` | 将每个配图名称对应到源文件路径，可直接指向已确认的母版。初始化模板也支持在配图目录中按名称收集图片。 |
| `references` | 可选的已确认角色参考图路径列表，供明确要求的作图流程使用。 |

直接填写初始化生成的模板即可，仓库示例提供填写好的清单。构建后从 `上架文案.md` 复制中文字段。

## 图片与检查项目

每张专辑收录 8–24 个不同的表情，整张使用统一的静态或动态类型。每个动作只选一个版本。工具会检查全部五张配图，其中包括赞赏引导图及致谢图。

| 图片或文件名主体 | 导出尺寸 | 格式 | 本地检查目标 |
| --- | --- | --- | --- |
| 表情主图 | 240 × 240 | 静态用 PNG、JPEG 或单帧 GIF，动态用多帧 GIF | ≤500 KB |
| `banner` 详情页横幅 | 750 × 400 | JPEG 或 PNG | ≤500 KB，不透明 |
| `cover` 表情封面图 | 240 × 240 | PNG | ≤500 KB，透明背景 |
| `icon` 聊天页图标 | 50 × 50 | PNG | ≤100 KB，透明背景 |
| `appreciation-guide` 赞赏引导图 | 750 × 560 | PNG 或 GIF | ≤500 KB，不透明 |
| `appreciation-thanks` 赞赏致谢图 | 750 × 750 | PNG 或 GIF | ≤500 KB，不透明 |

表中 1 KB 采用 1,000 字节。赞赏图片可提供 JPEG 母版，供工具转为平台接收的格式。工具解码源文件，检查尺寸、格式、文件大小及透明度。动态检查还涵盖帧数、可见变化、时长和持续循环。已合规的图片可原样复用，支持的母版可按比例缩放和优化，源文件保留在原处。请在正常速度下查看动图，在明暗底色上检查小图标，确认封面和图标无文字、方框或白边，横幅无文字。配字、角色一致性、画风、使用权和题材适宜性需人工复核。[本地规范、来源与核对日期](../.agents/skills/wechat-sticker-publisher/references/wechat-specifications.md)

## 命令速查

全局参数 `--project DIR` 指向另一个创作项目。专辑命令默认处理全部清单，也可用 `--pack ID` 指定一张，或用 `--all` 明确选择全部。任何子命令后都可加 `--help` 查看用法。

| 命令 | 用途 |
| --- | --- |
| `wechat-sticker init [--pack ID] [--type static\|animated]` | 创建可填写的清单及素材目录。 |
| `wechat-sticker inventory --all` | 盘点已声明及按目录收集的素材。使用 `inventory --scan DIR` 可独立扫描项目内指定的图片目录。 |
| `wechat-sticker validate --pack ID` | 检查清单、张数、重复项和源图。 |
| `wechat-sticker assets missing --all` | 列出仍需提供的素材。 |
| `wechat-sticker assets briefs --pack ID` | 获取缺图的制作要求。 |
| `wechat-sticker report --all` | 查看项目检查结果。 |
| `wechat-sticker build --all --offline` | 离线导出当前可用图片、文案、预览、报告、清单及压缩包。 |
| `wechat-sticker build --pack ID --release review-1` | 用自定标签保存一次发布，默认标签为本地日期。 |
| `wechat-sticker build --pack ID --generate-missing --provider NAME` | 请求已安装的可选插件生成缺少的配图。 |

检查类命令支持 `--json`，方便脚本读取。检查通过的退出码为 0，有缺项为 1，用法或配置错误为 2。报告显示缺项时，成功导出的文件仍保存在发布目录。

## 核对发布包

在 `releases/wechat/<发布标签>/` 下打开 `release-summary.md`、预览图及各专辑的 `validation-report.md`。专辑文件夹内含 `stickers/`、`supplementary/`、`metadata.json`、`上架文案.md` 和 `submission-checklist.md`。每张专辑另有一份 ZIP。有缺项时文件名以 `-INCOMPLETE.zip` 结尾，包内的 `artwork-briefs.json` 记录待办素材。重复使用标签 `review-1` 构建会依次生成 `review-1-02`、`review-1-03` 等目录。压缩包条目按稳定顺序和时间戳写入，相同输入、设置和软件版本可复现。

`TECHNICAL_PASS` 表示导出文件通过本地技术检查，`INCOMPLETE` 表示仍有待处理事项。请在微信表情开放平台后台核名、确认账号赞赏资格、填写版权署名和每张的含义词，核对当期要求，人工检查后逐项上传。审核结果由平台决定。

## 智能体打包与可选作图

安装命令行工具并激活其 Python 虚拟环境。在创作目录执行 `wechat-sticker skill list` 查看智能体标识，然后运行 `wechat-sticker skill install --agent codex --scope project`，将 `codex` 替换为相应标识。个人全局安装可改用 `--scope user`。在智能体的新会话中打开专辑目录，输入“帮我把这些表情打包成微信表情专辑”。按上一节的方法核对生成的 ZIP、报告和缺图说明。[安装与排错](agent-installation.md) · [兼容性实测](agent-compatibility.md) · [DeepSeek Harness 使用说明](deepseek-harness.md)

如需使用可选的 OpenAI Images 适配器，在工具仓库运行 `python -m pip install '.[openai]'`，在本机环境中设置 `OPENAI_API_KEY` 和 `WECHAT_STICKER_IMAGE_MODEL`，再执行 `wechat-sticker build --pack ID --generate-missing --provider openai-images`。这条作图命令可能将明确选用的参考图发给服务商并产生费用。其他已安装插件可通过 `--provider NAME` 或 `WECHAT_STICKER_PROVIDER` 配合 `--generate-missing` 选择。未配置插件时，程序会记录缺项、保存离线成果并提供手动作图说明。[插件配置与接口](artwork-providers.md)

## 常见问题

- **找不到命令。** 重新激活安装时使用的虚拟环境，执行 `python -m pip show wechat-sticker-publisher` 可查看安装位置。
- **找不到专辑或图片。** `--project` 要指向含有 `publishing-config/` 的项目。检查文件名大小写、配图名称及清单中的项目相对路径。
- **封面透明度不合格。** 导出带真实透明背景、主体可见的 PNG。白色画布及画上去的棋盘格都是不透明像素。
- **动态专辑数量不足。** 按不同动作计数，补充一个已完成的独立动作。相似动作、换字版本还需人工评估。
- **GIF 导出后仍太大。** 在动画母版中减少噪点、帧数或颜色数量，保留容易辨认的动作和节奏。重新导出，再播放实际成品。
