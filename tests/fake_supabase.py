"""Supabase falso, em memória, com o subconjunto do cliente que engine/storage.py usa.

Reproduz o que o esquema de supabase_schema.sql garante: ids por identity, created_at
preenchido pelo banco e as restrições de unicidade (com o mesmo código de erro do Postgres).
"""
from datetime import datetime, timezone
from types import SimpleNamespace

from postgrest.exceptions import APIError

IDENTITY = {'users', 'exercises'}
TIMESTAMPED = {'exercises', 'sessions'}
UNIQUE = {'users': [('email',)], 'exercises': [('code',)], 'participants': [('exercise_id', 'user_id')], 'sessions': [('token',)]}


class FakeSupabase:
    def __init__(self):
        self.tables = {name: [] for name in UNIQUE}
        self.next_id = {name: 1 for name in IDENTITY}

    def table(self, name): return Query(self, name)


class Query:
    def __init__(self, db, name):
        self.db, self.name, self.op, self.payload = db, name, 'select', None
        self.columns, self.filters, self.sort, self.max, self.ignore = '*', [], None, None, False

    def select(self, columns='*'): self.columns = columns; return self
    def insert(self, row): self.op, self.payload = 'insert', row; return self
    def update(self, values): self.op, self.payload = 'update', values; return self
    def delete(self): self.op = 'delete'; return self
    def upsert(self, row, on_conflict='', ignore_duplicates=False):
        assert ignore_duplicates and tuple(on_conflict.split(',')) in UNIQUE[self.name]
        self.op, self.payload, self.ignore = 'insert', row, True; return self

    def eq(self, col, val): self.filters.append(lambda r: r[col] == val); return self
    def in_(self, col, vals): self.filters.append(lambda r: r[col] in vals); return self
    def gte(self, col, val): self.filters.append(lambda r: datetime.fromisoformat(r[col]) >= datetime.fromisoformat(val)); return self
    def order(self, col, desc=False): self.sort = (col, desc); return self
    def limit(self, n): self.max = n; return self

    def execute(self):
        table = self.db.tables[self.name]
        hit = [r for r in table if all(f(r) for f in self.filters)]
        if self.op == 'insert':
            row = dict(self.payload)
            if any(all(r[c] == row[c] for c in cols) for cols in UNIQUE[self.name] for r in table):
                if self.ignore: return SimpleNamespace(data=[])
                raise APIError({'code': '23505', 'message': 'duplicate key value violates unique constraint'})
            if self.name in IDENTITY:
                row['id'] = self.db.next_id[self.name]; self.db.next_id[self.name] += 1
            if self.name in TIMESTAMPED: row.setdefault('created_at', datetime.now(timezone.utc).isoformat())
            table.append(row); hit = [row]
        elif self.op == 'update':
            for r in hit: r.update(self.payload)
        elif self.op == 'delete':
            table[:] = [r for r in table if not any(r is x for x in hit)]
        if self.sort: hit = sorted(hit, key=lambda r: r[self.sort[0]], reverse=self.sort[1])
        if self.max is not None: hit = hit[:self.max]
        keep = None if self.columns == '*' else self.columns.split(',')
        return SimpleNamespace(data=[dict(r) if keep is None else {c: r[c] for c in keep} for r in hit])
