"""Sidebar: marca, contexto e navegação entre as seções do workspace."""
import streamlit as st

from ui import dialogs, session
from ui.components import esc, icon

# (seção, número, ícone Material Symbols)
NAV_ITEMS = [
    ('Problema', '01', 'description'),
    ('Dados', '02', 'table_view'),
    ('Método', '03', 'function'),
    ('Análise', '04', 'analytics'),
    ('Sensibilidade', '05', 'tune'),
    ('Sobre', '06', 'info'),
]


def _brand():
    st.html(f'<div class="mcda-brand"><span class="mcda-brand-mark">{icon("query_stats")}</span>'
            '<div><div class="mcda-brand-name">MCDA Lab</div><div class="mcda-brand-sub">Laboratório acadêmico</div></div></div>')


def _account(user):
    """Conta e saída, iguais no painel e dentro de um exercício."""
    with st.container(key='nav_foot'):
        if st.button('Minha conta', width='stretch', icon=':material/person:'):
            dialogs.account(user)
        if st.button('Sair', width='stretch', icon=':material/logout:'):
            session.end(); st.rerun()


def sidebar_dashboard(user):
    with st.sidebar:
        _brand()
        st.divider()
        st.html(
            '<div class="mcda-side-block"><div class="mcda-side-label">Conectado como</div>'
            f'<div class="mcda-side-title">{esc(user.get("name") or user.get("email"))}</div>'
            f'<div class="mcda-side-meta">{esc(user.get("email") or "")}</div></div>'
        )
        st.divider()
        _account(user)


def sidebar_lab(exercise, owner, user):
    with st.sidebar:
        _brand()
        st.divider()
        st.html(
            '<div class="mcda-side-block"><div class="mcda-side-label">Exercício</div>'
            f'<div class="mcda-side-title">{esc(exercise["name"])}</div>'
            f'<div class="mcda-side-meta">{esc(exercise["method"])}<br><span class="code">{esc(exercise["code"])}</span>'
            f', {"proprietário" if owner else "participante"}</div></div>'
        )
        st.divider()
        current = st.session_state.get('section', 'Problema')
        with st.container(key='nav'):
            for name, number, symbol in NAV_ITEMS:
                # o número vai em `code` para ganhar coluna própria de largura fixa via CSS
                if st.button(f'`{number}` {name}', key='nav_' + name, width='stretch', icon=f':material/{symbol}:',
                             type='primary' if current == name else 'secondary'):
                    st.session_state.section = name; st.rerun()
        st.divider()
        with st.container(key='nav_back'):
            if st.button('Meus exercícios', width='stretch', icon=':material/arrow_back:'):
                st.session_state.pop('eid', None); st.rerun()
        _account(user)
