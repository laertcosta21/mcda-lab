import streamlit as st

from engine import storage
from ui.components import footer, steps

FLOW = ['Problema', 'Critérios', 'Preferências', 'Comparações', 'Fluxos / sobreclassificação', 'Análise']


def render():
    """Tela de acesso. Devolve True quando já existe usuário na sessão."""
    if st.session_state.get('user'): return True
    with st.container(key='login'):
        left, right = st.columns([1.15, .85], gap='large', vertical_alignment='center')
        with left:
            st.html(
                '<div class="mcda-hero"><div class="mcda-eyebrow">Laboratório acadêmico · UFMS</div>'
                '<h1>Decisão multicritério, explicada passo a passo.</h1>'
                '<div class="mcda-lead">Construa problemas, compare alternativas e compreenda visualmente PROMETHEE II e ELECTRE I, '
                'do dado bruto à análise de sensibilidade.</div>'
                + steps(FLOW) + '</div>'
            )
        with right:
            with st.container(border=True, key='login_card'):
                st.html('<div class="mcda-brand-kicker">Acesso</div><div class="mcda-brand-name">MCDA Lab</div>')
                tabs = st.tabs(['Entrar', 'Criar conta'])
                with tabs[0]:
                    with st.form('login', border=False):
                        e = st.text_input('E-mail', placeholder='nome@exemplo.com')
                        p = st.text_input('Senha', type='password')
                        if st.form_submit_button('Entrar', type='primary', width='stretch'):
                            u = storage.login(e, p)
                            if u:
                                st.session_state.user = dict(u); st.session_state.section = 'Problema'; st.rerun()
                            else: st.error('E-mail ou senha inválidos.')
                with tabs[1]:
                    with st.form('reg', border=False):
                        n = st.text_input('Nome')
                        e = st.text_input('E-mail', key='reg_email', placeholder='nome@exemplo.com')
                        p = st.text_input('Senha', type='password', key='reg_pass')
                        if st.form_submit_button('Criar conta', type='primary', width='stretch'):
                            ok, msg = storage.register(n, e, p)
                            if ok: st.success('Conta criada. Agora você pode entrar.')
                            else: st.error(msg)
                st.html('<div class="mcda-login-note">Ao acessar, você reconhece o caráter didático do laboratório. '
                        'Os resultados apoiam a análise e não substituem o julgamento do decisor.</div>')
        footer()
    return False
