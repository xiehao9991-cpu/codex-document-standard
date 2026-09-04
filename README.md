# Codex Document Standard

一套可复用的 Codex 工作文档统一规范，适用于报告、计划、复盘、会议纪要、方案、总结等专业文档。

它统一了标题层级、字体、颜色、段落间距、说明块、表格、链接与证据格式。用户本次要求、公司模板或已有文档样式始终优先。

需要可下载、可打印的统一格式版本，请使用 [`Codex Document Standard 使用教程`](docs/Codex-Document-Standard-使用教程.docx)。

## 访问与分享

本仓库是公开仓库。使用者无需登录 GitHub，直接打开下面的链接即可查看、下载或安装：

- 仓库主页：[github.com/xiehao9991-cpu/codex-document-standard](https://github.com/xiehao9991-cpu/codex-document-standard)
- Word 使用教程：[Download DOCX](https://raw.githubusercontent.com/xiehao9991-cpu/codex-document-standard/main/docs/Codex-Document-Standard-%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B.docx)
- Git 克隆地址：`https://github.com/xiehao9991-cpu/codex-document-standard.git`

分享给别人时，发送仓库主页链接即可。

## 包含内容

```text
codex-document-standard/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── docs/
│   └── Codex-Document-Standard-使用教程.docx
├── references/
│   └── style-standard.md
└── scripts/
    └── apply_dingtalk_heading_styles.py
```

- `SKILL.md`：定义适用场景、执行流程与边界。
- `agents/openai.yaml`：定义 Skill 在 Codex 中的展示名称和默认提示。
- `docs/Codex-Document-Standard-使用教程.docx`：按本 Skill 视觉规范排版的正式使用教程。
- `references/style-standard.md`：完整的文档视觉和结构规范。
- `scripts/apply_dingtalk_heading_styles.py`：DOCX 转换为钉钉在线文档后，重新写入并校验标题颜色、字号和粗体。

## 安装

### 方法一：让 Codex 安装

在 Codex 中发送：

```text
使用 $skill-installer 安装 GitHub 仓库 xiehao9991-cpu/codex-document-standard
根目录的 Skill；path 使用 .，安装名称使用 codex-document-standard。
```

安装完成后，在下一轮对话中使用。

### 方法二：使用 Git

macOS 或 Linux：

```bash
git clone https://github.com/xiehao9991-cpu/codex-document-standard.git ~/.codex/skills/codex-document-standard
```

Windows PowerShell：

```powershell
git clone https://github.com/xiehao9991-cpu/codex-document-standard.git "$env:USERPROFILE\.codex\skills\codex-document-standard"
```

安装后重新开始一轮 Codex 对话，让 Codex 重新发现 Skill。

### 方法三：下载 ZIP

1. 在 GitHub 仓库页面选择 **Code → Download ZIP**。
2. 解压文件。
3. 将文件夹重命名为 `codex-document-standard`。
4. 把它放入 `~/.codex/skills/`。
5. 确认最终路径是 `~/.codex/skills/codex-document-standard/SKILL.md`，不要多嵌套一层目录。

## 使用

### 自动使用

安装后，Codex 在创建或整理以下工作文档时会自动加载该 Skill：

- 报告与工作总结
- 计划与方案
- 复盘与评审文档
- 会议纪要
- 制度说明
- 钉钉工作文档和文档表格

示例：

```text
把这份季度复盘整理成正式工作文档，保留现有数据和链接。
```

### 显式使用

需要确保使用本规范时，在请求中直接写出 Skill 名称：

```text
使用 $codex-document-standard 创建一份项目周报。
```

```text
使用 $codex-document-standard 统一这份会议纪要的标题、正文和表格样式，不改动原文事实。
```

### 钉钉在线文档

钉钉在把 DOCX 转换成在线文档时会清除标题的自定义颜色和字号。转换完成后，需要用返回的文档 `nodeId` 执行：

```bash
python scripts/apply_dingtalk_heading_styles.py <node-id>
```

脚本会重新写入 Title、一级、二级和三级标题的颜色、字号、粗体及段落间距，并把钉钉标准表格文字规范为 10 pt。随后读取钉钉原生 JSONML 验证结果。源 DOCX 不得使用空白段落制造间距；脚本检测到空白块时会直接报错。仅检查导出的 DOCX 不能证明钉钉页面显示一致。

## 默认规则摘要

- 风格：专业、克制、清晰。
- 主色：`#2F75B5`。
- 深色表头：`#005D8D`。
- 标题：使用连续的 H1–H4 层级。
- 正文：默认 10.5 pt、1.2 倍行距。
- 标准表格：本地 DOCX 的表头和正文均为 10.5 pt，与外部正文一致；钉钉在线文档保留 10 pt。
- 表格：文字左对齐、数字右对齐、日期和状态居中。
- 空值：统一使用 `—`。
- 日期：统一使用 `YYYY-MM-DD`。
- 内容：结论先行，只使用有记录支持的事实和真实链接。
- 验证：完成前检查标题、间距、表格、链接、溢出和固定内容。

完整规则见 [`references/style-standard.md`](references/style-standard.md)。

## 优先级

发生冲突时按以下顺序执行：

1. 用户本次明确要求。
2. 用户提供的公司模板或原文档样式。
3. 本 Skill 的默认规范。

因此，该 Skill 不会为了统一样式而覆盖用户指定模板，也不会擅自重建整份现有文档。

## 不适用范围

默认不用于：

- 源代码和 README
- PPT 或其他演示文稿
- Excel 或其他电子表格文件
- 营销海报与视觉设计稿

用户明确要求沿用同一视觉语言时除外。

## 更新

使用 Git 安装时，可以更新到仓库最新版本。

macOS 或 Linux：

```bash
git -C ~/.codex/skills/codex-document-standard pull
```

Windows PowerShell：

```powershell
git -C "$env:USERPROFILE\.codex\skills\codex-document-standard" pull
```

## 自定义

需要改变品牌色、字体或业务字段时，可以修改 `references/style-standard.md`。建议保留以下原则：

- 用户和公司模板优先。
- 编辑现有文档时只修改授权范围。
- 不伪造事实、链接、数据、日期和责任人。
- 交付前检查实际渲染结果。

## License

[MIT](LICENSE)
