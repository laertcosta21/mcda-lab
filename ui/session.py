"""Sessão que sobrevive ao F5.

O Streamlit apaga o session_state a cada recarga. Para manter o login, o token da
sessão fica num cookie do navegador e é validado no banco a cada nova conexão.
A tela em que a pessoa estava (exercício e seção) fica na URL.

Quem lê o cookie é o navegador, por um componente que o devolve ao Python: o
Streamlit Community Cloud não repassa cookies ao app, então st.context.cookies
chega vazio em produção.
"""
import streamlit as st

from core.rules import SECTIONS
from engine import storage

COOKIE = 'mcda_session'

_reader = st.components.v2.component('mcda_session_reader', js="""
export default function({ setStateValue }) {
    const found = document.cookie.match(/(?:^|; )%s=([^;]*)/);
    setStateValue('token', found ? found[1] : '');
}
""" % COOKIE)


def restore():
    """Recupera o usuário pelo cookie e a tela pela URL, uma vez por conexão."""
    ss = st.session_state
    if not ss.get('user') and not ss.get('_logged_out') and '_browser_token' not in ss:
        token = _reader(key='mcda_session_reader', on_token_change=lambda: None).token
        if token is None: st.stop()  # o navegador ainda não respondeu; a resposta dispara nova execução
        ss['_browser_token'] = token
        u = storage.session_user(token)
        if u:
            ss.user = dict(u); ss['_token'] = token
    if not ss.get('_nav_restored'):
        ss['_nav_restored'] = True
        q = st.query_params
        if 'eid' not in ss and str(q.get('e', '')).isdigit(): ss.eid = int(q['e'])
        if 'section' not in ss and q.get('s') in SECTIONS: ss.section = q['s']


def start(user):
    """Login: abre a sessão no banco e marca o cookie para ser gravado."""
    ss = st.session_state
    ss.user = dict(user); ss['_token'] = storage.session_create(user['id']); ss.pop('_logged_out', None)


def end():
    """Logout: encerra a sessão no banco e limpa o estado local."""
    storage.session_delete(st.session_state.get('_token') or _read_cookie())
    st.session_state.clear()
    st.session_state['_logged_out'] = True; st.session_state['_nav_restored'] = True


def sync():
    """Mantém cookie e URL em dia com o estado. Chamar uma vez por execução, com o usuário já resolvido."""
    ss = st.session_state
    if ss.get('user') and ss.get('_token'):
        _cookie(ss['_token'], storage.SESSION_DAYS * 86400)
    elif ss.get('_logged_out'):
        _cookie('', 0)
    want = {'e': str(ss.eid), 's': ss.get('section', 'Problema')} if ss.get('user') and ss.get('eid') else {}
    for k in ('e', 's'):
        if k in want:
            if st.query_params.get(k) != want[k]: st.query_params[k] = want[k]
        elif k in st.query_params:
            del st.query_params[k]


def _read_cookie():
    """Token do cookie, ou None quando não há cookie legível (testes, contexto sem navegador)."""
    try: token = st.context.cookies.get(COOKIE)
    except Exception: return None
    return token if isinstance(token, str) and token else None


def _cookie(value, max_age):
    # o token é gerado por secrets.token_urlsafe, então só tem caracteres seguros para cookie
    st.html(
        f"<script>document.cookie='{COOKIE}={value}; path=/; max-age={max_age}; SameSite=Lax'"
        "+(location.protocol==='https:'?'; Secure':'');</script>",
        unsafe_allow_javascript=True,
    )
