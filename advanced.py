"""Biz-DNA v4: sector-specific diagnostics, observable trends, benchmarking and traceable recommendations."""
from math import isfinite
from engine import diagnose, AREAS
SECTOR_QUESTIONS = {
 '외식업': {'상품·서비스':['대표메뉴별 원가율을 확인한다','식재료 폐기율을 정기적으로 기록한다','메뉴별 판매량과 이익기여도를 분석한다','위생점검 결과를 개선에 반영한다'], '고객관리':['재방문 고객을 구분해 관리한다','시간대별 고객 특성을 파악한다','고객 리뷰에 대응하는 기준이 있다','혼잡시간 대기와 회전율을 관리한다'], '점포운영':['발주량을 판매예측에 따라 조정한다','피크시간대 인력을 배치한다','조리·서비스 매뉴얼이 있다','식재료 보관·위생 점검기록이 있다']},
 '도소매업': {'상품·서비스':['품목별 매출총이익을 관리한다','비인기·장기재고 상품을 파악한다','상품구색을 고객수요에 맞게 조정한다','가격 비교와 경쟁상품 조사를 수행한다'], '고객관리':['구매주기별 고객을 관리한다','고객별 선호상품을 분석한다','교환·반품 사유를 기록한다','단골고객 재구매를 유도한다'], '점포운영':['재고회전일수를 확인한다','품절과 과잉재고를 관리한다','거래처별 납기·조건을 비교한다','온라인·오프라인 재고를 일치시킨다']},
 '생활서비스업': {'상품·서비스':['서비스별 소요시간과 수익성을 파악한다','서비스 결과의 품질기준이 있다','추가서비스의 필요성을 검토한다','고객별 서비스 이력을 관리한다'], '고객관리':['예약·재방문 주기를 관리한다','고객 이탈·불만 원인을 기록한다','재방문 알림을 운영한다','고객 동의에 따라 연락처를 관리한다'], '점포운영':['예약·노쇼를 관리한다','인력별 업무배분을 관리한다','서비스별 표준 소요시간이 있다','장비·소모품 점검계획이 있다']},
}
SECTOR_WEIGHTS={
 '외식업':{'상권·입지':12,'상품·서비스':17,'고객관리':14,'마케팅·판로':9,'재무·수익':23,'점포운영':12,'디지털':4,'경영자·미래대응':9},
 '도소매업':{'상권·입지':15,'상품·서비스':15,'고객관리':12,'마케팅·판로':10,'재무·수익':21,'점포운영':14,'디지털':5,'경영자·미래대응':8},
 '생활서비스업':{'상권·입지':10,'상품·서비스':16,'고객관리':20,'마케팅·판로':11,'재무·수익':19,'점포운영':11,'디지털':5,'경영자·미래대응':8}}
STAGE_RULES=[('S1','시장검증기'),('S2','사업기반 구축기'),('S3','안정운영기'),('S4','성장확장기'),('S5','규모화·전환기')]
def _num(x,label):
 try: v=float(x)
 except (ValueError,TypeError): raise ValueError(f'{label}: 숫자가 필요합니다')
 if not isfinite(v) or v<0:raise ValueError(f'{label}: 0 이상의 유한한 숫자가 필요합니다')
 return v

def diagnose_v4(payload):
 r=diagnose(payload)
 p=payload['profile']; sector=p.get('sector','기타'); weights=SECTOR_WEIGHTS.get(sector,AREAS)
 r['overall']=round(sum(r['scores'][k]*w for k,w in weights.items())/100,2)
 r['weights']=weights
 r['model_version']='4.0-pilot'
 r['sector_diagnostics']={}
 supplemental=payload.get('sector_answers',{})
 for area,questions in SECTOR_QUESTIONS.get(sector,{}).items():
  values=supplemental.get(area)
  if values is None:continue
  if len(values)!=len(questions) or any(type(v)!=int or v<1 or v>5 for v in values):raise ValueError(f'업종 특화 {area}: 1~5점 정수 4개 필요')
  sector_score=round(sum(v-1 for v in values)/16*100,2)
  # Blend common and sector module; weights remain sector-specific.
  r['scores'][area]=round(.65*r['scores'][area]+.35*sector_score,2)
  r['sector_diagnostics'][area]={'score':sector_score,'questions':questions}
 if r['sector_diagnostics']:
  r['overall']=round(sum(r['scores'][k]*w for k,w in weights.items())/100,2)
  r['strengths']=sorted(r['scores'],key=lambda a:-r['scores'][a])[:2]
  r['weaknesses']=sorted(r['scores'],key=lambda a:r['scores'][a])[:2]
 # Re-run strategy priority after applying optional sector-specific scores.
 for st in r['strategies']:
  area=st['area']; st['gap']=round(100-r['scores'][area],2)
  st['priority']=round(.45*st['gap']+.35*st['fit']+.20*st['feasibility'],2)
  if st['gated']:st['priority']=min(st['priority'],35)
  st['rationale']=f"업종보정 역량 {r['scores'][area]:.1f}점, 적합도 {st['fit']:.0f}점, 실행가능성 {st['feasibility']:.0f}점"
 r['strategies'].sort(key=lambda x:-x['priority'])
 # Optional observed data; never infer a stage when evidence is missing.
 obs=payload.get('observations',{})
 valid_keys=['sales_prev','repeat_rate','months_operating','channels','staff','positive_cashflow_months']
 clean={k:_num(obs[k],k) for k in valid_keys if obs.get(k) not in (None,'')}
 if 'sales_prev' in clean:
  prev=clean['sales_prev']; curr=_num(p['monthly_sales'],'monthly_sales')
  r['sales_growth_pct']=round((curr/prev-1)*100,2) if prev>0 else None
 else:r['sales_growth_pct']=None
 # Explicit evidence gates, not an asserted validated lifecycle model.
 stage=None
 if all(k in clean for k in ['months_operating','repeat_rate','positive_cashflow_months']):
  months,repeat,positive=clean['months_operating'],clean['repeat_rate'],clean['positive_cashflow_months']
  if repeat>100 or positive>12:raise ValueError('재방문율은 0~100%, 흑자월수는 0~12 범위')
  if months<6 or repeat<10:stage=STAGE_RULES[0]
  elif months<12 or repeat<25:stage=STAGE_RULES[1]
  elif positive<9 or r['sales_growth_pct'] is None:stage=STAGE_RULES[2]
  elif r['sales_growth_pct']>=15 and clean.get('channels',0)>=2 and clean.get('staff',0)>=2:stage=STAGE_RULES[3]
  else:stage=STAGE_RULES[2]
  # S5 cannot be confirmed with these limited inputs.
 r['stage']={'code':stage[0],'label':stage[1],'reason':'입력된 운영기간·재방문·흑자월수·매출추세에 따른 잠정 판정'} if stage else {'code':'UNDETERMINED','label':'성장단계 미판정','reason':'운영기간·재방문율·최근 12개월 흑자월수 등 필수 증빙 미입력'}
 r['observations']=clean
 # User-supplied comparator only, never presented as population norm.
 benchmark=payload.get('benchmark')
 if benchmark:
  val=_num(benchmark.get('monthly_sales'),'비교기준 월매출')
  r['benchmark']={'source':benchmark.get('source','사용자 입력 비교기준'),'monthly_sales':val,'gap_pct':round((float(p['monthly_sales'])/val-1)*100,2) if val>0 else None,'warning':'사용자 제공 참고값이며 공식 업종 평균으로 검증되지 않음'}
 else:r['benchmark']=None
 r['confidence']={'level':'보통' if stage and len(r['sector_diagnostics'])==3 else '제한적','evidence_count':len(clean),'sector_modules':len(r['sector_diagnostics']),'note':'자가응답 기반. 외부 카드매출·상권 데이터 검증 전 단계'}
 r['evidence']='자가응답·점주 입력값 기반 예비진단. 업종 가중치·임계값·성장단계 판정규칙은 미검증. 매출-비용 차액은 세무상 이익이 아님.'
 return r
