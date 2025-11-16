"""
split_markdown.py
~~~~~~~~~~~~~~~~~~

一个用于按指定标题级别拆分 Markdown 文本的实用脚本，同时提供可直接使用的
命令行接口。核心拆分逻辑通过 `split_markdown` 函数暴露，便于在其他 Python
程序中复用，并确保所有实现仅依赖标准库。
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")


@dataclass
class Heading:
    """保存单个 Markdown 标题的关键信息。"""

    level: int
    title: str
    line_number: int


def parse_headings(lines: Iterable[str]) -> List[Heading]:
    """
    从 Markdown 行序列中收集所有 ATX 风格标题。

    参数:
        lines: 通过 text.splitlines() 得到的字符串行。

    返回:
        Heading 对象列表，包含标题级别、文本以及所在行号。
    """
    headings: List[Heading] = []
    for index, line in enumerate(lines):
        match = HEADING_PATTERN.match(line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        headings.append(Heading(level=level, title=title, line_number=index))
    return headings


def split_markdown(text: str, level: int = 2) -> List[dict]:
    """
    按指定标题级别拆分 Markdown 文本。

    参数:
        text: 完整的 Markdown 字符串。
        level: 需要拆分的标题级别（1-6）。

    返回:
        字典列表，每项代表一个章节，字段包括:
            - "title": 标题文本（字符串或 None）
            - "level": 标题级别（1-6 或 None，当章节来自前置内容时）
            - "content": 当前章节的 Markdown 内容（不含标题行）
            - "start_line": 标题所在行号（0-based）
            - "end_line": 章节的最后一行行号（0-based）

    异常:
        ValueError: 当 level 不在 1..6 范围内时抛出。
    """
    if not 1 <= level <= 6:
        raise ValueError("level 必须在 1 到 6 之间")

    plain_lines = text.splitlines()
    lines_with_endings = text.splitlines(keepends=True)
    headings = parse_headings(plain_lines)
    split_heads = [h for h in headings if h.level <= level]

    sections: List[dict] = []
    last_line_index = len(plain_lines) - 1

    def add_section(
        title: Optional[str],
        heading_level: Optional[int],
        start: int,
        end: int,
    ) -> None:
        """辅助函数，用于创建章节字典并写入列表。"""
        if start > end:
            return

        body_start = start if heading_level is None else start + 1
        if end < body_start:
            content = ""
        else:
            content = "".join(lines_with_endings[body_start : end + 1])

        sections.append(
            {
                "title": title,
                "level": heading_level,
                "content": content,
                "start_line": start,
                "end_line": end,
            }
        )

    if not split_heads:
        if plain_lines:
            add_section(title=None, heading_level=None, start=0, end=last_line_index)
        return sections

    first_start = split_heads[0].line_number
    if first_start > 0:
        add_section(title=None, heading_level=None, start=0, end=first_start - 1)

    for index, heading in enumerate(split_heads):
        if index + 1 < len(split_heads):
            end_line = split_heads[index + 1].line_number - 1
        else:
            end_line = last_line_index if last_line_index >= 0 else heading.line_number

        add_section(
            title=heading.title,
            heading_level=heading.level,
            start=heading.line_number,
            end=end_line,
        )

    return sections


def _sanitize_title(title: Optional[str]) -> str:
    """
    将章节标题转换为安全的文件名片段。

    空标题会使用 "untitled" 占位。对非字母数字字符统一替换为 "_"，并限制
    输出长度，方便批量写入文件系统。
    """
    if not title:
        return "untitled"

    safe = title.strip().replace(" ", "_")
    safe = re.sub(r"[^A-Za-z0-9_\-]+", "_", safe) or "untitled"
    return safe[:40]


def _write_sections_to_dir(
    sections: List[dict],
    output_dir: Path,
    original_lines: List[str],
    encoding: str,
) -> None:
    """
    将章节按顺序写入指定目录。

    每个文件包含原始标题行（如果存在）以及章节正文内容。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    total = len(sections)
    padding = max(2, len(str(total)))

    for index, section in enumerate(sections, start=1):
        safe_title = _sanitize_title(section["title"])
        filename = f"{str(index).zfill(padding)}_{safe_title}.md"
        heading_line = ""
        if section["level"] is not None and section["start_line"] < len(original_lines):
            heading_line = original_lines[section["start_line"]]
            if not heading_line.endswith(("\n", "\r")):
                heading_line += "\n"

        body = section["content"]
        content = heading_line + body
        (output_dir / filename).write_text(content, encoding=encoding)


def _print_sections_summary(sections: List[dict]) -> None:
    """将章节信息以易读的方式输出到终端。"""
    if not sections:
        print("未检测到任何符合条件的标题或章节。")
        return

    header = f"{'Idx':>3}  {'Lvl':>3}  {'Title':<30}  {'内容行数':>8}"
    print(header)
    print("-" * len(header))
    for idx, section in enumerate(sections, start=1):
        title = section["title"] or "(无标题)"
        level = section["level"] or 0
        line_count = len(section["content"].splitlines()) if section["content"] else 0
        print(f"{idx:>3}  {level:>3}  {title:<30.30}  {line_count:>8}")


def main(argv: Optional[List[str]] = None) -> None:
    """
    命令行入口，读取文件、拆分章节，并选择输出方式。

    - 若传入 --output-dir，则会将章节写入该目录，每个文件包含原始标题与正文。
    - 若未提供输出目录，则在终端打印统计信息，方便快速了解拆分结果。
    """
    parser = argparse.ArgumentParser(
        description="按指定标题级别拆分 Markdown 文件内容。"
    )
    parser.add_argument("input", help="需要拆分的 Markdown 文件路径")
    parser.add_argument(
        "--level",
        type=int,
        default=2,
        help="用于拆分的标题级别（默认: 2）",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="读取文件时使用的字符编码（默认: utf-8）",
    )
    parser.add_argument(
        "--output-dir",
        help="若提供，将章节写入该目录，每个章节一个文件",
    )

    args = parser.parse_args(argv)
    input_path = Path(args.input)
    text = input_path.read_text(encoding=args.encoding)
    sections = split_markdown(text, level=args.level)

    if args.output_dir:
        original_lines = text.splitlines(keepends=True)
        _write_sections_to_dir(
            sections=sections,
            output_dir=Path(args.output_dir),
            original_lines=original_lines,
            encoding=args.encoding,
        )
        print(f"已写入 {len(sections)} 个章节到 {args.output_dir}")
    else:
        _print_sections_summary(sections)


def _run_demo() -> None:
    """当直接运行脚本且未提供参数时，演示 split_markdown 的效果。"""
    demo_text = (
        "# 第一章 简介\n"
        "本段展示文档开头没有二级标题时的处理方式。\n"
        "\n"
        "## 第二章 概述\n"
        "这里是目标章节的正文。\n"
        "### 第二章 - 子节\n"
        "比拆分级别更深的标题会留在当前章节中。\n"
        "\n"
        "## 第三章 结语\n"
        "最后提供一个简单的结语示例。\n"
    )
    print("---- split_markdown 示例（level=2） ----")
    sections = split_markdown(demo_text, level=2)
    for section in sections:
        title = section['title'] or "(无标题)"
        print(
            f"标题: {title}, 级别: {section['level']}, "
            f"行范围: {section['start_line']}~{section['end_line']}"
        )
        print("内容:")
        print(section["content"] or "(空章节)")
        print("-" * 40)
    print("---- 示例结束，如需处理文件请提供命令行参数 ----")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _run_demo()
    else:
        main()
