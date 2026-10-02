"""Sessão persistente e operações de edição e remoção, sempre contra um banco temporário."""
import pytest

from engine import storage

DATA = {'alternatives': [], 'criteria': [], 'matrix': [], 'c': .7, 'd': .4}


@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, 'DB', tmp_path / 'test.db')
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
