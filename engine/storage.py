"""Persistência no Supabase (PostgreSQL). O esquema fica em supabase_schema.sql."""
import json, hashlib, os, secrets, string
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from dotenv import dotenv_values, load_dotenv
from postgrest.exceptions import APIError
from supabase import create_client

load_dotenv()

SESSION_DAYS = 30
UNIQUE_VIOLATION = '23505'


def setting(key):
    """Credencial vinda de st.secrets (Streamlit Cloud) ou, na falta, do ambiente (.env local)."""
    try:
        import streamlit as st
        if key in st.secrets and st.secrets[key]: return str(st.secrets[key])
    except Exception:
        pass  # sem secrets.toml, ou fora do Streamlit
    # o Streamlit copia o secrets.toml para o ambiente; se ele estiver em branco, apaga o valor
    # que o load_dotenv() carregou, então o .env é relido como último recurso
    return os.getenv(key) or dotenv_values().get(key) or None


@lru_cache(maxsize=1)
def client():
    url, key = setting('SUPABASE_URL'), setting('SUPABASE_KEY')
    if not url or not key:
        raise RuntimeError('Defina SUPABASE_URL e SUPABASE_KEY no .env (local) ou nos secrets do Streamlit Cloud.')
    return create_client(url, key)


def t(name): return client().table(name)
def rows(q): return q.execute().data or []
def one(q):
    r = rows(q.limit(1)); return r[0] if r else None
def owns(eid, uid): return one(t('exercises').select('id').eq('id', eid).eq('owner_id', uid)) is not None


def init():
    """As tabelas são criadas pelo supabase_schema.sql; aqui só se confere a configuração."""
    client()


def h(p): return hashlib.sha256(p.encode()).hexdigest()
def register(name,email,password):
 try: t('users').insert({'name':name,'email':email.lower(),'password':h(password)}).execute()
 except APIError as e:
  if e.code!=UNIQUE_VIOLATION: raise
  return False,'E-mail já cadastrado.'
 return True,None
def login(email,password): return one(t('users').select('*').eq('email',email.lower()).eq('password',h(password)))
def code(): return 'MCDA-'+''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(5))
def create(uid,name,desc,method,data):
 return rows(t('exercises').insert({'owner_id':uid,'name':name,'description':desc,'method':method,'code':code(),'data':json.dumps(data)}))[0]['id']
def update(eid,uid,data,name=None,desc=None):
 ex=one(t('exercises').select('*').eq('id',eid).eq('owner_id',uid))
 if not ex:return False
 t('exercises').update({'data':json.dumps(data),'name':name or ex['name'],'description':desc if desc is not None else ex['description']}).eq('id',eid).execute();return True
def list_for(uid):
 found={e['id']:e for e in rows(t('exercises').select('*').eq('owner_id',uid))}
 joined=[p['exercise_id'] for p in rows(t('participants').select('exercise_id').eq('user_id',uid))]
 if joined: found.update({e['id']:e for e in rows(t('exercises').select('*').in_('id',joined))})
 return sorted(found.values(),key=lambda e:e['id'],reverse=True)
def get(eid,uid):
 e=one(t('exercises').select('*').eq('id',eid))
 if not e:return None
 if e['owner_id']==uid or one(t('participants').select('user_id').eq('exercise_id',eid).eq('user_id',uid)):return e
 return None
def join(uid,cd):
 e=one(t('exercises').select('id').eq('code',cd.upper().strip()))
 if not e:return False
 t('participants').upsert({'exercise_id':e['id'],'user_id':uid},on_conflict='exercise_id,user_id',ignore_duplicates=True).execute();return True


# ── Sessão persistente e operações de edição e remoção ─────────────────────────


def session_create(uid):
    """Abre uma sessão e devolve o token que vai para o cookie; o banco guarda só o hash."""
    token = secrets.token_urlsafe(32)
    t('sessions').insert({'token': h(token), 'user_id': uid}).execute()
    return token


def session_user(token):
    """Usuário dono de um token válido e não expirado, ou None."""
    if not token: return None
    since = (datetime.now(timezone.utc) - timedelta(days=SESSION_DAYS)).isoformat()
    s = one(t('sessions').select('user_id').eq('token', h(token)).gte('created_at', since))
    return one(t('users').select('*').eq('id', s['user_id'])) if s else None


def session_delete(token):
    if not token: return
    t('sessions').delete().eq('token', h(token)).execute()


def user_update(uid, name):
    t('users').update({'name': name}).eq('id', uid).execute()


def user_set_password(uid, current, new):
    """Troca a senha se a atual conferir."""
    if not one(t('users').select('id').eq('id', uid).eq('password', h(current))): return False
    t('users').update({'password': h(new)}).eq('id', uid).execute()
    return True


def user_delete(uid):
    """Remove a conta, os exercícios que ela possui, suas participações e sessões."""
    owned = [e['id'] for e in rows(t('exercises').select('id').eq('owner_id', uid))]
    if owned: t('participants').delete().in_('exercise_id', owned).execute()
    t('exercises').delete().eq('owner_id', uid).execute()
    t('participants').delete().eq('user_id', uid).execute()
    t('sessions').delete().eq('user_id', uid).execute()
    t('users').delete().eq('id', uid).execute()


def exercise_delete(eid, uid):
    """Exclui o exercício e suas participações. Só o proprietário pode."""
    if not owns(eid, uid): return False
    t('participants').delete().eq('exercise_id', eid).execute()
    t('exercises').delete().eq('id', eid).execute()
    return True


def exercise_leave(eid, uid):
    """O participante sai do exercício; o exercício continua existindo."""
    t('participants').delete().eq('exercise_id', eid).eq('user_id', uid).execute()


def participants(eid, uid):
    """Participantes de um exercício, visíveis apenas ao proprietário."""
    if not owns(eid, uid): return []
    ids = [p['user_id'] for p in rows(t('participants').select('user_id').eq('exercise_id', eid))]
    return rows(t('users').select('id,name,email').in_('id', ids).order('name')) if ids else []


def participant_remove(eid, owner_id, user_id):
    if not owns(eid, owner_id): return False
    t('participants').delete().eq('exercise_id', eid).eq('user_id', user_id).execute()
    return True
