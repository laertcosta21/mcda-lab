import numpy as np
import streamlit as st

from core.explain import leaders, rank_changes
from engine.electre import sensitivity as esens
from engine.promethee import sensitivity as psens
from ui import charts
from ui.components import callout, cell, data_table, esc, metric_strip, page_header, panel, section

_NOT_RANK_REVERSAL = ('Esta análise varia apenas pesos, com as mesmas alternativas. Ela não trata de rank reversal, '
                      'que é a mudança de ordem causada por incluir ou remover alternativas.')


def promethee(data):
    A = data['alternatives']; C = data['criteria']; X = np.array(data['matrix'])
    page_header('05 / Sensibilidade', 'O ranking permanece estável quando os pesos mudam?',
                'Varie o peso de um critério e observe como os fluxos líquidos e as posições respondem. Os demais pesos são reajustados proporcionalmente.')
    if len(C) < 2:
        st.info('A análise de sensibilidade de pesos precisa de pelo menos 2 critérios.', icon=':material/info:'); return

    c1, c2 = st.columns([1, 2], gap='medium')
    idx = c1.selectbox('Critério a variar', range(len(C)), format_func=lambda i: C[i]['name'])
    lo, hi = c2.slider('Intervalo de peso testado', 0., 1., (0.05, 0.80), .05)
    vals = np.linspace(lo, hi, 16); sd = psens(X, C, idx, vals)
    name = C[idx]['name']
    total = sum(float(c['weight']) for c in C)
    original = float(C[idx]['weight']) / total
    changes = rank_changes(sd, A)
    lead = leaders(sd, A)
    lead_names = list(dict.fromkeys(n for _, n in lead))

    metric_strip([
        ('Critério', name, 'peso em análise'),
        ('Peso original', f'{original:.4f}', 'normalizado, como entra no cálculo', {'mono': True}),
        ('Intervalo testado', f'{lo:.2f} – {hi:.2f}', f'{len(vals)} pontos', {'mono': True}),
        ('Trocas de posição', len(changes), 'ranking estável no intervalo' if not changes else 'ao longo do intervalo',
         {'tone': 'success' if not changes else 'neutral'}),
    ])

    series = [(A[a], sd[sd['alternative'] == a].sort_values('weight')['phi'].tolist()) for a in range(len(A))]
    left, right = st.columns([8, 4], gap='small')
    with left:
        with panel('sens', f'Fluxo líquido φ conforme o peso de {name}', 'Linha tracejada: peso original. Linhas pontilhadas: trocas de posição.'):
            charts.sensitivity_lines(sorted(sd['weight'].unique()), series, original, [c['weight'] for c in changes], f'peso de {name}', key='chart_sens')
    with right:
        with panel('changes', 'Mudanças no ranking', 'Pesos em que duas alternativas trocam de posição.'):
            if changes:
                items = ''.join(f'<li>Perto de <span class="num">{c["weight"]:.3f}</span>, <strong>{esc(c["up"])}</strong> ultrapassa {esc(c["down"])}</li>'
                                for c in changes)
                st.html(f'<ul class="mcda-list">{items}</ul>')
            else:
                st.html('<div class="mcda-empty">Nenhuma troca de posição entre os pesos testados. As linhas do gráfico não se cruzam neste intervalo.</div>')

    section('Posição por peso testado', f'Cada coluna é um peso de {name}; cada célula, a posição no ranking.')
    rank = sd.pivot(index='weight', columns='alternative', values='rank')
    closest = min(rank.index, key=lambda w: abs(w - original)) if lo <= original <= hi else None
    rows = [[A[a]] + [cell(int(rank.loc[w, a]), 'r num' + (' hit' if rank.loc[w, a] == 1 else '') + (' col-lead' if w == closest else ''))
                      for w in rank.index] for a in range(len(A))]
    data_table([('Alternativa', '')] + [(f'{w:.3g}', 'r' + (' col-lead' if w == closest else '')) for w in rank.index], rows,
               note='A coluna destacada é o peso testado mais próximo do original.' if closest is not None else 'O peso original está fora do intervalo testado.')

    section('Interpretação')
    if len(lead_names) == 1:
        text = f'<strong>{esc(lead_names[0])}</strong> mantém a 1ª posição em todo o intervalo testado. '
    else:
        text = f'A 1ª posição muda ao longo do intervalo: {esc(" → ".join(lead_names))}. '
    if changes:
        near = min(changes, key=lambda c: abs(c['weight'] - original))
        text += (f'A troca mais próxima do peso original ({original:.4f}) ocorre perto de {near["weight"]:.3f}, quando {esc(near["up"])} '
                 f'ultrapassa {esc(near["down"])}: uma distância de {abs(near["weight"] - original):.3f} no peso de {esc(name)}. ')
    else:
        text += f'Nenhuma alternativa troca de posição, o que indica um ranking robusto a variações no peso de {esc(name)}. '
    callout(text + _NOT_RANK_REVERSAL, 'Leitura')


def electre(data):
    A = data['alternatives']; C = data['criteria']; X = np.array(data['matrix'])
    ct, dt = float(data['c']), float(data['d'])
    page_header('05 / Sensibilidade', 'Como os limiares alteram a relação?',
                'Explore pequenas variações de c′ e d′ e observe quantas relações de sobreclassificação permanecem ativas.')
    cv = np.linspace(max(0, data['c'] - .2), min(1, data['c'] + .2), 5); dv = np.linspace(max(0, data['d'] - .2), min(1, data['d'] + .2), 5)
    sd = esens(X, C, cv, dv)
    ci = int(np.argmin(np.abs(cv - ct))); di = int(np.argmin(np.abs(dv - dt)))
    grid = {(i, j): int(sd.iloc[i * len(dv) + j]['arcs']) for i in range(len(cv)) for j in range(len(dv))}

    def kernel_names(text):
        if text == 'nenhum': return 'nenhum'
        return ' | '.join('{' + ', '.join(A[int(i)] for i in k.split(',')) + '}' for k in text.split(' | '))

    kernels = [kernel_names(k) for k in sd['kernels']]
    current_kernel = kernels[ci * len(dv) + di]
    distinct = list(dict.fromkeys(kernels))
    same = sum(k == current_kernel for k in kernels)
    metric_strip([
        ('Limiares atuais', f'{ct:.2f} / {dt:.2f}', 'c′ / d′ definidos em 02 Dados', {'mono': True}),
        ('Relações atuais', grid[(ci, di)], 'aSb aceitas', {'plain': True}),
        ('Faixa de relações', f'{min(grid.values())} – {max(grid.values())}', f'nas {len(grid)} combinações testadas', {'mono': True}),
        ('Kernel preservado', f'{same} de {len(kernels)}', 'combinações com o kernel atual', {'tone': 'success' if same == len(kernels) else 'neutral'}),
    ])

    left, right = st.columns([7, 5], gap='small')
    with left:
        with panel('heat', 'Relações aSb por combinação de limiares', 'A célula contornada corresponde aos limiares atuais.'):
            charts.threshold_heatmap(cv, dv, grid, (ci, di), key='chart_heat')
    with right:
        section('Combinações testadas')
        rows = [[cell(f'{row["c"]:.2f}', 'num'), cell(f'{row["d"]:.2f}', 'num'), cell(int(row['arcs']), 'r num'), k] for (_, row), k in zip(sd.iterrows(), kernels)]
        with st.container(height=372, border=False, key='combos'):
            data_table([('c′', ''), ('d′', ''), ('Relações', 'r'), ('Kernel', '')], rows, lead_rows=[ci * len(dv) + di])

    section('Interpretação')
    text = (f'Aumentar c′ exige mais apoio ponderado e reduzir d′ tolera menos desvantagem: ambos tornam a sobreclassificação mais difícil. '
            f'Nas {len(grid)} combinações testadas, o número de relações aceitas vai de {min(grid.values())} a {max(grid.values())}. ')
    if len(distinct) == 1:
        text += f'O kernel <strong>{esc(current_kernel)}</strong> se mantém em todas elas, o que indica um resultado robusto a estes limiares.'
    else:
        text += (f'O kernel atual <strong>{esc(current_kernel)}</strong> aparece em {same} delas; no total surgem {len(distinct)} resultados distintos, '
                 'portanto a conclusão depende dos limiares escolhidos.')
    callout(text, 'Leitura')
