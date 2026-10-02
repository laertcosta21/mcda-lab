"""MCDA Lab: roteador. Telas em ui/views, regras em core/, motores e persistência em engine/."""
import json

import streamlit as st

from core.rules import validate
from engine import storage
from ui.components import callout, esc, footer, page_header
from ui.layout import context_bar, flash, setup_page
from ui.navigation import sidebar_lab
from ui.views import about, analysis, auth, dashboard, method, problem, sensitivity
from ui.views import data as data_view

storage.init()
setup_page()

CALC_PAGES = {
    'PROMETHEE II': {'Método': method.promethee, 'Análise': analysis.promethee, 'Sensibilidade': sensitivity.promethee},
    'ELECTRE I': {'Método': method.electre, 'Análise': analysis.electre, 'Sensibilidade': sensitivity.electre},
}


def lab():
    u = st.session_state.user; e = storage.get(st.session_state.eid, u['id'])
    if not e: st.session_state.pop('eid', None); st.rerun()
    data = json.loads(e['data']); owner = e['owner_id'] == u['id']
    sidebar_lab(e, owner)
    flash()
    context_bar(e, owner)
    name = st.session_state.get('section', 'Problema')
    if name == 'Problema': problem.render(e, data, owner, u)
    elif name == 'Dados': data_view.render(e, data, owner, u)
    elif name in ('Método', 'Análise', 'Sensibilidade'):
        pages = CALC_PAGES.get(e['method'], CALC_PAGES['ELECTRE I'])
        errs = validate(data)
        if errs:
            page_header('Modelo incompleto', 'Complete os dados antes de calcular', 'O laboratório precisa de uma estrutura válida para executar o método.')
            callout('<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in errs) + '</ul>', 'O que falta', 'warning')
        else:
            try: pages[name](data)
            except ValueError as err:
                # o motor recusa parâmetros que a validação não cobre (ex.: V-Shape com p = 0)
                st.error(f'O método não pôde ser calculado com os parâmetros atuais: {err}. Revise os dados em 02 Dados.', icon=':material/error:')
    else: about.render(e)
    footer()


if auth.render():
    if st.session_state.get('eid'): lab()
    else: dashboard.render()
