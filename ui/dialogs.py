"""Diálogos de criar, editar e excluir. Toda ação destrutiva pede confirmação aqui."""
import json

import streamlit as st

from core.rules import METHODS, default_data
from engine import storage
from ui import session
from ui.components import esc
from ui.layout import flash


def _confirm_row(danger_label, key):
    """Par Cancelar / ação destrutiva, sempre na mesma ordem. Devolve True se confirmou."""
    cancel, confirm = st.columns(2)
    if cancel.button('Cancelar', width='stretch', key=f'cancel_{key}'): st.rerun()
    with confirm:
        with st.container(key=f'danger_{key}'):
            return st.button(danger_label, width='stretch', key=f'confirm_{key}')


@st.dialog('Novo exercício')
def new_exercise(user):
    with st.form('new', border=False):
        n = st.text_input('Nome do exercício', placeholder='Ex.: Seleção de fornecedores')
        d = st.text_area('Descrição', placeholder='Contexto e objetivo da decisão')
        m = st.radio('Método', METHODS, horizontal=True)
        if st.form_submit_button('Criar exercício', type='primary', width='stretch'):
            if not n.strip(): st.error('Informe um nome para o exercício.')
            else:
                st.session_state.eid = storage.create(user['id'], n, d, m, default_data()); st.session_state.section = 'Problema'; st.rerun()


@st.dialog('Entrar com código')
def join_exercise(user):
    with st.form('join', border=False):
        cd = st.text_input('Código do exercício', placeholder='MCDA-7K4P2', help='Peça o código ao proprietário do exercício.')
        if st.form_submit_button('Entrar no exercício', type='primary', width='stretch'):
            if storage.join(user['id'], cd): flash('Exercício adicionado.'); st.rerun()
            else: st.error('Código não encontrado.')


@st.dialog('Editar exercício')
def edit_exercise(exercise, user):
    with st.form(f'edit_{exercise["id"]}', border=False):
        n = st.text_input('Nome do exercício', value=exercise['name'])
        d = st.text_area('Descrição', value=exercise['description'] or '')
        st.caption(f'O método ({exercise["method"]}) é definido na criação e não pode ser trocado.')
        if st.form_submit_button('Salvar alterações', type='primary', width='stretch'):
            if not n.strip(): st.error('Informe um nome para o exercício.')
            else:
                storage.update(exercise['id'], user['id'], json.loads(exercise['data']), n.strip(), d)
                flash('Exercício atualizado.'); st.rerun()


@st.dialog('Excluir exercício')
def delete_exercise(exercise, user):
    st.html(f'<div class="mcda-prose">Excluir <strong>{esc(exercise["name"])}</strong>? Os dados, a matriz e o acesso dos participantes '
            'são removidos. Esta ação não pode ser desfeita.</div>')
    if _confirm_row('Excluir exercício', f'del_{exercise["id"]}'):
        storage.exercise_delete(exercise['id'], user['id'])
        if st.session_state.get('eid') == exercise['id']: st.session_state.pop('eid', None)
        flash('Exercício excluído.'); st.rerun()


@st.dialog('Sair do exercício')
def leave_exercise(exercise, user):
    st.html(f'<div class="mcda-prose">Sair de <strong>{esc(exercise["name"])}</strong>? Ele some da sua lista, mas continua existindo. '
            f'Para voltar, use o código {esc(exercise["code"])}.</div>')
    if _confirm_row('Sair do exercício', f'leave_{exercise["id"]}'):
        storage.exercise_leave(exercise['id'], user['id'])
        if st.session_state.get('eid') == exercise['id']: st.session_state.pop('eid', None)
        flash('Você saiu do exercício.'); st.rerun()


@st.dialog('Minha conta')
def account(user):
    profile, password, remove = st.tabs(['Perfil', 'Senha', 'Excluir conta'])
    with profile:
        with st.form('acc_profile', border=False):
            name = st.text_input('Nome', value=user.get('name') or '')
            st.text_input('E-mail', value=user.get('email') or '', disabled=True, help='O e-mail identifica a conta e não pode ser alterado.')
            if st.form_submit_button('Salvar perfil', type='primary', width='stretch'):
                if not name.strip(): st.error('Informe um nome.')
                else:
                    storage.user_update(user['id'], name.strip()); st.session_state.user['name'] = name.strip()
                    flash('Perfil atualizado.'); st.rerun()
    with password:
        with st.form('acc_password', border=False):
            current = st.text_input('Senha atual', type='password')
            new = st.text_input('Nova senha', type='password')
            again = st.text_input('Repita a nova senha', type='password')
            if st.form_submit_button('Alterar senha', type='primary', width='stretch'):
                if not new: st.error('Informe a nova senha.')
                elif new != again: st.error('As duas senhas novas não coincidem.')
                elif not storage.user_set_password(user['id'], current, new): st.error('A senha atual não confere.')
                else: flash('Senha alterada.'); st.rerun()
    with remove:
        st.html('<div class="mcda-prose">Excluir a conta remove também os exercícios que você criou e sua participação nos demais. '
                'Esta ação não pode ser desfeita.</div>')
        typed = st.text_input('Digite seu e-mail para confirmar', placeholder=user.get('email') or '')
        if _confirm_row('Excluir minha conta', 'account'):
            if typed.strip().lower() != (user.get('email') or '').lower(): st.error('O e-mail digitado não confere.')
            else:
                storage.user_delete(user['id']); session.end(); st.rerun()
