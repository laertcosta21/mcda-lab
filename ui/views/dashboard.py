import json

import streamlit as st

from core.rules import METHODS, default_data, role_label
from engine import storage
from ui.components import badge, esc, footer, metric_strip, method_tone, page_header, section
from ui.layout import flash
from ui.navigation import sidebar_dashboard


@st.dialog('Novo exercício')
def _new_dialog(user):
    with st.form('new', border=False):
        n = st.text_input('Nome do exercício', placeholder='Ex.: Seleção de fornecedores')
        d = st.text_area('Descrição', placeholder='Contexto e objetivo da decisão')
        m = st.radio('Método', METHODS, horizontal=True)
        if st.form_submit_button('Criar exercício', type='primary', width='stretch'):
            if not n.strip(): st.error('Informe um nome para o exercício.')
            else:
                st.session_state.eid = storage.create(user['id'], n, d, m, default_data()); st.session_state.section = 'Problema'; st.rerun()


@st.dialog('Entrar com código')
def _join_dialog(user):
    with st.form('join', border=False):
        cd = st.text_input('Código do exercício', placeholder='MCDA-7K4P2', help='Peça o código ao proprietário do exercício.')
        if st.form_submit_button('Entrar no exercício', type='primary', width='stretch'):
            if storage.join(user['id'], cd): flash('Exercício adicionado.'); st.rerun()
            else: st.error('Código não encontrado.')


def _counts(exercise):
    try: data = json.loads(exercise['data'])
    except Exception: data = {}
    return len(data.get('alternatives', [])), len(data.get('criteria', []))


def _created(exercise):
    raw = (exercise['created_at'] or '')[:10]
    parts = raw.split('-')
    return '/'.join(reversed(parts)) if len(parts) == 3 else ''


def _card(exercise, user):
    n_alt, n_crit = _counts(exercise)
    created = _created(exercise)
    with st.container(border=True, key=f'excard_{exercise["id"]}'):
        st.html(
            f'<div class="mcda-ex-head {method_tone(exercise["method"])}"><span>{esc(exercise["method"])}</span>'
            f'<span class="mcda-ex-role">{role_label(exercise, user)}</span></div>'
            '<div class="mcda-ex-body">'
            f'<div class="mcda-ex-title" title="{esc(exercise["name"])}">{esc(exercise["name"])}</div>'
            f'<div class="mcda-ex-desc">{esc(exercise["description"] or "Sem descrição.")}</div>'
            '<div class="mcda-ex-stats">'
            f'<div class="mcda-ex-stat"><b>{n_alt}</b><span>{"alternativa" if n_alt == 1 else "alternativas"}</span></div>'
            f'<div class="mcda-ex-stat"><b>{n_crit}</b><span>{"critério" if n_crit == 1 else "critérios"}</span></div>'
            '</div>'
            f'<div class="mcda-ex-meta">{badge(exercise["code"], "code")}'
            + (f'<span>Criado em {esc(created)}</span>' if created else '')
            + '</div></div>'
        )
        if st.button('Abrir exercício', key=f"o{exercise['id']}", width='stretch'):
            st.session_state.eid = exercise['id']; st.session_state.section = 'Problema'; st.rerun()


def render():
    u = st.session_state.user
    sidebar_dashboard(u)
    flash()
    head, actions = st.columns([1.6, 1], vertical_alignment='bottom')
    with head:
        page_header('Workspace', 'Meus exercícios', 'Crie um experimento multicritério ou participe de uma análise usando um código compartilhado.')
    with actions:
        a, b = st.columns(2)
        if a.button('Novo exercício', type='primary', width='stretch', icon=':material/add:'): _new_dialog(u)
        if b.button('Entrar com código', width='stretch', icon=':material/key:'): _join_dialog(u)

    exs = storage.list_for(u['id'])
    if exs:
        own = sum(e['owner_id'] == u['id'] for e in exs)
        metric_strip([
            ('Exercícios', len(exs), ''),
            ('Como proprietário', own, ''),
            ('Como participante', len(exs) - own, ''),
            ('PROMETHEE II', sum(e['method'] == 'PROMETHEE II' for e in exs), ''),
            ('ELECTRE I', sum(e['method'] == 'ELECTRE I' for e in exs), ''),
        ])
    section('Exercícios', 'Mais recentes primeiro.' if exs else '')
    if not exs:
        st.html('<div class="mcda-empty">Nenhum exercício ainda. Use <strong>Novo exercício</strong> para montar o primeiro problema '
                'ou <strong>Entrar com código</strong> para participar de um exercício existente.</div>')
    for i in range(0, len(exs), 3):
        cols = st.columns(3)
        for col, e in zip(cols, exs[i:i + 3]):
            with col: _card(e, u)
    footer()
