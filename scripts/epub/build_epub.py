"""把 content/ 下的讲义合成一本 EPUB。

用法（在仓库根目录）:
    npm install --prefix <MJ目录> mathjax-full@3      # 只需一次
    MJ_DIR=<MJ目录> python3 -I scripts/epub/build_epub.py

依赖：pandoc（3.x）、node、playwright 全局模块和 Chromium。
简单公式直接转成 HTML 文本；复杂公式（分数、求和、根号、行间公式）用 MathJax 渲染后截成 PNG。
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from texsimple import to_html  # noqa: E402

BUILD = os.path.join(ROOT, 'build')
MATH_DIR = os.path.join(BUILD, 'math')
OUT = os.path.join(ROOT, 'dist', '投资体系 v29 · 第5章 估值体系.epub')

TITLE = '投资体系 v29 · 第5章 估值体系'
SUBTITLE = '估值：它值多少钱，价格贵不贵（讲义版）'


def node_key(path):
    name = os.path.basename(path)
    m = re.match(r'(\d+(?:\.\d+)+)([a-c]?)', name)
    return [int(x) for x in m.group(1).split('.')] + [m.group(2)]


def chapter_titles():
    titles, sections = {}, {}
    for line in open(os.path.join(ROOT, 'framework', 'outline-v29.md'), encoding='utf-8'):
        m = re.match(r'^## (5\.\d) (.+)$', line.strip())
        if m:
            titles[m.group(1)] = m.group(2)
        m = re.match(r'^### ((5\.\d)\.\d+) (.+)$', line.strip())
        if m:
            title = re.sub(r'\s*\[[^\]]*\]\s*$', '', m.group(3))
            sections.setdefault(m.group(2), []).append(f'{m.group(1)} {title}')
    return titles, sections


def demote(md):
    """所有标题降一级；代码块里的内容不动；去掉 HTML 注释（出处备查）。"""
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    out, fence = [], False
    for line in md.splitlines():
        if line.lstrip().startswith('```'):
            fence = not fence
        if not fence and re.match(r'^#{1,5} ', line):
            line = '#' + line
        out.append(line)
    return '\n'.join(out).strip() + '\n'


def assemble():
    titles, sections = chapter_titles()
    parts = []
    for d in sorted(glob.glob(os.path.join(ROOT, 'content', '5.*')), key=lambda p: [int(x) for x in re.match(r'.*/(5\.\d)', p).group(1).split('.')]):
        ch = re.match(r'.*/(5\.\d)', d).group(1)
        intro = '\n'.join(f'- {t}' for t in sections.get(ch, []))
        parts.append(f'# {ch} {titles[ch]}\n\n本节包括：\n\n{intro}\n')
        for f in sorted(glob.glob(os.path.join(d, '*.md')), key=node_key):
            parts.append(demote(open(f, encoding='utf-8').read()))
    return '\n\n'.join(parts)


def walk(x, fn):
    if isinstance(x, list):
        return [walk(i, fn) for i in x]
    if isinstance(x, dict):
        r = fn(x)
        if r is not None:
            return r
        return {k: walk(v, fn) for k, v in x.items()}
    return x


def main():
    os.makedirs(MATH_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    md = assemble()
    open(os.path.join(BUILD, 'book.md'), 'w', encoding='utf-8').write(md)
    doc = json.loads(subprocess.run(['pandoc', '-f', 'markdown', '-t', 'json', os.path.join(BUILD, 'book.md')],
                                    capture_output=True, check=True).stdout)

    complex_items = {}

    def collect(node):
        if node.get('t') == 'Math':
            kind, tex = node['c'][0]['t'], node['c'][1]
            display = kind == 'DisplayMath'
            if to_html(tex) is None:
                fid = 'm' + hashlib.md5((kind + tex).encode()).hexdigest()[:12]
                complex_items[fid] = {'id': fid, 'tex': tex, 'display': display}
        return None

    walk(doc, collect)
    todo = [it for it in complex_items.values() if not os.path.exists(os.path.join(MATH_DIR, it['id'] + '.png'))]
    meta_path = os.path.join(MATH_DIR, 'meta.json')
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    if todo:
        tmp = os.path.join(BUILD, 'todo.json')
        json.dump(todo, open(tmp, 'w'), ensure_ascii=False)
        tmpdir = os.path.join(BUILD, 'math_new')
        subprocess.run(['node', os.path.join(HERE, 'render.mjs'), tmp, tmpdir], check=True)
        meta.update(json.load(open(os.path.join(tmpdir, 'meta.json'))))
        for f in os.listdir(tmpdir):
            if f.endswith('.png'):
                os.replace(os.path.join(tmpdir, f), os.path.join(MATH_DIR, f))
        json.dump(meta, open(meta_path, 'w'))
    print(f'complex formulas: {len(complex_items)} (newly rendered {len(todo)})')

    def ex(v):
        return float(re.sub(r'[^0-9.\-]', '', v or '0') or 0)

    def replace(node):
        if node.get('t') != 'Math':
            return None
        kind, tex = node['c'][0]['t'], node['c'][1]
        display = kind == 'DisplayMath'
        h = to_html(tex)
        if h is not None:
            if display:
                h = h.replace('class="m"', 'class="m dm"')
            return {'t': 'RawInline', 'c': ['html', h]}
        fid = 'm' + hashlib.md5((kind + tex).encode()).hexdigest()[:12]
        m = meta[fid]
        va = re.search(r'vertical-align:\s*(-?[0-9.]+)ex', m['style'])
        # 1ex ≈ 0.5em；截图四周各留 2px（约 0.125em）
        height = ex(m['height']) * 0.5 + 0.25
        valign = (float(va.group(1)) * 0.5 - 0.125) if va else -0.125
        style = f'height:{height:.3f}em' if display else f'height:{height:.3f}em;vertical-align:{valign:.3f}em'
        cls = 'dmath' if display else 'imath'
        return {'t': 'Image', 'c': [['', [cls], [['style', style]]], [{'t': 'Str', 'c': tex}],
                                    [os.path.join(MATH_DIR, fid + '.png'), '']]}

    doc = walk(doc, replace)
    jpath = os.path.join(BUILD, 'book.json')
    json.dump(doc, open(jpath, 'w', encoding='utf-8'), ensure_ascii=False)
    meta_yaml = os.path.join(BUILD, 'meta.yaml')
    open(meta_yaml, 'w', encoding='utf-8').write(
        f'---\ntitle: "{TITLE}"\nsubtitle: "{SUBTITLE}"\nlang: zh-CN\ntoc-title: "目录"\n'
        'description: "以价值评估为骨架、整合科勒《价值评估》与达摩达兰《投资估价》的个人估值讲义"\n---\n')
    subprocess.run([
        'pandoc', jpath, '-f', 'json', '-t', 'epub3', '-o', OUT,
        '--metadata-file', meta_yaml,
        '--epub-cover-image', os.path.join(ROOT, 'assets', 'cover.jpg'),
        '--css', os.path.join(HERE, 'style.css'),
        '--toc', '--toc-depth=3', '--split-level=2',
        '--resource-path', ROOT,
    ], check=True)
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()
