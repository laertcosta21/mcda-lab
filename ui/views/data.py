import pandas as pd
import streamlit as st

from core.rules import FUNCTION_PARAMS, FUNCTIONS, PARAM_DEFAULTS, rebuild_matrix
from engine import storage
from ui.components import cell, data_table, esc, metric_strip, page_header, panel, section
from ui.layout import flash

_PARAM_HELP = {'q': 'q: limiar de indiferença', 'p': 'p: limiar de preferência estrita', 's': 's: ponto de inflexão da curva gaussiana'}
_PARAM_GRID = [3, 3, 2, 2, 2]


def _objective(direction):
    return '↑ Maximizar' if direction == 'MAX' else '↓ Minimizar'


def _params_text(c):
    used = FUNCTION_PARAMS.get(c.get('function', 'Usual'), ())
    return ', '.join(f'{k} = {float(c.get(k, PARAM_DEFAULTS[k])):g}' for k in used) or '—'


def _criteria_editor(data, promethee):
    """Tabela compacta de critérios. Função só existe no PROMETHEE; q, p e s ficam no bloco de parâmetros."""
    stored = {c.get('name'): c for c in data['criteria']}
    cols = ['Critério', 'Objetivo', 'Peso'] + (['Função'] if promethee else [])
    rows = [{'Critério': c.get('name', ''), 'Objetivo': c.get('direction', 'MAX'), 'Peso': c.get('weight', 0), 'Função': c.get('function', 'Usual')}
            for c in data['criteria']]
    cfg = {
        'Critério': st.column_config.TextColumn('Critério', required=True, width='medium'),
        'Objetivo': st.column_config.SelectboxColumn('Objetivo', options=['MAX', 'MIN'], default='MAX', required=True,
                                                     help='MAX = maximizar (maior é preferível) · MIN = minimizar (menor é preferível)'),
        'Peso': st.column_config.NumberColumn('Peso', min_value=0., format='%.4f', default=0., help='Os pesos são normalizados no cálculo.'),
        'Função': st.column_config.SelectboxColumn('Função de preferência', options=FUNCTIONS, default='Usual', required=True, width='medium',
                                                   help='Usual não tem parâmetros. U-Shape usa q; V-Shape usa p; Level e V-Shape with Indifference usam q e p; Gaussian usa s.'),
    }
    df = st.data_editor(pd.DataFrame(rows, columns=cols), num_rows='dynamic', width='stretch', hide_index=True, key='crit_v3',
                        column_config={k: v for k, v in cfg.items() if k in cols})
    crit = []
    for _, r in df.iterrows():
        name = r.get('Critério')
        if name is None or pd.isna(name) or not str(name).strip(): continue
        name = str(name).strip(); prev = stored.get(name, {})
        weight = r.get('Peso')
        crit.append({
            'name': name,
            'direction': str(r.get('Objetivo') or 'MAX'),
            'weight': 0. if weight is None or pd.isna(weight) else float(weight),
            'function': str(r.get('Função') or 'Usual') if promethee else prev.get('function', 'Usual'),
            'q': float(prev.get('q', 0) or 0), 'p': float(prev.get('p', 1) or 1), 's': float(prev.get('s', 1) or 1),
        })
    return crit


def _params_editor(crit):
    """Uma linha por critério cuja função exige parâmetros; só os campos necessários aparecem."""
    need = [(i, c) for i, c in enumerate(crit) if FUNCTION_PARAMS.get(c['function'])]
    if not need: return
    with panel('params', 'Parâmetros das funções de preferência', 'Aparecem apenas os parâmetros exigidos pela função escolhida.'):
        head = st.columns(_PARAM_GRID, vertical_alignment='center')
        for col, label in zip(head, ['Critério', 'Função', 'q', 'p', 's']):
            col.html(f'<div class="mcda-param-head">{label}</div>')
        for i, c in need:
            row = st.columns(_PARAM_GRID, vertical_alignment='center')
            row[0].html(f'<div class="mcda-param-cell">{esc(c["name"])}</div>')
            row[1].html(f'<div class="mcda-param-cell">{esc(c["function"])}</div>')
            for k, param in enumerate(('q', 'p', 's')):
                if param in FUNCTION_PARAMS[c['function']]:
                    c[param] = row[2 + k].number_input(f'{param} de {c["name"]}', value=float(c[param]), min_value=0., step=.1, format='%.4f',
                                                       key=f'prm_{i}_{c["name"]}_{param}', label_visibility='collapsed', help=_PARAM_HELP[param])
                else:
                    row[2 + k].html('<div class="mcda-param-cell dim">—</div>')


def render(e, data, owner, u):
    promethee = e['method'] == 'PROMETHEE II'
    page_header('02 / Dados', 'Critérios, pesos e desempenho',
                'Organize a estrutura do modelo em uma visão compacta: o que se avalia, com que importância e como cada alternativa se sai.')
    if not owner: st.info('Modo participante: os dados são definidos pelo proprietário do exercício.', icon=':material/visibility:')

    section('Critérios', 'Objetivo, peso' + (' e função de preferência de cada critério.' if promethee else ' de cada critério.')
            + (' Inclua na última linha; para excluir, selecione a linha e use a lixeira.' if owner else ''))
    if owner:
        crit = _criteria_editor(data, promethee)
        if promethee: _params_editor(crit)
    else:
        crit = data['criteria']
        sw = sum(float(c.get('weight', 0)) for c in crit)
        if crit:
            columns = [('Critério', ''), ('Objetivo', ''), ('Peso', 'r'), ('Peso normalizado', 'r')] + ([('Função', ''), ('Parâmetros', '')] if promethee else [])
            rows = []
            for c in crit:
                w = float(c.get('weight', 0))
                row = [c['name'], _objective(c.get('direction', 'MAX')), cell(f'{w:.4f}', 'r num'), cell(f'{w / sw:.4f}' if sw > 0 else '—', 'r num')]
                if promethee: row += [c.get('function', 'Usual'), cell(_params_text(c), 'num')]
                rows.append(row)
            data_table(columns, rows)
        else: st.html('<div class="mcda-empty">Nenhum critério cadastrado.</div>')

    if crit:
        sw = sum(c['weight'] for c in crit)
        n_max = sum(c['direction'] == 'MAX' for c in crit)
        metric_strip([
            ('Critérios', len(crit), 'estrutura de avaliação'),
            ('Soma dos pesos', f'{sw:.4f}', 'normalizada no cálculo', {'mono': True}),
            ('Objetivos', f'{n_max} ↑  {len(crit) - n_max} ↓', 'a maximizar e a minimizar'),
        ])

    section('Matriz de desempenho', 'Alternativas nas linhas, critérios nas colunas.')
    alts = data['alternatives']
    new = rebuild_matrix(data, alts, [c['name'] for c in crit])
    new.index.name = 'Alternativa'
    edited = new
    if not alts:
        st.html('<div class="mcda-empty">Cadastre as alternativas em <strong>01 Problema</strong> para montar a matriz.</div>')
    elif not crit:
        st.html('<div class="mcda-empty">Adicione ao menos um critério acima para montar a matriz.</div>')
    else:
        cfg = {c['name']: st.column_config.NumberColumn(f"{c['name']} {'↑' if c['direction'] == 'MAX' else '↓'}",
                                                        help=f"{c['name']}: {'maximizar, valores maiores são preferíveis' if c['direction'] == 'MAX' else 'minimizar, valores menores são preferíveis'}")
               for c in crit}
        if owner: edited = st.data_editor(new, width='stretch', key='matrix_v3', column_config=cfg)
        else: st.dataframe(new, width='stretch', column_config=cfg)
        st.caption('↑ maximizar: valores maiores são preferíveis. ↓ minimizar: valores menores são preferíveis.')

    if not promethee:
        section('Limiares', 'Condições para aceitar a sobreclassificação aSb.')
        c1, c2 = st.columns(2, gap='medium')
        data['c'] = c1.slider('Concordância mínima c′', 0., 1., float(data.get('c', .7)), .01, disabled=not owner,
                              help='aSb exige C(a,b) ≥ c′.')
        data['d'] = c2.slider('Discordância máxima d′', 0., 1., float(data.get('d', .4)), .01, disabled=not owner,
                              help='aSb exige D(a,b) ≤ d′.')

    if owner:
        st.caption('As alterações só entram no cálculo depois de salvas.')
        if st.button('Salvar dados', type='primary', icon=':material/save:'):
            if edited.isna().any().any():
                st.error('Preencha todos os valores da matriz de desempenho antes de salvar.')
            else:
                data['criteria'] = crit; data['matrix'] = edited.astype(float).values.tolist()
                storage.update(e['id'], u['id'], data); flash('Dados salvos.'); st.rerun()
