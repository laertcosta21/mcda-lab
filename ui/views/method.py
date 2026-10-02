import numpy as np
import streamlit as st

from core.explain import electre_pair
from engine.electre import EPS, calculate as ecalc
from engine.promethee import calculate as pcalc
from ui.components import callout, cell, data_table, esc, formula, metric_strip, page_header, section, steps


def _objective(c):
    return '↑ MAX' if c['direction'] == 'MAX' else '↓ MIN'


def _pair(A, prefix):
    c1, c2 = st.columns(2, gap='medium')
    a = c1.selectbox('Alternativa a', range(len(A)), format_func=lambda i: A[i], key=prefix + 'a')
    b = c2.selectbox('Alternativa b', range(len(A)), index=min(1, len(A) - 1), format_func=lambda i: A[i], key=prefix + 'b')
    return a, b


def _res(text):
    return f'<span class="res">{esc(text)}</span>'


def promethee(data):
    A = data['alternatives']; C = data['criteria']; X = np.array(data['matrix']); r = pcalc(X, C)
    page_header('03 / Método', 'Como o PROMETHEE II constrói a preferência',
                'Explore uma comparação par a par e veja como cada critério contribui para a preferência agregada.')
    st.html(steps(['Comparação', 'Preferência por critério', 'Contribuição ponderada', 'Preferência agregada']))

    section('Formulação', step='1')
    formula(['S(a,b) = Σⱼ wⱼ · Fⱼ(a,b)', 'φ⁺(a) = Σ S(a,b) / (n−1)', 'φ⁻(a) = Σ S(b,a) / (n−1)', 'φ(a) = φ⁺(a) − φ⁻(a)'])

    section('Comparação par a par', 'escolha o par a → b', step='2')
    a, b = _pair(A, 'p')
    if a == b:
        st.warning('Escolha duas alternativas diferentes para visualizar a comparação.'); return
    na, nb = A[a], A[b]; w = r['weights']; F = r['preferences'][a, b]

    section('Preferência por critério e contribuição ponderada', f'{na} em relação a {nb}', step='3')
    rows = []
    for j, c in enumerate(C):
        contrib = w[j] * F[j]
        rows.append([c['name'], _objective(c), cell(f'{X[a, j]:g}', 'r num'), cell(f'{X[b, j]:g}', 'r num'), c.get('function', 'Usual'),
                     cell(f'{F[j]:.4f}', 'r num' + ('' if F[j] > 0 else ' dim')), cell(f'{w[j]:.4f}', 'r num'),
                     cell(f'{contrib:.4f}', 'r num' + (' hit' if contrib > 0 else ' dim'))])
    data_table(
        [('Critério', ''), ('Objetivo', ''), (na, 'r'), (nb, 'r'), ('Função', ''), ('Fⱼ(a,b)', 'r'), ('wⱼ', 'r'), ('wⱼ × Fⱼ', 'r')],
        rows,
        total=[f'S({na}, {nb})', '', '', '', '', '', cell('Σ', 'r dim'), cell(f'{r["S"][a, b]:.4f}', 'r num hit')],
        note='Leia da esquerda para a direita: desempenho → preferência Fⱼ → peso normalizado wⱼ → contribuição wⱼ × Fⱼ.',
    )

    section('Preferência agregada', 'substituição numérica', step='4')
    terms = ' + '.join(f'{w[j]:.4f}×{F[j]:.4g}' for j in range(len(C)))
    formula([
        f'S({esc(na)}, {esc(nb)}) = Σⱼ wⱼ · Fⱼ',
        f'S({esc(na)}, {esc(nb)}) = {terms}',
        f'S({esc(na)}, {esc(nb)}) = {_res(format(r["S"][a, b], ".4f"))}',
    ])
    favor = [C[j]['name'] for j in range(len(C)) if F[j] > 0]
    sab, sba = float(r['S'][a, b]), float(r['S'][b, a])
    metric_strip([
        (f'S({na}, {nb})', f'{sab:.4f}', 'preferência de a sobre b', {'mono': True, 'plain': True}),
        (f'S({nb}, {na})', f'{sba:.4f}', 'preferência de b sobre a', {'mono': True, 'plain': True}),
        ('Critérios a favor de a', f'{len(favor)} de {len(C)}', 'com Fⱼ(a,b) > 0'),
    ])
    if favor:
        text = (f'<strong>{esc(na)}</strong> é preferida a <strong>{esc(nb)}</strong> em {len(favor)} de {len(C)} critérios '
                f'({esc(", ".join(favor))}). Somando as contribuições ponderadas, S = {sab:.4f}. ')
    else:
        text = f'<strong>{esc(na)}</strong> não é preferida a <strong>{esc(nb)}</strong> em nenhum critério, portanto S = {sab:.4f}. '
    text += (f'No sentido inverso, S({esc(nb)}, {esc(na)}) = {sba:.4f}. Esses valores par a par alimentam os fluxos φ⁺ e φ⁻ '
             'de cada alternativa na página Análise.')
    callout(text, 'Leitura')


def electre(data):
    A = data['alternatives']; C = data['criteria']; X = np.array(data['matrix']); r = ecalc(X, C, data['c'], data['d'])
    ct, dt = float(data['c']), float(data['d'])
    page_header('03 / Método', 'Como o ELECTRE I testa a sobreclassificação',
                'Compare concordância e discordância com os limiares definidos para verificar se a relação aSb é aceita.')
    st.html(steps(['Comparação', 'Concordância', 'Discordância', 'Limiares', 'Relação de sobreclassificação']))

    section('Formulação', step='1')
    formula(['C(a,b) = Σ wⱼ nos critérios em que a é pelo menos tão boa quanto b',
             'D(a,b) = max(desvantagem de a / amplitude do critério)',
             'aSb ⇔ C(a,b) ≥ c′  E  D(a,b) ≤ d′'])

    section('Comparação par a par', 'escolha o par a → b', step='2')
    a, b = _pair(A, 'e')
    if a == b:
        st.warning('Escolha duas alternativas diferentes.'); return
    na, nb = A[a], A[b]; w = r['weights']; pair = electre_pair(X, C, a, b)
    cc = float(r['C'][a, b]); dd = float(r['D'][a, b]); okc = cc >= ct - EPS; okd = dd <= dt + EPS; rel = bool(r['R'][a, b])

    section('Concordância e discordância por critério', f'{na} em relação a {nb}', step='3')
    rows = []
    for j, c in enumerate(C):
        agrees = bool(pair['agrees'][j]); disc = float(pair['discordance'][j])
        rows.append([c['name'], _objective(c), cell(f'{X[a, j]:g}', 'r num'), cell(f'{X[b, j]:g}', 'r num'), cell(f'{w[j]:.4f}', 'r num'),
                     cell('concorda' if agrees else 'discorda', 'strong' if agrees else 'dim'),
                     cell(f'{w[j]:.4f}' if agrees else '—', 'r num' + (' hit' if agrees else ' dim')),
                     cell(f'{disc:.4f}' if disc > 0 else '—', 'r num' + ('' if disc > 0 else ' dim'))])
    data_table(
        [('Critério', ''), ('Objetivo', ''), (na, 'r'), (nb, 'r'), ('wⱼ', 'r'), ('a ≥ b?', ''), ('Peso concordante', 'r'), ('Desvantagem de a', 'r')],
        rows,
        total=['Resultado', '', '', '', '', '', cell(f'C = {cc:.4f}', 'r num hit'), cell(f'D = {dd:.4f}', 'r num hit')],
        note='A concordância soma os pesos dos critérios em que a não é pior que b. A discordância é a maior desvantagem de a, em proporção da amplitude do critério.',
    )
    agree_terms = ' + '.join(f'{w[j]:.4f}' for j in range(len(C)) if pair['agrees'][j]) or '0'
    disc_terms = ', '.join(f'{float(v):.4f}' for v in pair['discordance'] if v > 0) or '0'
    formula([
        f'C({esc(na)}, {esc(nb)}) = {agree_terms} = {_res(format(cc, ".4f"))}',
        f'D({esc(na)}, {esc(nb)}) = max({disc_terms}) = {_res(format(dd, ".4f"))}',
    ])

    section('Teste dos limiares e relação', step='4')
    metric_strip([
        ('Concordância C(a,b)', f'{cc:.4f}', f"{'≥' if okc else '<'} c′ = {ct:.2f} · {'atende' if okc else 'não atende'}",
         {'mono': True, 'plain': True, 'tone': 'success' if okc else 'neutral'}),
        ('Discordância D(a,b)', f'{dd:.4f}', f"{'≤' if okd else '>'} d′ = {dt:.2f} · {'atende' if okd else 'não atende'}",
         {'mono': True, 'plain': True, 'tone': 'success' if okd else 'neutral'}),
        ('Relação aSb', 'Sim' if rel else 'Não', f'{na} → {nb}', {'plain': True, 'tone': 'success' if rel else 'neutral'}),
    ])
    if rel:
        why = 'os dois testes são atendidos ao mesmo tempo: a maioria ponderada dos critérios apoia a afirmação e nenhuma desvantagem é grande o bastante para vetá-la'
    elif not okc and not okd:
        why = 'nenhum dos dois testes é atendido: falta apoio ponderado suficiente e há uma desvantagem acima do tolerado'
    elif not okc:
        why = f'a concordância {cc:.4f} fica abaixo do mínimo c′ = {ct:.2f}, ou seja, falta apoio ponderado suficiente'
    else:
        why = f'a discordância {dd:.4f} supera o máximo d′ = {dt:.2f}, ou seja, há um critério em que a desvantagem é grande demais'
    callout(f'<strong>{esc(na)}</strong> {"sobreclassifica" if rel else "não sobreclassifica"} <strong>{esc(nb)}</strong>: {why}. '
            'A relação exige que concordância e discordância satisfaçam simultaneamente seus limiares.', 'Leitura')
