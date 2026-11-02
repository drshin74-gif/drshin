"""Aggregate *latest* assessment per shop; avoid duplicate weighting."""
import json,collections,statistics

def aggregate(rows,sector=None,district=None,min_group=5):
 latest={}
 for row in rows:
  if sector and row['sector']!=sector:continue
  if district and row['district']!=district:continue
  latest.setdefault(row['shop_key'],row)
 records=list(latest.values()); n=len(records)
 if n<min_group:return {'n':n,'suppressed':True,'message':f'집계 대상 {n}개 점포: 최소 {min_group}개 미만이므로 통계 비공개'}
 parsed=[json.loads(x['result_json']) for x in records]
 scores=[float(x['overall']) for x in parsed]
 areas=collections.defaultdict(list)
 for x in parsed:
  for k,v in x['scores'].items():areas[k].append(float(v))
 types=collections.Counter(x['dna_code'] for x in parsed)
 risks=collections.Counter(r['code'] if 'code' in r else r.get('text','위험') for x in parsed for r in x.get('risks',[]))
 strategies=collections.Counter(s['title'] for x in parsed for s in x.get('strategies',[])[:3])
 return {'n':n,'suppressed':False,'overall_mean':round(statistics.mean(scores),2),'overall_median':round(statistics.median(scores),2),'areas':{k:round(statistics.mean(v),2) for k,v in areas.items()},'dna_types':dict(types),'risk_counts':dict(risks),'strategy_top3_counts':dict(strategies),'note':'자가진단 표본의 기술통계. 모집단 대표성·인과효과·공식 상권 평균을 의미하지 않음.'}
