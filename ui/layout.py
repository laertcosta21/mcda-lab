"""App shell: configuração da página e estrutura comum a todas as telas."""
import streamlit as st

from ui.components import badge, esc, method_tone
from ui.theme import apply_theme


def setup_page():
    st.set_page_config(page_title='MCDA Lab', page_icon=':material/query_stats:', layout='wide', initial_sidebar_state='expanded')
    apply_theme()


def context_bar(exercise, owner):
    """Identificação do exercício, igual em todas as páginas do workspace."""
    st.html(
        '<div class="mcda-context">'
        f'<span class="mcda-context-name">{esc(exercise["name"])}</span>'
        '<span class="mcda-badges">'
        + badge(exercise['method'], method_tone(exercise['method']))
        + badge(exercise['code'], 'mono')
        + badge('Proprietário' if owner else 'Participante')
        + '</span></div>'
    )


def flash(message=None):
    """Mensagem que sobrevive a um st.rerun(): grave com flash('...'), exiba com flash()."""
    if message is not None:
        st.session_state['_flash'] = message
        return
    pending = st.session_state.pop('_flash', None)
    if pending:
        st.toast(pending, icon=':material/check_circle:')
