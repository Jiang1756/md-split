# Markdown 拆分工具

[PROJECT-TYPE] Application  
这个仓库提供一个对初学者友好的命令行脚本 `split_markdown.py`，用于将 Markdown
文档按照指定的标题级别拆分为多个章节或多个文件。

## 特性
- 只依赖 Python 标准库，可直接运行。
- `split_markdown(text, level)` 核心函数可在其他脚本中复用。
- 支持 ATX 风格（`#` ~ `######`）标题识别，并正确处理连续标题、空章节以及文档
  开头无标题的场景。
- 简洁的 CLI，可以输出章节概览或写出独立 Markdown 文件。

## 环境需求
- Python 3.9 及以上版本（用于 `list[dict]` 等现代类型注解）

## 快速上手

```bash
# 查看演示（不带参数时会输出内置示例）
python3 split_markdown.py

# 将 input.md 按二级标题拆分，并打印章节概览
python3 split_markdown.py input.md --level 2

# 写出多个章节文件（自动创建目录）
python3 split_markdown.py input.md --level 2 --output-dir out_sections
```

### 命令行参数
- `input`: 必填，Markdown 文件路径。
- `--level`: 拆分的标题级别，默认 2（范围 1~6）。
- `--encoding`: 读取与写入文件时使用的编码，默认 `utf-8`。
- `--output-dir`: 若设置，则将章节写入该目录，以 `01_title.md` 形式命名。

当不传 `--output-dir` 时，终端会展示各章节的索引、标题、级别与内容行数，帮助你快
速确认拆分情况。

## 章节文件命名规则
写入文件时会使用顺序编号加标题片段，例如 `01_介绍.md`。标题会被转为小写字母数字
和 `_` / `-`，并截断至 40 个字符，从而保证跨平台兼容性。没有标题的章节会使用
`untitled`。

## 作为库调用

```python
from split_markdown import split_markdown

with open("input.md", "r", encoding="utf-8") as f:
    text = f.read()

sections = split_markdown(text, level=2)
for section in sections:
    print(section["title"], section["start_line"], section["end_line"])
```

`split_markdown` 会返回一个列表，每项包含 `title`、`level`、`content`、
`start_line`、`end_line`。当文档开头没有匹配的标题时，会先返回一个
`title=None` 的章节来保存前置内容。

## 内置示例
当直接运行 `python3 split_markdown.py` 且没有额外参数时，脚本会展示一段包含
H1/H2/H3 的示例文本，并打印拆分结果，便于新手理解输出格式。

## 许可证
尚未指定许可，默认仅供个人学习参考。若需正式发布或商用，请自行补充许可文本。
