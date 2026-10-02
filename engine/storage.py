import sqlite3, json, hashlib, secrets, string
from pathlib import Path
DB=Path(__file__).resolve().parent.parent/'mcda_lab.db'
def con():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
 with con() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,email TEXT UNIQUE,name TEXT,password TEXT); CREATE TABLE IF NOT EXISTS exercises(id INTEGER PRIMARY KEY,owner_id INTEGER,name TEXT,description TEXT,method TEXT,code TEXT UNIQUE,data TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP); CREATE TABLE IF NOT EXISTS participants(exercise_id INTEGER,user_id INTEGER,UNIQUE(exercise_id,user_id));''')
  c.executescript(EXTRA_SCHEMA)
def h(p): return hashlib.sha256(p.encode()).hexdigest()
def register(name,email,password):
 try:
  with con() as c: c.execute('INSERT INTO users(name,email,password) VALUES(?,?,?)',(name,email.lower(),h(password)))
  return True,None
 except Exception as e:return False,'E-mail já cadastrado.'
def login(email,password):
 with con() as c:return c.execute('SELECT * FROM users WHERE email=? AND password=?',(email.lower(),h(password))).fetchone()
def code(): return 'MCDA-'+''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(5))
def create(uid,name,desc,method,data):
 with con() as c:
  cd=code(); cur=c.execute('INSERT INTO exercises(owner_id,name,description,method,code,data) VALUES(?,?,?,?,?,?)',(uid,name,desc,method,cd,json.dumps(data))); return cur.lastrowid
def update(eid,uid,data,name=None,desc=None):
 with con() as c:
  ex=c.execute('SELECT * FROM exercises WHERE id=? AND owner_id=?',(eid,uid)).fetchone()
  if not ex:return False
  c.execute('UPDATE exercises SET data=?,name=?,description=? WHERE id=?',(json.dumps(data),name or ex['name'],desc if desc is not None else ex['description'],eid));return True
def list_for(uid):
 with con() as c:return c.execute('''SELECT DISTINCT e.* FROM exercises e LEFT JOIN participants p ON p.exercise_id=e.id WHERE e.owner_id=? OR p.user_id=? ORDER BY e.id DESC''',(uid,uid)).fetchall()
def get(eid,uid):
 with con() as c:return c.execute('''SELECT DISTINCT e.* FROM exercises e LEFT JOIN participants p ON p.exercise_id=e.id WHERE e.id=? AND (e.owner_id=? OR p.user_id=?)''',(eid,uid,uid)).fetchone()
def join(uid,cd):
 with con() as c:
  e=c.execute('SELECT id FROM exercises WHERE code=?',(cd.upper().strip(),)).fetchone()
  if not e:return False
  c.execute('INSERT OR IGNORE INTO participants(exercise_id,user_id) VALUES(?,?)',(e['id'],uid));return True


# ── Acréscimos: sessão persistente e operações de edição e remoção ──────────────
# Só adicionam tabela e funções; o esquema e as funções acima seguem como estavam.
EXTRA_SCHEMA = 'CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP);'
SESSION_DAYS = 30


def session_create(uid):
    """Abre uma sessão e devolve o token que vai para o cookie; o banco guarda só o hash."""
    token = secrets.token_urlsafe(32)
    with con() as c: c.execute('INSERT INTO sessions(token,user_id) VALUES(?,?)', (h(token), uid))
    return token


def session_user(token):
    """Usuário dono de um token válido e não expirado, ou None."""
    if not token: return None
    with con() as c:
        return c.execute(
            f"""SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id
                WHERE s.token=? AND s.created_at>=datetime('now','-{SESSION_DAYS} days')""", (h(token),)).fetchone()


def session_delete(token):
    if not token: return
    with con() as c: c.execute('DELETE FROM sessions WHERE token=?', (h(token),))


def user_update(uid, name):
    with con() as c: c.execute('UPDATE users SET name=? WHERE id=?', (name, uid))


def user_set_password(uid, current, new):
    """Troca a senha se a atual conferir."""
    with con() as c:
        ok = c.execute('SELECT 1 FROM users WHERE id=? AND password=?', (uid, h(current))).fetchone()
        if not ok: return False
        c.execute('UPDATE users SET password=? WHERE id=?', (h(new), uid))
        return True


def user_delete(uid):
    """Remove a conta, os exercícios que ela possui, suas participações e sessões."""
    with con() as c:
        c.execute('DELETE FROM participants WHERE exercise_id IN (SELECT id FROM exercises WHERE owner_id=?)', (uid,))
        c.execute('DELETE FROM exercises WHERE owner_id=?', (uid,))
        c.execute('DELETE FROM participants WHERE user_id=?', (uid,))
        c.execute('DELETE FROM sessions WHERE user_id=?', (uid,))
        c.execute('DELETE FROM users WHERE id=?', (uid,))


def exercise_delete(eid, uid):
    """Exclui o exercício e suas participações. Só o proprietário pode."""
    with con() as c:
        if not c.execute('SELECT 1 FROM exercises WHERE id=? AND owner_id=?', (eid, uid)).fetchone(): return False
        c.execute('DELETE FROM participants WHERE exercise_id=?', (eid,))
        c.execute('DELETE FROM exercises WHERE id=?', (eid,))
        return True


def exercise_leave(eid, uid):
    """O participante sai do exercício; o exercício continua existindo."""
    with con() as c: c.execute('DELETE FROM participants WHERE exercise_id=? AND user_id=?', (eid, uid))


def participants(eid, uid):
    """Participantes de um exercício, visíveis apenas ao proprietário."""
    with con() as c:
        if not c.execute('SELECT 1 FROM exercises WHERE id=? AND owner_id=?', (eid, uid)).fetchone(): return []
        return c.execute('SELECT u.id,u.name,u.email FROM participants p JOIN users u ON u.id=p.user_id WHERE p.exercise_id=? ORDER BY u.name', (eid,)).fetchall()


def participant_remove(eid, owner_id, user_id):
    with con() as c:
        if not c.execute('SELECT 1 FROM exercises WHERE id=? AND owner_id=?', (eid, owner_id)).fetchone(): return False
        c.execute('DELETE FROM participants WHERE exercise_id=? AND user_id=?', (eid, user_id))
        return True
