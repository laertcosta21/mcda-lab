import numpy as np
import streamlit as st

from core.explain import electre_tests, promethee_ranking
from engine.electre import calculate as ecalc
from engine.promethee import calculate as pcalc
from ui import charts
from ui.components import callout, cell, data_table, esc, matrix_table, metric_strip, page_header, panel, rank_list, section


def promethee(data):
    A = data['alternatives']; C = data['criteria']; X = np.array(data['matrix']); r = pcalc(X, C)
    page_header('04 / Análise', 'Resultado PROMETHEE II',
                'Fluxos positivos e negativos sintetizam as comparações par a par; o fluxo líquido φ organiza o ranking final.')
    out = promethee_ranking(A, r)
    winner = out.iloc[0]
    metric_strip([
        ('1ª posição', winner['Alternativa'], 'maior fluxo líquido', {'accent': True}),
        ('φ⁺', f"{winner['φ+']:.4f}", 'força: o quanto supera as demais', {'mono': True, 'plain': True}),
        ('φ⁻', f"{winner['φ−']:.4f}", 'fraqueza: o quanto é superada', {'mono': True, 'plain': True}),
        ('φ', f"{winner['φ']:+.4f}", 'saldo líquido φ⁺ − φ⁻', {'mono': True, 'plain': True}),
    ])

    left, right = st.columns([8, 4], gap='small')
    with left:
        with panel('phi', 'Fluxo líquido φ', 'Valores positivos: a alternativa mais supera do que é superada.'):
            charts.net_flow_bar(A, [float(v) for v in r['phi']], key='chart_phi')
    with right:
        with panel('rank', 'Ranking', 'Ordenação completa por φ.'):
            rank_list([(int(row['Posição']), row['Alternativa'], f"{row['φ']:+.4f}") for _, row in out.iterrows()])

    left, right = st.columns(2, gap='small')
    with left:
        section('Matriz de preferências', 'S(a,b): preferência da linha a sobre a coluna b.')
        matrix_table(r['S'], A, note='Quanto mais escura a célula, maior a preferência agregada de a sobre b.')
    with right:
        section('Fluxos por alternativa')
        data_table(
            [('Pos.', ''), ('Alternativa', ''), ('φ⁺', 'r'), ('φ⁻', 'r'), ('φ', 'r')],
            [[cell(int(row['Posição']), 'num dim'), cell(row['Alternativa'], 'strong'), cell(f"{row['φ+']:.4f}", 'r num'),
              cell(f"{row['φ−']:.4f}", 'r num'), cell(f"{row['φ']:+.4f}", 'r num strong')] for _, row in out.iterrows()],
            lead_rows=[i for i, p in enumerate(out['Posição']) if p == 1],
            note='φ⁺ é a média de S(a,·); φ⁻ é a média de S(·,a); φ = φ⁺ − φ⁻.',
        )

    section('Interpretação')
    firsts = out[out['Posição'] == 1]['Alternativa'].tolist()
    if len(firsts) > 1:
        text = f'Há empate na 1ª posição entre <strong>{esc(", ".join(firsts))}</strong>, com φ = {winner["φ"]:+.4f}. '
    else:
        text = f'<strong>{esc(firsts[0])}</strong> ocupa a 1ª posição com φ = {winner["φ"]:+.4f}. '
        if len(out) > len(firsts):
            second = out.iloc[len(firsts)]
            text += f'A distância para a posição seguinte ({esc(second["Alternativa"])}) é de {winner["φ"] - second["φ"]:.4f}. '
    text += ('O ranking é uma consequência dos dados, pesos e funções de preferência informados: distâncias pequenas em φ indicam '
             'posições sensíveis a mudanças nos pesos, o que pode ser examinado em 05 Sensibilidade.')
    callout(text, 'Leitura')


def electre(data):
    A = data['alternatives']; C = data['criteria']; X = np.array(data['matrix']); r = ecalc(X, C, data['c'], data['d'])
    ct, dt = float(data['c']), float(data['d'])
    page_header('04 / Análise', 'Relação de sobreclassificação ELECTRE I',
                'Leia as matrizes, o grafo dirigido e o kernel sem forçar um ranking completo onde o método não o produz.')
    arcs = int(r['R'].sum()); ks = ['{' + ', '.join(A[i] for i in k) + '}' for k in r['kernels']]
    metric_strip([
        ('Relações aSb', arcs, f'de {len(A) * (len(A) - 1)} pares ordenados', {'plain': True}),
        ('Limiares', f'{ct:.2f} / {dt:.2f}', 'c′ mínimo de concordância, d′ máximo de discordância', {'mono': True}),
        ('Kernel', ' e '.join(ks) if ks else '—', '1 conjunto encontrado' if len(ks) == 1 else f'{len(ks)} conjuntos encontrados', {'accent': True}),
    ])

    okc, okd = electre_tests(r['C'], r['D'], ct, dt)
    left, right = st.columns(2, gap='small')
    with left:
        section('Concordância', f'C(a,b). Em destaque, os pares com C ≥ {ct:.2f}.')
        matrix_table(r['C'], A, mark=okc)
    with right:
        section('Discordância', f'D(a,b). Em destaque, os pares com D ≤ {dt:.2f}.')
        matrix_table(r['D'], A, mark=okd)

    left, right = st.columns([5, 7], gap='small')
    with left:
        section('Relação de sobreclassificação', 'S indica que a linha sobreclassifica a coluna.')
        rows = []
        for i, name in enumerate(A):
            rows.append([name] + [cell('—', 'c num dim') if i == j else cell('S' if r['R'][i, j] else '·', 'c num ' + ('hit' if r['R'][i, j] else 'dim'))
                                  for j in range(len(A))])
        data_table([('a \\ b', '')] + [(n, 'c') for n in A], rows,
                   note='aSb só é aceita quando os dois destaques acima coincidem no mesmo par.')
    with right:
        with panel('graph', 'Grafo de sobreclassificação', 'A seta a → b indica que a sobreclassifica b. Nós preenchidos pertencem ao kernel.'):
            charts.outranking_graph(A, r['R'].tolist(), {i for k in r['kernels'] for i in k}, key='chart_graph')

    section('Interpretação')
    if not ks:
        text = ('Com estes limiares não existe kernel: há ciclos na relação de sobreclassificação que impedem isolar um conjunto estável. '
                'Ajustar c′ e d′ em 02 Dados muda quais relações são aceitas.')
    elif len(ks) == 1:
        text = (f'O kernel é <strong>{esc(ks[0])}</strong>: nenhuma dessas alternativas sobreclassifica outra do conjunto e toda alternativa '
                'fora dele é sobreclassificada por ao menos uma de dentro. ')
        text += ('Como o kernel reúne mais de uma alternativa, o método não as distingue entre si com estes limiares.' if len(r['kernels'][0]) > 1
                 else 'Como o kernel tem uma única alternativa, ela se destaca das demais sob estes limiares.')
    else:
        text = f'Foram encontrados {len(ks)} kernels: <strong>{esc(" e ".join(ks))}</strong>. Isso ocorre quando a relação contém ciclos; cada conjunto é uma leitura possível.'
    text += (f' Foram aceitas {arcs} relações aSb. O ELECTRE I separa um subconjunto de alternativas a examinar; ele não produz uma ordenação completa.')
    callout(text, 'Leitura')
