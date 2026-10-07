"""把 epub 按章节拆成纯文本，供写作/审校 agent 读取。

用法: python3 -I scripts/extract_epub.py <book.epub> <输出目录> <书代号>
例:   python3 -I scripts/extract_epub.py 价值评估.epub sources/mai mai
输出: <输出目录>/<书代号>-NN-<章标题>.txt，以及 index.txt（章节号 / 字数 / 文件名）
原书有版权，sources/ 已加入 .gitignore，不进仓库。
"""
import html
import re
import sys
import zipfile


def to_text(raw):
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw, flags=re.S)
    t = re.sub(r'<(h[1-6])[^>]*>', lambda m: '\n' + '#' * int(m.group(1)[1]) + ' ', t)
    t = re.sub(r'<(p|li|br|tr|div|h[1-6])[^>]*>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\n\s*\n+', '\n\n', html.unescape(t)).strip()


def main(epub, outdir, code):
    import os
    os.makedirs(outdir, exist_ok=True)
    z = zipfile.ZipFile(epub)
    opf = next(n for n in z.namelist() if n.endswith('.opf'))
    base = opf.rsplit('/', 1)[0] + '/' if '/' in opf else ''
    o = z.read(opf).decode('utf-8', 'replace')
    items = dict(re.findall(r'<item[^>]*id="([^"]+)"[^>]*href="([^"]+)"', o))
    items.update({i: h for h, i in re.findall(r'<item[^>]*href="([^"]+)"[^>]*id="([^"]+)"', o)})
    index = []
    for n, idref in enumerate(re.findall(r'<itemref[^>]*idref="([^"]+)"', o)):
        href = items.get(idref, '')
        if not href.endswith('html'):
            continue
        text = to_text(z.read(base + href).decode('utf-8', 'replace'))
        if len(text) < 200:
            continue
        title = re.sub(r'^#+\s*', '', next((l for l in text.splitlines() if l.strip()), ''))[:30]
        safe = re.sub(r'[\\/:*?"<>|\s]+', '_', title)
        name = f'{code}-{n:02d}-{safe}.txt'
        open(f'{outdir}/{name}', 'w', encoding='utf-8').write(text + '\n')
        index.append(f'{n:02d}\t{len(text)}\t{name}')
    open(f'{outdir}/index.txt', 'w', encoding='utf-8').write('\n'.join(index) + '\n')
    print('\n'.join(index))


if __name__ == '__main__':
    main(*sys.argv[1:4])
