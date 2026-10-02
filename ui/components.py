"""Componentes visuais reutilizáveis. Tudo que chega do usuário passa por esc()."""
import html

import numpy as np
import streamlit as st

from ui.theme import COLORS, rgb

# ícone de cada área, o mesmo usado na navegação lateral
PAGE_ICONS = {
    'Problema': 'description', 'Dados': 'table_view', 'Método': 'function', 'Análise': 'analytics',
    'Sensibilidade': 'tune', 'Sobre': 'info', 'Workspace': 'folder_open', 'Modelo incompleto': 'rule',
}


def esc(x):
    return html.escape(str(x))


def icon(name):
    """Ícone Material Symbols (mesma família usada nos widgets nativos)."""
    return f'<span class="mcda-ico" aria-hidden="true">{esc(name)}</span>'


def badge(text, tone=''):
    return f'<span class="mcda-badge {tone}">{esc(text)}</span>'


def method_tone(method):
    return 'promethee' if method == 'PROMETHEE II' else 'electre'


def page_header(where, title, lead=''):
    """Título da página. `where` identifica a área ('03 / Método', 'Workspace') e escolhe o ícone."""
    name = where.partition(' / ')[2] or where
    mark = icon(PAGE_ICONS[name]) if name in PAGE_ICONS else ''
    st.html(
        f'<div class="mcda-pagehead"><h1 class="mcda-title">{mark}<span>{esc(title)}</span></h1>'
        + (f'<div class="mcda-lead">{esc(lead)}</div>' if lead else '')
        + '</div>'
    )


def section(label, hint='', step=None):
    """Título de seção. `step` numera etapas quando o conteúdo é de fato uma sequência."""
    st.html(
        '<div class="mcda-section"><div class="mcda-section-head">'
        + (f'<span class="mcda-section-step">{esc(step)}</span>' if step else '')
        + f'<h2 class="mcda-section-label">{esc(label)}</h2></div>'
        + (f'<div class="mcda-section-hint">{esc(hint)}</div>' if hint else '')
        + '</div>'
    )


def panel(key, title='', hint=''):
    """Card padrão para gráficos, tabelas e grupos. Use com `with`.

    Ocupa toda a altura da linha, então dois cards lado a lado começam e terminam juntos.
    """
    box = st.container(border=True, key=f'panel_{key}', height='stretch')
    if title:
        box.html(
            f'<div class="mcda-panel-title">{esc(title)}</div>'
            + (f'<div class="mcda-panel-hint">{esc(hint)}</div>' if hint else '')
        )
    return box


def metric_strip(items):
    """Linha de cards de métrica. Cada item: (rótulo, valor, nota[, opções]).

    opções: 'accent' destaca o card principal; 'tone' ('success' | 'neutral') transforma a
    nota em selo; 'small' reduz o valor (textos longos); 'code' usa fonte de código.
    """
    cells = []
    for item in items:
        label, value, note = item[:3]
        opt = item[3] if len(item) > 3 else {}
        size = ' code' if opt.get('code') else ' small' if opt.get('small') else ''
        cells.append(
            f'<div class="mcda-metric {opt.get("tone", "")}{" accent" if opt.get("accent") else ""}">'
            f'<div class="mcda-metric-label">{esc(label)}</div>'
            f'<div class="mcda-metric-value{size}" title="{esc(value)}">{esc(value)}</div>'
            + (f'<div class="mcda-metric-note">{esc(note)}</div>' if note else '')
            + '</div>'
        )
    st.html(f'<div class="mcda-metrics">{"".join(cells)}</div>')


def callout(text, title='', tone=''):
    """Bloco de leitura. `text` pode conter <strong>; escape os trechos vindos do usuário antes."""
    mark = 'warning' if tone == 'warning' else 'lightbulb'
    st.html(
        f'<div class="mcda-callout {tone}">{icon(mark)}<div>'
        + (f'<div class="mcda-callout-title">{esc(title)}</div>' if title else '')
        + f'{text}</div></div>'
    )


def formula(lines):
    """Bloco monoespaçado. Linhas já devem estar escapadas (podem conter <span class="res">)."""
    st.html('<div class="mcda-formula">' + '<br>'.join(lines) + '</div>')


def steps(labels):
    """Sequência numerada de etapas, usada no login e nas páginas de método."""
    parts = []
    for i, label in enumerate(labels, 1):
        parts.append(f'<span class="mcda-step"><span class="mcda-step-n">{i}</span><span>{esc(label)}</span></span>')
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


def data_table(columns, rows, total=None, lead_rows=(), note='', compact=False):
    """Tabela densa somente leitura.

    columns: lista de (rótulo, classe) — classe 'r' alinha números à direita.
    rows: lista de linhas; a primeira célula vira cabeçalho de linha.
    total: linha de totalização opcional. lead_rows: índices a destacar.
    compact: células mais estreitas, para tabelas com muitas colunas.
    """
    head = ''.join(f'<th class="{cls}" scope="col">{esc(label)}</th>' for label, cls in columns)
    body = []
    for i, row in enumerate(rows):
        first = _td(row[0], 'th').replace('<th', '<th scope="row"', 1)
        body.append(f'<tr class="{"lead" if i in lead_rows else ""}">{first}{"".join(_td(c) for c in row[1:])}</tr>')
    if total:
        body.append(f'<tr class="total">{_td(total[0], "th")}{"".join(_td(c) for c in total[1:])}</tr>')
    st.html(
        f'<div class="mcda-table-wrap"><table class="mcda-table{" compact" if compact else ""}"><thead><tr>{head}</tr></thead>'
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
    tint = rgb(COLORS['primary'])
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
                alpha = 0.03 + 0.25 * (v - lo) / (hi - lo)
                style = f' style="background:rgba({tint},{alpha:.3f})"'
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
            f'<div class="mcda-rank{" first" if pos == 1 else ""}"><span class="mcda-rank-n">{pos}</span>'
            f'<span class="mcda-rank-name">{esc(name)}</span><span class="mcda-rank-val">{esc(value)}</span></div>'
        )
    st.html(''.join(out))


def footer():
    """Rodapé da página. O container com key='footer' é empurrado para o fim da tela pelo CSS."""
    with st.container(key='footer'):
        st.html(
            '<footer class="mcda-footer"><div class="mcda-footer-grid">'
            f'<div><div class="mcda-footer-brand"><span class="mcda-brand-mark">{icon("query_stats")}</span>MCDA Lab</div>'
            '<div class="mcda-footer-desc">Laboratório didático de Apoio Multicritério à Decisão.</div></div>'
            '<div><div class="mcda-footer-head">Métodos</div><ul><li>PROMETHEE II</li><li>ELECTRE I</li></ul></div>'
            '<div><div class="mcda-footer-head">Autoria</div><ul><li>Laert Costa</li><li>Felipe Pires</li></ul></div>'
            '<div><div class="mcda-footer-head">Instituição</div><ul><li>UFMS</li><li>2026</li></ul></div>'
            '</div><div class="mcda-footer-note">'
            '<span>Ferramenta didática de uso acadêmico. Os resultados dependem dos dados, pesos, parâmetros e limiares definidos pelo '
            'usuário. O sistema apoia a análise e não substitui o julgamento do decisor.</span>'
            '</div></footer>'
        )
