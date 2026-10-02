import json

import streamlit as st

from core.rules import role_label
from engine import storage
from ui import dialogs
from ui.components import badge, esc, footer, metric_strip, method_tone, page_header, section
from ui.layout import flash
from ui.navigation import sidebar_dashboard


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
    owner = exercise['owner_id'] == user['id']
    eid = exercise['id']
    with st.container(border=True, key=f'excard_{eid}'):
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
        with st.container(horizontal=True, key=f'exact_{eid}'):
            if st.button('Abrir exercício', key=f'o{eid}', width='stretch'):
                st.session_state.eid = eid; st.session_state.section = 'Problema'; st.rerun()
            with st.popover('', icon=':material/more_horiz:', help='Mais ações', key=f'more_{eid}'):
                if owner:
                    if st.button('Editar nome e descrição', key=f'ed{eid}', width='stretch', icon=':material/edit:'):
                        dialogs.edit_exercise(exercise, user)
                    with st.container(key=f'danger_card{eid}'):
                        if st.button('Excluir exercício', key=f'del{eid}', width='stretch', icon=':material/delete:'):
                            dialogs.delete_exercise(exercise, user)
                else:
                    with st.container(key=f'danger_card{eid}'):
                        if st.button('Sair do exercício', key=f'lv{eid}', width='stretch', icon=':material/logout:'):
                            dialogs.leave_exercise(exercise, user)


def render():
    u = st.session_state.user
    sidebar_dashboard(u)
    flash()
    head, actions = st.columns([3, 2], vertical_alignment='bottom')
    with head:
        page_header('Workspace', 'Meus exercícios', 'Crie um exercício ou entre em um existente com o código compartilhado.')
    with actions:
        with st.container(horizontal=True, horizontal_alignment='right', key='page_actions'):
            if st.button('Novo exercício', type='primary', icon=':material/add:'): dialogs.new_exercise(u)
            if st.button('Entrar com código', icon=':material/key:'): dialogs.join_exercise(u)

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
    section('Exercícios', 'Mais recentes primeiro. Use o menu de cada card para editar ou excluir.' if exs else '')
    if not exs:
        st.html('<div class="mcda-empty">Nenhum exercício ainda. Use <strong>Novo exercício</strong> para montar o primeiro problema '
                'ou <strong>Entrar com código</strong> para participar de um exercício existente.</div>')
    for i in range(0, len(exs), 3):
        cols = st.columns(3)
        for col, e in zip(cols, exs[i:i + 3]):
            with col: _card(e, u)
    footer()
