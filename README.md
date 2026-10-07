# 估值体系

以价值评估为骨架的个人估值讲义。素材来自三本书：科勒《价值评估》第4版［麦］、达摩达兰《投资估价》第3版上下册［达］，再加上我自己的整合［自］。

## 目录

| 位置 | 内容 |
|---|---|
| [`framework/outline-v29.md`](framework/outline-v29.md) | 骨架（当前版本）；[v28 原版](framework/outline-v28.md)，[编号映射](framework/v28-to-v29.md) |
| [`framework/concepts.md`](framework/concepts.md) | 概念台账：每个概念的唯一主讲位置、术语对照 |
| [`framework/stance.md`](framework/stance.md) | 作者立场 |
| [`framework/style.md`](framework/style.md) | 文风规则 |
| [`framework/source-map.md`](framework/source-map.md) | 书章 → 节点映射 |
| [`content/`](content/) | 讲义正文 |
| [`reviews/`](reviews/) | 审校记录 |
| [`progress.md`](progress.md) | 写作进度 |
| [`CLAUDE.md`](CLAUDE.md) | 总编手册：写作流程和质量红线 |
| [`docs/整理方案.md`](docs/整理方案.md) | 为什么这样组织 |

## 准备原书

原书不进仓库。把 epub 放到本地后运行 `scripts/extract_epub.py`（用法见 CLAUDE.md），会把书按章拆成文本，放到 `sources/`（已被 gitignore）。

## 生成 EPUB

成书在 [`dist/`](dist/)（EPUB 和单文件 Markdown，后者用 `python3 -I scripts/epub/build_md.py` 生成）。内容修改后重新生成：

```
npm install --prefix <某个目录> mathjax-full@3     # 只需一次
MJ_DIR=<那个目录> python3 -I scripts/epub/build_epub.py
```

需要 pandoc 3.x、node 和 Playwright/Chromium。简单公式会转成文字，复杂公式由 MathJax 渲染成图片。封面是 `assets/cover.jpg`。
