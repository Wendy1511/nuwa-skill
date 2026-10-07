"""把 framework/outline-v29.md 转成目录树格式（与 v28 的框架树文件同一格式）。"""
import re
import sys

src, out, title = sys.argv[1], sys.argv[2], sys.argv[3]
nodes = [('5', '估值：它值多少钱，价格贵不贵')]
for line in open(src, encoding='utf-8'):
    m = re.match(r'^\s*(?:#+|-)\s+(\d+(?:\.\d+)+)\s+(.*)$', line)
    if m:
        nodes.append((m.group(1), m.group(2).strip()))
kids = {}
for num, _ in nodes[1:]:
    kids.setdefault(num.rsplit('.', 1)[0], []).append(num)
name = dict(nodes)
lines = []


def walk(num, prefix, last, top=False):
    lines.append(f'{prefix}{"└── " if last else "├── "}{num} {name[num]}/')
    ch = kids.get(num, [])
    for i, c in enumerate(ch):
        walk(c, prefix + ('    ' if last else '│   '), i == len(ch) - 1)


walk('5', '', False)
open(out, 'w', encoding='utf-8').write(f'# {title}\n\n```text\n' + '\n'.join(lines) + '\n```\n')
print(len(lines), 'lines')
