# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-11-18
### Added
- Added `--h1-regex` CLI 参数与 `h1_regex` 函数参数，可用正则表达式描述允许的一级
  标题格式，满足“中文数字+顿号”等复杂场景。

## [0.2.0] - 2025-11-17
### Added
- Introduced `h1_prefixes` 支持与 `--h1-prefix` CLI 参数，可只拆分符合特定前缀的
  一级标题，避免教材注释类 `#` 被视作章节。
- 扩展 `split_markdown` 函数签名以接受上述前缀过滤，保持 CLI 与库调用的行为一致。

## [0.1.0] - 2025-11-16
### Added
- Introduced `split_markdown.py` with reusable `split_markdown` API、命令行接口和内置示例。
- Added beginner-friendly `README.md` 说明 CLI 和库调用方式。
### Fixed
- 修复围栏代码块中的 `#` 会被识别为章节标题的问题，确保拆分结果稳定。
