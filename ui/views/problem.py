import pandas as pd
import streamlit as st

from core.rules import rebuild_matrix
from engine import storage
from ui.components import cell, data_table, esc, metric_strip, page_header, section
from ui.layout import flash


def render(e, data, owner, u):
    page_header('01 / Problema', 'Defina o problema de decisão',
                'Comece pelo contexto. A matemática entra depois que a decisão e as alternativas estiverem claras.')
    n_alt = len(data['alternatives'])
    metric_strip([
        ('Método', e['method'], 'definido na criação'),
        ('Alternativas', n_alt, 'mínimo para calcular: 2'),
        ('Critérios', len(data['criteria']), 'definidos em 02 Dados'),
        ('Código', e['code'], 'compartilhe com participantes', {'mono': True}),
    ])
    if not owner:
        st.info('Modo participante: somente o proprietário pode editar o problema.', icon=':material/visibility:')
        left, right = st.columns([7, 5], gap='medium')
        with left:
            section('Contexto')
            st.html(f'<div class="mcda-prose">{esc(e["description"] or "Sem descrição.")}</div>')
        with right:
            section('Alternativas', f'{n_alt} cadastradas')
            if n_alt: data_table([('#', ''), ('Alternativa', '')], [[cell(f'{i:02d}', 'num dim'), a] for i, a in enumerate(data['alternatives'], 1)])
            else: st.html('<div class="mcda-empty">Nenhuma alternativa cadastrada.</div>')
        return

    left, right = st.columns([7, 5], gap='medium')
    with left:
        section('Contexto')
        title = st.text_input('Título do exercício', value=e['name'])
        desc = st.text_area('Descrição do problema', value=e['description'] or '', height=168,
                            placeholder='Descreva o objetivo da decisão e seu contexto.')
    with right:
        section('Alternativas', 'uma por linha')
        adf = st.data_editor(pd.DataFrame({'Alternativa': data['alternatives']}), num_rows='dynamic', width='stretch', hide_index=True,
                             key='alts_v3', column_config={'Alternativa': st.column_config.TextColumn('Alternativa', required=True)})
    alts = [str(x).strip() for x in adf['Alternativa'].tolist() if str(x).strip() and str(x) != 'nan']
    st.caption('As alterações só entram no cálculo depois de salvas. Os valores já lançados na matriz são preservados por alternativa.')
    if st.button('Salvar problema', type='primary', icon=':material/save:'):
        new = rebuild_matrix(data, alts, [c['name'] for c in data['criteria']])
        data['alternatives'] = alts; data['matrix'] = new.values.tolist()
        storage.update(e['id'], u['id'], data, title, desc); flash('Problema salvo.'); st.rerun()
