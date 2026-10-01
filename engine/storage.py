import sqlite3, json, hashlib, secrets, string
from pathlib import Path
DB=Path(__file__).resolve().parent.parent/'mcda_lab.db'
def con():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
 with con() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,email TEXT UNIQUE,name TEXT,password TEXT); CREATE TABLE IF NOT EXISTS exercises(id INTEGER PRIMARY KEY,owner_id INTEGER,name TEXT,description TEXT,method TEXT,code TEXT UNIQUE,data TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP); CREATE TABLE IF NOT EXISTS participants(exercise_id INTEGER,user_id INTEGER,UNIQUE(exercise_id,user_id));''')
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
