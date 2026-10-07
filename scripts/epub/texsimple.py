"""把简单的 TeX 公式转成 HTML 文本；遇到复杂结构返回 None（交给图片渲染）。"""
import html
import re

SYM = {
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ε', 'varepsilon': 'ε',
    'theta': 'θ', 'lambda': 'λ', 'mu': 'μ', 'pi': 'π', 'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ',
    'phi': 'φ', 'varphi': 'φ', 'omega': 'ω', 'Delta': 'Δ', 'Sigma': 'Σ', 'Pi': 'Π', 'Omega': 'Ω',
    'times': '×', 'cdot': '·', 'div': '÷', 'pm': '±', 'approx': '≈', 'le': '≤', 'leq': '≤',
    'ge': '≥', 'geq': '≥', 'neq': '≠', 'ne': '≠', 'to': '→', 'rightarrow': '→', 'Rightarrow': '⇒',
    'leftarrow': '←', 'infty': '∞', 'ldots': '…', 'cdots': '⋯', 'dots': '…', 'sim': '~',
    'propto': '∝', 'in': '∈', 'uparrow': '↑', 'downarrow': '↓', 'equiv': '≡', 'mid': '|',
    '%': '%', '$': '$', '&': '&', '#': '#', '_': '_', '{': '{', '}': '}',
    ',': ' ', ';': ' ', ':': ' ', '!': '', ' ': ' ', 'quad': ' ', 'qquad': '  ',
    'max': 'max', 'min': 'min', 'ln': 'ln', 'log': 'log', 'exp': 'exp', 'lim': 'lim',
    'left': '', 'right': '', 'big': '', 'Big': '', 'bigl': '', 'bigr': '', 'Bigl': '', 'Bigr': '',
}
TEXTCMD = {'text', 'textrm', 'mathrm', 'operatorname', 'textbf', 'mathbf', 'mathit', 'textit'}


class Complex(Exception):
    pass


def _group(s, i):
    """读取从 i 开始的一个参数（花括号组或单个记号），返回 (内容, 新位置)。"""
    while i < len(s) and s[i] == ' ':
        i += 1
    if i >= len(s):
        raise Complex
    if s[i] == '{':
        depth, j = 0, i
        while j < len(s):
            if s[j] == '\\':
                j += 2
                continue
            if s[j] == '{':
                depth += 1
            elif s[j] == '}':
                depth -= 1
                if depth == 0:
                    return s[i + 1:j], j + 1
            j += 1
        raise Complex
    if s[i] == '\\':
        m = re.match(r'\\([A-Za-z]+|.)', s[i:])
        return m.group(0), i + len(m.group(0))
    return s[i], i + 1


def conv(s, italic=True, depth=0):
    if depth > 3:
        raise Complex
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == '\\':
            m = re.match(r'\\([A-Za-z]+|.)', s[i:])
            name = m.group(1)
            i += len(m.group(0))
            if name in TEXTCMD:
                arg, i = _group(s, i)
                inner = conv(arg, italic=False, depth=depth + 1)
                out.append(f'<b>{inner}</b>' if name in ('textbf', 'mathbf') else inner)
            elif name in SYM:
                out.append(html.escape(SYM[name]))
            else:
                raise Complex
        elif c in '_^':
            arg, i = _group(s, i + 1)
            tag = 'sub' if c == '_' else 'sup'
            out.append(f'<{tag}>{conv(arg, italic, depth + 1)}</{tag}>')
        elif c in '{}':
            i += 1
        elif c == ' ' and italic:
            i += 1
        elif c == '~':
            out.append(' ')
            i += 1
        elif c.isalpha() and c.isascii() and italic:
            j = i
            while j < len(s) and s[j].isalpha() and s[j].isascii():
                j += 1
            word = s[i:j]
            # 多字母缩写（ROIC、WACC）用正体，单字母变量用斜体
            out.append(f'<i>{word}</i>' if len(word) == 1 else word)
            i = j
        elif c in '+-=<>':
            sym = {'-': '−'}.get(c, c)
            out.append(f' {html.escape(sym)} ' if c != '-' or (out and out[-1].strip()) else '−')
            i += 1
        else:
            out.append(html.escape(c))
            i += 1
    return ''.join(out)


def to_html(tex):
    try:
        return '<span class="m">' + conv(tex.strip()) + '</span>'
    except (Complex, AttributeError):
        return None
