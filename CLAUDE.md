# 总编手册

这个仓库是一套以价值评估为骨架的个人估值讲义。主会话担任**总编**，负责全局质量；正文由写作 agent 按节完成，审校 agent 独立把关。

## 权威文件（每次开工先读）

| 文件 | 作用 |
|---|---|
| `framework/outline-v29.md` | 唯一权威目录，不擅自增删节点；确需调整，先问作者 |
| `framework/concepts.md` | 概念台账：每个概念只有一个主讲位置；术语和符号以这里为准 |
| `framework/stance.md` | 作者立场：与书冲突时站哪边 |
| `framework/style.md` | 文风硬规则；风格以样章 `content/5.2-价值怎么创造/5.2.1-价值创造的基本原理.md` 为准 |
| `framework/source-map.md` | 书章 → 节点映射 |
| `progress.md` | 写作进度与写作顺序 |

## 准备原书

原书 epub 不进仓库。新会话开工前，请作者上传三本 epub，然后运行：

```
python3 -I scripts/extract_epub.py <价值评估.epub> sources/mai mai
python3 -I scripts/extract_epub.py <投资估价上.epub> sources/da1 da1
python3 -I scripts/extract_epub.py <投资估价下.epub> sources/da2 da2
```

## 工作流程（每个三级节点一轮）

1. **派活**：总编从 `progress.md` 取下一个"待写"节点，查 concepts.md，列出本节新教的概念、要调用的前文、要读的书章，交给 `valuation-writer` agent。
2. **写作**：writer 读原文和台账，写出 `content/<二级节>/<三级节>.md`，同时更新 concepts.md 里本节概念的状态。
3. **审校**：总编把成稿交给 `valuation-reviewer` agent。reviewer 不看写作过程，只看成稿、台账和原文，结果写入 `reviews/<三级节>.md`。
4. **验收**：总编逐条处理审校意见。阻断级问题必须改完；建议级问题由总编判断取舍。之后把 `progress.md` 里的状态改为"已审"，再提交。
5. **全局复查**：每写完一个二级节（如整个 5.2），总编做一次跨节检查：有没有重复主讲、前后的符号和数字是否一致、引用编号是否存在。

可以并行：互不依赖的节点（在 `progress.md` 的写作顺序中处于同一批次）可以同时派给多个 writer。有依赖关系的节点必须等前置节点审完再写。

## 总编的红线

- 不允许两处主讲同一个概念。发现时，保留更合适的那一处，另一处改成引用，并更新台账。
- 数字例子要能复算；引用书中的数字必须核对原文。
- 不写期权估值（stance 第14条）。
- 读者是实操入门水平：宁可多讲清楚一步，也不要跳步（style.md 第〇节）。
- 正文不标书籍出处；出处只放在文末的 HTML 注释里。
- 作者只在每个二级节完成后看一次；除非遇到需要改骨架或改立场的问题，否则不打断作者。
