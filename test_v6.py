import tempfile,os,json
from pathlib import Path
with tempfile.TemporaryDirectory() as d:
 os.environ['BIZDNA_DB']=str(Path(d)/'test.sqlite3')
 import storage
 from analytics import aggregate
 from advanced import diagnose_v4
 storage.init()
 p=json.loads((Path(__file__).parent/'sample_cafe.json').read_text(encoding='utf-8'))
 r=diagnose_v4(p)
 assert 0<=r['overall']<=100
 assert aggregate(storage.records())['suppressed']
 try:storage.save(p,r,'A',False);assert False
 except ValueError:pass
 for i in range(5):
  q=json.loads(json.dumps(p));q['profile']['name']=f'점포{i}';storage.save(q,diagnose_v4(q),'A',True)
 out=aggregate(storage.records(),district='A');assert out['n']==5 and not out['suppressed']
 assert len(out['areas'])==8
 storage.save(q,diagnose_v4(q),'A',True)
 assert aggregate(storage.records(),district='A')['n']==5
 assert storage.delete(1)==1
 assert aggregate(storage.records(),district='A')['suppressed']
 print('PASS: diagnosis, consent, suppression, deduplication, aggregation, delete')
