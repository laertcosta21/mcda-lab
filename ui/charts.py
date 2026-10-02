"""Gráficos ECharts no padrão do design system. Cada função monta `options` e renderiza."""
import math

from ui.theme import CHART_SERIES, COLORS, FONTS, HEIGHTS, TYPE

_TEXT = {'fontFamily': FONTS['sans'], 'fontSize': TYPE['sm'], 'color': COLORS['ink-2']}
_MONO = {'fontFamily': FONTS['mono'], 'fontSize': TYPE['xs'], 'color': COLORS['muted']}
_AXIS_LINE = {'lineStyle': {'color': COLORS['line-strong']}}
_SPLIT = {'lineStyle': {'color': COLORS['line']}}
_TOOLTIP = {
    'backgroundColor': COLORS['surface'], 'borderColor': COLORS['line-strong'], 'borderWidth': 1,
    'textStyle': {'fontFamily': FONTS['sans'], 'fontSize': TYPE['sm'], 'color': COLORS['ink']},
    'extraCssText': 'box-shadow:0 6px 20px rgba(24,36,42,.08);border-radius:6px;',
}
_SYMBOLS = ['circle', 'rect', 'triangle', 'diamond', 'roundRect', 'pin', 'arrow', 'circle']


def _render(options, height, key):
    # o componente só pode ser registrado dentro do runtime do Streamlit; importar aqui
    # mantém ui.charts importável em testes e scripts.
    from streamlit_echarts import JsCode, st_echarts
    options.setdefault('textStyle', _TEXT)
    options.setdefault('backgroundColor', 'transparent')
    options.setdefault('animationDuration', 300)
    if options.get('tooltip', {}).pop('_fixed4', False):
        options['tooltip']['valueFormatter'] = JsCode("function(v){return typeof v==='number'?v.toFixed(4):v}")
    st_echarts(options=options, height=f'{height}px', key=key)


def net_flow_bar(names, phi, key):
    """Barras horizontais do fluxo líquido φ, da maior para a menor, divergindo em zero."""
    order = sorted(range(len(names)), key=lambda i: phi[i])
    best = max(phi)
    span = max(max(abs(float(v)) for v in phi), .05) * 1.4  # folga simétrica para os rótulos não invadirem os nomes
    data = []
    for i in order:
        v = float(phi[i])
        color = COLORS['primary'] if v == best else (COLORS['secondary'] if v >= 0 else COLORS['faint'])
        data.append({
            'value': round(v, 6),
            'itemStyle': {'color': color, 'borderRadius': 2},
            'label': {'show': True, 'position': 'right' if v >= 0 else 'left', 'formatter': f'{v:+.4f}', **_MONO, 'color': COLORS['ink-2']},
        })
    _render({
        'grid': {'left': 8, 'right': 16, 'top': 12, 'bottom': 8, 'containLabel': True},
        'tooltip': {**_TOOLTIP, 'trigger': 'item', '_fixed4': True},
        'xAxis': {'type': 'value', 'min': -round(span, 2), 'max': round(span, 2), 'axisLabel': {**_MONO, 'hideOverlap': True}, 'splitLine': _SPLIT,
                  'axisLine': {'show': False}},
        'yAxis': {'type': 'category', 'data': [names[i] for i in order], 'axisLabel': {**_TEXT, 'color': COLORS['ink']},
                  'axisTick': {'show': False}, 'axisLine': _AXIS_LINE},
        'series': [{
            'type': 'bar', 'name': 'φ', 'data': data, 'barMaxWidth': 22,
            'markLine': {'silent': True, 'symbol': 'none', 'label': {'show': False},
                         'lineStyle': {'color': COLORS['ink-2'], 'type': 'solid', 'width': 1}, 'data': [{'xAxis': 0}]},
        }],
    }, HEIGHTS['chart'], key)


def sensitivity_lines(weights, series, original, crossings, x_label, key):
    """φ de cada alternativa ao longo do peso testado, com o peso original e as trocas marcados.

    series: lista de (nome, [φ por peso]). crossings: pesos em que há troca de posição.
    """
    lo, hi = float(min(weights)), float(max(weights))
    marks = []
    if lo <= original <= hi:
        marks.append({'xAxis': round(original, 6), 'lineStyle': {'color': COLORS['ink'], 'type': 'dashed', 'width': 1.5},
                      'label': {'formatter': 'peso original', 'position': 'end', **_TEXT, 'fontSize': TYPE['xs'], 'color': COLORS['ink']}})
    for w in crossings:
        marks.append({'xAxis': round(w, 6), 'lineStyle': {'color': COLORS['warning'], 'type': 'dotted', 'width': 1.5},
                      'label': {'formatter': 'troca', 'position': 'end', **_TEXT, 'fontSize': TYPE['xs'], 'color': COLORS['warning']}})
    out = []
    for i, (name, values) in enumerate(series):
        s = {
            'type': 'line', 'name': name, 'data': [[round(float(w), 6), round(float(v), 6)] for w, v in zip(weights, values)],
            'symbol': _SYMBOLS[i % len(_SYMBOLS)], 'symbolSize': 6, 'lineStyle': {'width': 2},
            'emphasis': {'focus': 'series'},
        }
        if i == 0 and marks:
            s['markLine'] = {'silent': True, 'symbol': 'none', 'data': marks}
        out.append(s)
    _render({
        'color': CHART_SERIES,
        'grid': {'left': 8, 'right': 32, 'top': 64, 'bottom': 32, 'containLabel': True},
        'legend': {'top': 0, 'left': 0, 'icon': 'roundRect', 'itemWidth': 12, 'itemHeight': 4, 'textStyle': _TEXT},
        'tooltip': {**_TOOLTIP, 'trigger': 'axis', '_fixed4': True},
        'xAxis': {'type': 'value', 'min': round(lo, 4), 'max': round(hi, 4), 'name': x_label, 'nameLocation': 'middle', 'nameGap': 28,
                  'nameTextStyle': _TEXT, 'axisLabel': _MONO, 'axisLine': _AXIS_LINE, 'splitLine': {'show': False}},
        'yAxis': {'type': 'value', 'name': 'φ', 'nameGap': 24, 'nameTextStyle': _TEXT, 'axisLabel': _MONO, 'splitLine': _SPLIT, 'scale': True},
        'series': out,
    }, HEIGHTS['chart-lg'], key)


def outranking_graph(names, R, kernel_nodes, key):
    """Grafo dirigido de sobreclassificação; nós do kernel aparecem preenchidos."""
    n = len(names)
    nodes = []
    for i, name in enumerate(names):
        ang = 2 * math.pi * i / max(n, 1) - math.pi / 2
        x, y = math.cos(ang), math.sin(ang)
        pos = 'top' if y < -.5 else 'bottom' if y > .5 else 'right' if x > 0 else 'left'
        in_kernel = i in kernel_nodes
        nodes.append({
            'id': str(i), 'name': name, 'x': x * 100, 'y': y * 100, 'symbolSize': 26,
            'itemStyle': {'color': COLORS['primary'] if in_kernel else COLORS['surface'],
                          'borderColor': COLORS['primary'] if in_kernel else COLORS['secondary'], 'borderWidth': 1.5},
            'label': {'show': True, 'position': pos, 'distance': 8, **_TEXT, 'color': COLORS['ink'], 'fontWeight': 600 if in_kernel else 500},
        })
    links = []
    for a in range(n):
        for b in range(n):
            if R[a][b]:
                links.append({'source': str(a), 'target': str(b), 'lineStyle': {'curveness': .18 if R[b][a] else 0}})
    _render({
        'tooltip': {**_TOOLTIP, 'show': False},
        'series': [{
            'type': 'graph', 'layout': 'none', 'data': nodes, 'links': links, 'roam': False,
            'zoom': .72,
            'edgeSymbol': ['none', 'arrow'], 'edgeSymbolSize': 9,
            'lineStyle': {'color': COLORS['secondary'], 'width': 1.5, 'opacity': 1},
            'emphasis': {'focus': 'adjacency', 'lineStyle': {'width': 2.5}},
        }],
    }, HEIGHTS['chart'], key)


def threshold_heatmap(c_values, d_values, arcs, current, key):
    """Número de relações aSb para cada combinação de limiares; a combinação atual fica contornada.

    arcs: dict {(i_c, i_d): relações}. current: (i_c, i_d) dos limiares do exercício.
    """
    top = max(arcs.values()) if arcs else 0
    data = []
    for (i, j), v in arcs.items():
        dark = top > 0 and v / top > .55
        data.append({'value': [i, j, v], 'label': {'color': COLORS['surface'] if dark else COLORS['ink']}})
    # a célula atual vai numa série própria, desenhada por cima, para o contorno não ser coberto pelas vizinhas
    here = [d for d in data if tuple(d['value'][:2]) == current]
    label = {'show': True, 'fontFamily': FONTS['mono'], 'fontSize': TYPE['sm'], 'fontWeight': 600}
    axis = {'type': 'category', 'axisLabel': _MONO, 'axisTick': {'show': False}, 'axisLine': _AXIS_LINE,
            'splitArea': {'show': False}, 'nameLocation': 'middle', 'nameTextStyle': _TEXT}
    _render({
        'grid': {'left': 48, 'right': 16, 'top': 12, 'bottom': 44, 'containLabel': True},
        'tooltip': {**_TOOLTIP, 'show': False},
        'xAxis': {**axis, 'data': [f'{v:.2f}' for v in c_values], 'name': 'limiar de concordância c′', 'nameGap': 30},
        'yAxis': {**axis, 'data': [f'{v:.2f}' for v in d_values], 'name': 'limiar de discordância d′', 'nameGap': 44},
        'visualMap': {'show': False, 'min': 0, 'max': max(top, 1), 'inRange': {'color': [COLORS['sunken'], COLORS['primary']]}},
        'series': [
            {'type': 'heatmap', 'data': data, 'label': label, 'itemStyle': {'borderColor': COLORS['surface'], 'borderWidth': 2},
             'emphasis': {'disabled': True}},
            {'type': 'heatmap', 'data': here, 'label': label, 'itemStyle': {'borderColor': COLORS['ink'], 'borderWidth': 2},
             'emphasis': {'disabled': True}},
        ],
    }, HEIGHTS['chart'], key)
