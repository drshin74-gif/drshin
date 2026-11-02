"""SQLite persistence; demo/local use only. Not a multi-tenant production security boundary."""
import sqlite3,json,datetime,hashlib,os
from pathlib import Path
DB=Path(os.getenv('BIZDNA_DB',str(Path(__file__).parent/'bizdna_demo.sqlite3')))
def connect():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');return c
def init():
 with connect() as c:
  c.execute('''CREATE TABLE IF NOT EXISTS assessments(id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, shop_key TEXT NOT NULL, shop_name TEXT NOT NULL, sector TEXT NOT NULL, district TEXT NOT NULL, consent INTEGER NOT NULL, model_version TEXT NOT NULL, input_json TEXT NOT NULL, result_json TEXT NOT NULL)''')
  c.execute('CREATE INDEX IF NOT EXISTS idx_district ON assessments(district,sector)')
def save(payload,result,district,consent):
 if not consent:raise ValueError('저장 동의가 필요합니다.')
 if not district.strip():raise ValueError('상권명은 필수입니다.')
 profile=payload['profile']; name=profile['name'].strip()
 if not name:raise ValueError('점포명은 필수입니다.')
 key=hashlib.sha256((district.strip()+'|'+name).encode()).hexdigest()[:16]
 with connect() as c:
  cur=c.execute('INSERT INTO assessments(created_at,shop_key,shop_name,sector,district,consent,model_version,input_json,result_json) VALUES(?,?,?,?,?,?,?,?,?)',(datetime.datetime.now(datetime.timezone.utc).isoformat(),key,name,profile['sector'],district.strip(),1,result.get('model_version','v5'),json.dumps(payload,ensure_ascii=False),json.dumps(result,ensure_ascii=False)))
  return cur.lastrowid
def records():
 with connect() as c:return [dict(r) for r in c.execute('SELECT id,created_at,shop_key,shop_name,sector,district,model_version,result_json FROM assessments ORDER BY id DESC')]
def get(id):
 with connect() as c:
  r=c.execute('SELECT * FROM assessments WHERE id=?',(id,)).fetchone();return dict(r) if r else None
def delete(id):
 with connect() as c:return c.execute('DELETE FROM assessments WHERE id=?',(id,)).rowcount
