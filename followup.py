"""Follow-up measurement and action tracking. Local demonstration only."""
import sqlite3, datetime, json
from storage import connect

def init_followup():
    with connect() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS actions (id INTEGER PRIMARY KEY, assessment_id INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE, strategy TEXT NOT NULL, task TEXT NOT NULL, owner TEXT NOT NULL, due_date TEXT, status TEXT NOT NULL DEFAULT '계획', created_at TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS kpi_measurements (id INTEGER PRIMARY KEY, assessment_id INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE, measured_on TEXT NOT NULL, monthly_sales REAL, monthly_cost REAL, monthly_rent REAL, repeat_rate REAL, note TEXT, created_at TEXT NOT NULL, CHECK(monthly_sales IS NULL OR monthly_sales>=0), CHECK(monthly_cost IS NULL OR monthly_cost>=0), CHECK(repeat_rate IS NULL OR (repeat_rate>=0 AND repeat_rate<=100)))''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_kpi_assessment ON kpi_measurements(assessment_id,measured_on)')

def add_action(assessment_id,strategy,task,owner,due_date=None):
    if not strategy.strip() or not task.strip() or not owner.strip():raise ValueError('전략, 실행과제, 담당자 필수')
    with connect() as c:
        c.execute('INSERT INTO actions(assessment_id,strategy,task,owner,due_date,created_at) VALUES(?,?,?,?,?,?)',(assessment_id,strategy,task,owner,due_date,datetime.datetime.now(datetime.timezone.utc).isoformat()))

def update_action(action_id,status):
    if status not in ('계획','진행','완료','보류'):raise ValueError('허용되지 않는 상태')
    with connect() as c:c.execute('UPDATE actions SET status=? WHERE id=?',(status,action_id))

def actions(assessment_id):
    with connect() as c:return [dict(x) for x in c.execute('SELECT * FROM actions WHERE assessment_id=? ORDER BY id',(assessment_id,))]

def add_measurement(assessment_id,date,sales,cost,rent=None,repeat=None,note=''):
    if sales<0 or cost<0 or (rent is not None and rent<0):raise ValueError('금액은 음수 불가')
    if repeat is not None and not 0<=repeat<=100:raise ValueError('재방문율 범위 오류')
    datetime.date.fromisoformat(date)
    with connect() as c:c.execute('INSERT INTO kpi_measurements(assessment_id,measured_on,monthly_sales,monthly_cost,monthly_rent,repeat_rate,note,created_at) VALUES(?,?,?,?,?,?,?,?)',(assessment_id,date,sales,cost,rent,repeat,note,datetime.datetime.now(datetime.timezone.utc).isoformat()))

def measurements(assessment_id):
    with connect() as c:return [dict(x) for x in c.execute('SELECT * FROM kpi_measurements WHERE assessment_id=? ORDER BY measured_on,id',(assessment_id,))]

def evaluate(assessment_id):
    from storage import get
    rec=get(assessment_id)
    if rec is None:raise ValueError('진단기록 없음')
    p=json.loads(rec['input_json'])['profile']; base_s=p.get('monthly_sales');base_c=p.get('monthly_cost')
    series=measurements(assessment_id)
    if not series:return {'baseline_sales':base_s,'baseline_profit':None if base_s is None or base_c is None else base_s-base_c,'measurements':[],'caution':'후속 측정자료 없음'}
    out=[]
    for r in series:
        s=r['monthly_sales'];c=r['monthly_cost'];profit=None if s is None or c is None else s-c
        growth=None if not base_s or s is None else round((s/base_s-1)*100,2)
        out.append({'date':r['measured_on'],'sales':s,'cost':c,'operating_surplus_proxy':profit,'sales_change_from_baseline_pct':growth,'repeat_rate':r['repeat_rate']})
    return {'baseline_sales':base_s,'baseline_profit':None if base_s is None or base_c is None else base_s-base_c,'measurements':out,'caution':'매출-입력비용은 단순 영업잔여액이며 회계상 영업이익과 다를 수 있음. 개선효과는 인과적 정책효과를 의미하지 않음.'}
