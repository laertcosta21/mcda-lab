"""Componentes visuais reutilizáveis. Tudo que chega do usuário passa por esc()."""
import html

import numpy as np
import streamlit as st


def esc(x):
    return html.escape(str(x))


def icon(name):
    """Ícone Material Symbols (mesma família usada nos widgets nativos)."""
    return f'<span class="mcda-ico" aria-hidden="true">{esc(name)}</span>'


def badge(text, tone=''):
    return f'<span class="mcda-badge {tone}">{esc(text)}</span>'


def method_tone(method):
    return 'promethee' if method == 'PROMETHEE II' else 'electre'


def page_header(kicker, title, lead=''):
    num, _, name = kicker.partition(' / ')
    eyebrow = f'<span class="num">{esc(num)}</span> · {esc(name)}' if name else esc(kicker)
    st.html(
        f'<div class="mcda-pagehead"><div class="mcda-eyebrow">{eyebrow}</div>'
        f'<h1 class="mcda-title">{esc(title)}</h1>'
        + (f'<div class="mcda-lead">{esc(lead)}</div>' if lead else '')
        + '</div>'
    )


def section(label, hint='', step=None):
    st.html(
        '<div class="mcda-section">'
        + (f'<span class="mcda-section-step">{esc(step)}</span>' if step else '')
        + f'<span class="mcda-section-label">{esc(label)}</span>'
        + (f'<span class="mcda-section-hint">{esc(hint)}</span>' if hint else '')
        + '</div>'
    )


def panel(key, title='', hint=''):
    """Superfície branca com borda para gráficos e grupos. Use com `with`."""
    box = st.container(border=True, key=f'panel_{key}')
    if title:
        box.html(
            f'<div class="mcda-panel-title">{esc(title)}</div>'
            + (f'<div class="mcda-panel-hint">{esc(hint)}</div>' if hint else '')
        )
    return box


def metric_strip(items):
    """Faixa compacta de indicadores. Cada item: (rótulo, valor, nota[, opções]).

    opções: {'mono': bool, 'tone': 'success' | 'neutral', 'plain': bool}
    `plain` desliga as maiúsculas do rótulo, para notação (φ, S(a,b)) e nomes.
    """
    cells = []
    for item in items:
        label, value, note = item[:3]
        opt = item[3] if len(item) > 3 else {}
        cells.append(
            f'<div class="mcda-metric {opt.get("tone", "")}">'
            f'<div class="mcda-metric-label{" plain" if opt.get("plain") else ""}">{esc(label)}</div>'
            f'<div class="mcda-metric-value{" mono" if opt.get("mono") else ""}">{esc(value)}</div>'
            + (f'<div class="mcda-metric-note">{esc(note)}</div>' if note else '')
            + '</div>'
        )
    st.html(f'<div class="mcda-metrics">{"".join(cells)}</div>')


def callout(text, title='', tone=''):
    """`text` pode conter <strong>; escape os trechos vindos do usuário antes."""
    st.html(
        f'<div class="mcda-callout {tone}">'
        + (f'<div class="mcda-callout-title">{esc(title)}</div>' if title else '')
        + f'{text}</div>'
    )


def formula(lines):
    """Bloco monoespaçado. Linhas já devem estar escapadas (podem conter <span class="res">)."""
    st.html('<div class="mcda-formula">' + '<br>'.join(lines) + '</div>')


def steps(labels):
    """Sequência numerada de etapas, usada no login e nas páginas de método."""
    parts = []
    for i, label in enumerate(labels, 1):
        parts.append(f'<span class="mcda-step"><span class="mcda-step-n">{i:02d}</span>{esc(label)}</span>')
    sep = '<span class="mcda-step-sep" aria-hidden="true"></span>'
    return f'<div class="mcda-steps">{sep.join(parts)}</div>'


def cell(value, cls=''):
    """Célula de tabela com classes: r (direita), c (centro), num, dim, strong, hit."""
    return {'v': value, 'cls': cls}


def _td(c, tag='td'):
    if isinstance(c, dict):
        style = f' style="{c["style"]}"' if c.get('style') else ''
        return f'<{tag} class="{c.get("cls", "")}"{style}>{esc(c["v"])}</{tag}>'
    return f'<{tag}>{esc(c)}</{tag}>'


def data_table(columns, rows, total=None, lead_rows=(), note=''):
    """Tabela densa somente leitura.

    columns: lista de (rótulo, classe) — classe 'r' alinha números à direita.
    rows: lista de linhas; a primeira célula vira cabeçalho de linha.
    total: linha de totalização opcional. lead_rows: índices a destacar.
    """
    head = ''.join(f'<th class="{cls}" scope="col">{esc(label)}</th>' for label, cls in columns)
    body = []
    for i, row in enumerate(rows):
        first = _td(row[0], 'th').replace('<th', '<th scope="row"', 1)
        body.append(f'<tr class="{"lead" if i in lead_rows else ""}">{first}{"".join(_td(c) for c in row[1:])}</tr>')
    if total:
        body.append(f'<tr class="total">{_td(total[0], "th")}{"".join(_td(c) for c in total[1:])}</tr>')
    st.html(
        f'<div class="mcda-table-wrap"><table class="mcda-table"><thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div>'
        + (f'<div class="mcda-table-note">{esc(note)}</div>' if note else '')
    )


def matrix_table(M, names, fmt='{:.4f}', heat=True, mark=None, corner='a \\ b', note=''):
    """Matriz alternativa × alternativa com tinta proporcional ao valor.

    mark: matriz booleana opcional; células marcadas ganham ênfase tipográfica.
    """
    M = np.asarray(M, dtype=float)
    off = M[~np.eye(len(M), dtype=bool)] if len(M) > 1 else M.ravel()
    lo, hi = (float(off.min()), float(off.max())) if off.size else (0.0, 0.0)
    head = f'<th scope="col">{esc(corner)}</th>' + ''.join(f'<th class="r" scope="col">{esc(n)}</th>' for n in names)
    body = []
    for i, name in enumerate(names):
        tds = []
        for j in range(len(names)):
            if i == j:
                tds.append('<td class="num dim">—</td>')
                continue
            v = M[i, j]
            style = ''
            if heat and hi > lo:
                alpha = 0.03 + 0.22 * (v - lo) / (hi - lo)
                style = f' style="background:rgba(27,90,114,{alpha:.3f})"'
            cls = 'num hit' if mark is not None and mark[i][j] else 'num'
            tds.append(f'<td class="{cls}"{style}>{esc(fmt.format(v))}</td>')
        body.append(f'<tr><th scope="row">{esc(name)}</th>{"".join(tds)}</tr>')
    st.html(
        f'<div class="mcda-table-wrap"><table class="mcda-table matrix"><thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div>'
        + (f'<div class="mcda-table-note">{esc(note)}</div>' if note else '')
    )


def rank_list(rows):
    """rows: lista de (posição, nome, valor formatado)."""
    out = []
    for pos, name, value in rows:
        out.append(
            f'<div class="mcda-rank{" first" if pos == 1 else ""}"><span class="mcda-rank-n">{pos:02d}</span>'
            f'<span class="mcda-rank-name">{esc(name)}</span><span class="mcda-rank-val">{esc(value)}</span></div>'
        )
    st.html(''.join(out))


def footer():
    st.html(
        '<div class="mcda-footer">'
        '<span><strong>MCDA Lab</strong> · Laboratório didático de Apoio Multicritério à Decisão</span>'
        '<span>UFMS · 2026 · Laert Costa · Felipe Pires · PROMETHEE II · ELECTRE I · Uso acadêmico</span>'
        '<span class="mcda-footer-note">Ferramenta didática: os resultados dependem dos dados, pesos, parâmetros e limiares '
        'definidos pelo usuário. O sistema apoia a análise e não substitui o julgamento do decisor.</span>'
        '</div>'
    )
