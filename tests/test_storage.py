"""Sessão persistente e operações de edição e remoção, sempre contra um Supabase falso em memória."""
import pytest
import streamlit as st

from engine import storage
from fake_supabase import FakeSupabase

DATA = {'alternatives': [], 'criteria': [], 'matrix': [], 'c': .7, 'd': .4}


@pytest.fixture
def db(monkeypatch):
    fake = FakeSupabase()
    monkeypatch.setattr(storage, 'client', lambda: fake)
    monkeypatch.setattr(storage, 'BCRYPT_ROUNDS', 4)  # custo mínimo: os testes não medem a força do hash
    storage.init()
    storage.register('Ana', 'ana@x.test', 'senha-a'); storage.register('Bia', 'bia@x.test', 'senha-b')
    return storage.login('ana@x.test', 'senha-a')['id'], storage.login('bia@x.test', 'senha-b')['id']


def test_session_survives_until_logout(db):
    ana, _ = db
    token = storage.session_create(ana)
    assert storage.session_user(token)['email'] == 'ana@x.test'
    assert storage.session_user('token-inventado') is None and storage.session_user(None) is None
    storage.session_delete(token)
    assert storage.session_user(token) is None


def test_only_owner_deletes_exercise(db):
    ana, bia = db
    eid = storage.create(ana, 'Ex', '', 'PROMETHEE II', DATA)
    storage.join(bia, storage.get(eid, ana)['code'])
    assert storage.exercise_delete(eid, bia) is False and storage.get(eid, ana) is not None
    assert storage.exercise_delete(eid, ana) is True
    assert storage.get(eid, ana) is None and storage.list_for(bia) == []


def test_participants_are_listed_removed_and_can_leave(db):
    ana, bia = db
    eid = storage.create(ana, 'Ex', '', 'ELECTRE I', DATA)
    code = storage.get(eid, ana)['code']
    storage.join(bia, code)
    assert [p['email'] for p in storage.participants(eid, ana)] == ['bia@x.test']
    assert storage.participants(eid, bia) == []
    assert storage.participant_remove(eid, bia, bia) is False
    assert storage.participant_remove(eid, ana, bia) is True and storage.list_for(bia) == []
    storage.join(bia, code); storage.exercise_leave(eid, bia)
    assert storage.list_for(bia) == [] and storage.get(eid, ana) is not None


def test_profile_password_and_account_removal(db):
    ana, bia = db
    storage.user_update(ana, 'Ana Lima')
    assert storage.login('ana@x.test', 'senha-a')['name'] == 'Ana Lima'
    assert storage.user_set_password(ana, 'errada', 'nova') is False
    assert storage.user_set_password(ana, 'senha-a', 'nova') is True
    assert storage.login('ana@x.test', 'senha-a') is None and storage.login('ana@x.test', 'nova') is not None
    eid = storage.create(ana, 'Ex', '', 'PROMETHEE II', DATA)
    storage.join(bia, storage.get(eid, ana)['code'])
    token = storage.session_create(ana)
    storage.user_delete(ana)
    assert storage.login('ana@x.test', 'nova') is None and storage.session_user(token) is None
    assert storage.list_for(bia) == []


def test_duplicate_email_and_duplicate_join_are_harmless(db):
    ana, bia = db
    assert storage.register('Outra Ana', 'ANA@x.test', 'x') == (False, 'E-mail já cadastrado.')
    eid = storage.create(ana, 'Ex', '', 'ELECTRE I', DATA)
    code = storage.get(eid, ana)['code']
    assert storage.join(bia, code) is True and storage.join(bia, code) is True
    assert storage.join(bia, 'MCDA-XXXXX') is False
    assert [e['id'] for e in storage.list_for(bia)] == [eid] and storage.get(eid, bia)['id'] == eid
    assert storage.update(eid, bia, DATA) is False and storage.update(eid, ana, DATA, 'Novo') is True
    assert storage.get(eid, ana)['name'] == 'Novo'


def test_expired_session_is_rejected(db, monkeypatch):
    ana, _ = db
    token = storage.session_create(ana)
    monkeypatch.setattr(storage, 'SESSION_DAYS', -1)
    assert storage.session_user(token) is None


def test_credentials_come_from_secrets_then_environment(monkeypatch):
    monkeypatch.setenv('SUPABASE_URL', 'https://env.test')
    monkeypatch.setattr(st, 'secrets', {'SUPABASE_URL': 'https://secrets.test'})
    assert storage.setting('SUPABASE_URL') == 'https://secrets.test'
    monkeypatch.setattr(st, 'secrets', {'SUPABASE_URL': ''})
    assert storage.setting('SUPABASE_URL') == 'https://env.test'
    monkeypatch.setenv('SUPABASE_URL', '')  # é o que um secrets.toml em branco deixa no ambiente
    monkeypatch.setattr(storage, 'dotenv_values', lambda: {'SUPABASE_URL': 'https://dotenv.test'})
    assert storage.setting('SUPABASE_URL') == 'https://dotenv.test'
    monkeypatch.setattr(storage, 'dotenv_values', lambda: {'SUPABASE_URL': ''})
    assert storage.setting('SUPABASE_URL') is None


def test_passwords_are_stored_with_bcrypt_and_old_hashes_are_upgraded(db):
    ana, _ = db
    stored = lambda: storage.t('users').select('password').eq('id', ana).execute().data[0]['password']
    assert stored().startswith('$2') and 'senha-a' not in stored()
    assert storage.hash_password('senha-a') != storage.hash_password('senha-a')  # salt por senha
    longa = 'x' * 100
    assert storage.user_set_password(ana, 'senha-a', longa) is True
    assert storage.login('ana@x.test', longa) is not None and storage.login('ana@x.test', longa + 'y') is None
    storage.t('users').update({'password': storage.h('antiga')}).eq('id', ana).execute()  # conta da era SHA-256
    assert storage.login('ana@x.test', 'errada') is None and not stored().startswith('$2')
    assert storage.login('ana@x.test', 'antiga')['id'] == ana and stored().startswith('$2')
    assert storage.login('ana@x.test', 'antiga')['id'] == ana
