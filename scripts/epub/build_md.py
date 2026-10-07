"""把 content/ 下的讲义合成一个 Markdown 文件：dist/<书名>.md"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_epub import ROOT, SUBTITLE, TITLE, assemble, chapter_titles  # noqa: E402


def main():
    titles, sections = chapter_titles()
    toc = []
    for ch in sorted(titles, key=lambda c: int(c.split('.')[1])):
        toc.append(f'- **{ch} {titles[ch]}**')
        toc += [f'  - {s}' for s in sections.get(ch, [])]
    head = f'# {TITLE}\n\n**{SUBTITLE}**\n\n## 目录\n\n' + '\n'.join(toc) + '\n\n---\n\n'
    # 正文里各章标题从 # 起，整体降一级，让书名独占一级标题
    body = '\n'.join(('#' + l if l.startswith('#') and not l.startswith('#######') else l) for l in assemble().splitlines())
    out = os.path.join(ROOT, 'dist', f'{TITLE}（v29）.md')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(head + body + '\n')
    print('wrote', out, os.path.getsize(out) // 1024, 'KB')


if __name__ == '__main__':
    main()
