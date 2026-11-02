import json,io,csv
from pathlib import Path
import pandas as pd
import streamlit as st
from engine import DNA,QUESTIONS
from advanced import diagnose_v4,SECTOR_QUESTIONS
from report import build_pdf
from storage import init,save,records,get,delete
from analytics import aggregate
from followup import init_followup,add_action,update_action,actions,add_measurement,measurements,evaluate
st.set_page_config(page_title='Biz-DNA v6 소상공인 진단',layout='wide')
st.markdown('<style>.block-container{max-width:1240px;padding-top:1.8rem}h1,h2,h3{color:#123453}</style>',unsafe_allow_html=True)
init();init_followup();st.title('Biz-DNA | 소상공인 경영진단·상권 통합관리')
st.caption('v6 시범 시스템 · 진단 저장 및 상권별 통계 · 기본/정밀 PDF')
mode=st.sidebar.radio('화면 선택',['점주 진단','운영기관 대시보드','진단이력 관리','개선과제·성과추적'])
st.sidebar.warning('로컬 시연용. 로그인·권한분리·암호화·운영서버 보안 미구현. 실제 개인정보 입력 금지.')
if mode=='점주 진단':
 st.subheader('01. 점포 및 경영현황')
 ex=st.selectbox('예시 데이터',['직접 입력','카페 예시','생활서비스 예시'])
 file={'카페 예시':'sample_cafe.json','생활서비스 예시':'sample_service.json'}.get(ex)
 sample=json.loads((Path(__file__).parent/file).read_text(encoding='utf-8')) if file else None
 with st.form('assessment'):
  a,b,c=st.columns(3)
  with a:
   name=st.text_input('점포명',sample['profile']['name'] if sample else '')
   district=st.text_input('상권명/분석구역','시범상권 A')
  with b:
   sector=st.selectbox('업종',['외식업','도소매업','생활서비스업','기타'],index=['외식업','도소매업','생활서비스업','기타'].index(sample['profile']['sector']) if sample else 0)
   sales=st.number_input('월평균 매출 (만원)',0.,value=float(sample['profile']['monthly_sales']) if sample else 2000.)
  with c:
   cost=st.number_input('월평균 비용 (만원)',0.,value=float(sample['profile']['monthly_cost']) if sample else 1600.)
   rent=st.number_input('월 임대료 (비용에 포함, 만원)',0.,value=float(sample['profile']['monthly_rent']) if sample else 200.)
  target=st.selectbox('경영목표',['수익성 개선','매출확대','단골확보','운영효율','사업전환'])
  st.subheader('02. DNA 경영성향 (16문항)')
  dna={}
  for axis,qs in DNA.items():
   with st.expander(axis):
    dna[axis]=[st.radio(f'{i+1}. {l} ↔ {r}',[1,2,3,4,5],index=(sample['dna'][axis][i]-1 if sample else 2),horizontal=True,key=f'dna{axis}{i}') for i,(l,r) in enumerate(qs)]
  st.subheader('03. 8대 경영역량 (32문항)')
  answers={}
  for area,qs in QUESTIONS.items():
   with st.expander(area):
    answers[area]=[st.radio(f'{i+1}. {q}',[1,2,3,4,5],index=(sample['responses'][area][i]-1 if sample else 2),horizontal=True,key=f'ans{area}{i}') for i,q in enumerate(qs)]
  st.subheader('04. 업종별 추가진단 (선택)')
  supplement={}
  for area,qs in SECTOR_QUESTIONS.get(sector,{}).items():
   with st.expander(f'{sector} · {area}'):
    supplement[area]=[st.slider(q,1,5,3,key=f'sup{sector}{area}{i}') for i,q in enumerate(qs)]
  st.subheader('05. 성장단계 근거자료 (선택)')
  x,y,z=st.columns(3)
  months=x.number_input('운영개월수',0,600,0); repeat=y.number_input('재방문율(%)',0.,100.,0.); positive=z.number_input('최근 12개월 흑자월수',0,12,0)
  previous=x.number_input('전년 동월 매출 (만원)',0.,value=0.); channels=y.number_input('판매채널 수',0,100,1); staff=z.number_input('종사자 수',0,1000,0)
  consent=st.checkbox('진단내용을 로컬 시범 DB에 저장하는 데 동의합니다 (미동의 시 결과만 화면 표시)')
  submit=st.form_submit_button('진단 실행',type='primary',use_container_width=True)
 if submit:
  payload={'profile':{'name':name or '미입력','sector':sector,'monthly_sales':sales,'monthly_cost':cost,'monthly_rent':rent,'target':target},'dna':dna,'responses':answers,'sector_answers':supplement,'observations':({'months_operating':months,'repeat_rate':repeat,'positive_cashflow_months':positive,'channels':channels,'staff':staff,**({'sales_prev':previous} if previous>0 else {})} if months>0 and repeat>0 and positive>0 else {})}
  try:
   result=diagnose_v4(payload); saved_id=save(payload,result,district,consent) if consent else None
   st.session_state['last']=(payload,result,saved_id)
  except ValueError as e:st.error(str(e))
 if 'last' in st.session_state:
  payload,r,saved_id=st.session_state['last']
  st.divider();st.subheader('진단결과')
  c1,c2,c3=st.columns(3);c1.metric('경영역량',f"{r['overall']:.1f}점");c2.metric('DNA 유형',r['dna_code']);c3.metric('성장단계',r['stage']['code'])
  st.bar_chart(pd.DataFrame({'영역':list(r['scores']),'점수':list(r['scores'].values())}).set_index('영역'))
  st.write('**취약역량:** '+', '.join(r['weaknesses']));st.write('**우선 추천전략:** '+', '.join(s['title'] for s in r['strategies'][:3]))
  for risk in r['risks']:st.warning(risk['text'])
  if saved_id:st.success(f'로컬 저장 완료 · 진단번호 {saved_id}')
  l,m=st.columns(2)
  l.download_button('기본형 PDF',build_pdf(r,False),file_name='BizDNA_basic.pdf',mime='application/pdf')
  m.download_button('정밀형 PDF',build_pdf(r,True),file_name='BizDNA_detailed.pdf',mime='application/pdf')
elif mode=='운영기관 대시보드':
 st.subheader('상권별 소상공인 경영진단 현황')
 rows=records();districts=sorted(set(r['district'] for r in rows));sectors=sorted(set(r['sector'] for r in rows))
 a,b=st.columns(2);d=a.selectbox('분석 상권',['전체']+districts);s=b.selectbox('업종',['전체']+sectors)
 min_group=5
 summary=aggregate(rows,None if s=='전체' else s,None if d=='전체' else d,min_group)
 st.metric('진단 점포수 (중복점포 최신 결과만)',summary['n'])
 if summary['suppressed']:st.warning(summary['message'])
 else:
  a,b=st.columns(2);a.metric('평균 경영역량',f"{summary['overall_mean']}점");b.metric('중앙값',f"{summary['overall_median']}점")
  st.subheader('8대 영역 평균');st.bar_chart(pd.Series(summary['areas']))
  st.subheader('상위 경영개선 수요');st.bar_chart(pd.Series(summary['strategy_top3_counts']).sort_values(ascending=False).head(10))
  st.subheader('DNA 유형 분포');st.bar_chart(pd.Series(summary['dna_types']).sort_values(ascending=False))
  st.caption(summary['note'])
  st.download_button('집계 JSON 다운로드',json.dumps(summary,ensure_ascii=False,indent=2),file_name='bizdna_aggregate.json',mime='application/json')
 st.info('집계 통계는 자가진단 참여점포 기준이며 대표성 있는 상권 모집단 통계가 아닙니다. 최소 5개 점포 미만 집계는 숨깁니다.')
elif mode=='진단이력 관리':
 st.subheader('로컬 진단이력 관리')
 rows=records()
 if not rows:st.info('저장된 진단이 없습니다.')
 else:
  st.dataframe(pd.DataFrame([{k:r[k] for k in ('id','created_at','shop_name','sector','district','model_version')} for r in rows]),hide_index=True,use_container_width=True)
  selected=st.selectbox('진단번호', [r['id'] for r in rows]); rec=get(selected)
  if rec:
   r=json.loads(rec['result_json']);st.write(f"**{rec['shop_name']}** · {r['dna_code']} · {r['overall']}점")
   st.download_button('해당 진단 JSON 내보내기',json.dumps({'input':json.loads(rec['input_json']),'result':r},ensure_ascii=False,indent=2),file_name=f'assessment_{selected}.json')
   st.download_button('정밀 PDF 다운로드',build_pdf(r,True),file_name=f'assessment_{selected}.pdf',mime='application/pdf')
   confirm=st.checkbox('이 진단을 영구 삭제하는 데 동의합니다')
   if st.button('선택 진단 삭제',disabled=not confirm):delete(selected);st.rerun()

else:
 st.subheader('개선과제 실행관리 및 후속 성과측정')
 st.warning('시범용 로컬 데이터입니다. 로그인·접근권한 분리가 없어 실제 사업장 정보는 입력하지 마세요.')
 rows=records()
 if not rows:st.info('먼저 진단을 저장하세요.')
 else:
  sid=st.selectbox('관리할 진단', [r['id'] for r in rows],format_func=lambda x: next(f"{r['shop_name']} / {r['district']} / #{r['id']}" for r in rows if r['id']==x))
  rec=get(sid); result=json.loads(rec['result_json'])
  st.markdown('### 실행과제 등록')
  strategies=[s['title'] for s in result.get('strategies',[])] or ['경영개선']
  with st.form('new_action'):
   strategy=st.selectbox('추천전략',strategies)
   task=st.text_input('실행과제')
   owner=st.text_input('담당자 (가명 사용 권장)',value='점주')
   due=st.date_input('목표일')
   if st.form_submit_button('과제 등록'):
    try:add_action(sid,strategy,task,owner,due.isoformat());st.success('과제 등록 완료')
    except ValueError as e:st.error(str(e))
  current=actions(sid)
  if current:
   st.dataframe(pd.DataFrame(current)[['id','strategy','task','owner','due_date','status']],hide_index=True,use_container_width=True)
   a,b=st.columns(2)
   aid=a.selectbox('상태 변경 과제번호',[r['id'] for r in current]);status=b.selectbox('변경할 상태',['계획','진행','완료','보류'])
   if st.button('과제 상태 저장'):update_action(aid,status);st.rerun()
  st.markdown('### 월별 후속 실적 입력')
  with st.form('new_measure'):
   a,b,c=st.columns(3)
   dt=a.date_input('측정일',key='measure_date');sales=b.number_input('월 매출(만원)',min_value=0.,value=0.,key='msales');cost=c.number_input('월 비용(만원)',min_value=0.,value=0.,key='mcost')
   repeat=st.number_input('재방문율(%) — 미확인 시 0이 아니라 미입력 선택',min_value=0.,max_value=100.,value=0.)
   has_repeat=st.checkbox('재방문율 측정자료 있음')
   note=st.text_input('측정 메모')
   if st.form_submit_button('실적 저장'):
    add_measurement(sid,dt.isoformat(),sales,cost,repeat=repeat if has_repeat else None,note=note);st.success('실적 저장 완료')
  summary=evaluate(sid)
  if summary['measurements']:
   st.dataframe(pd.DataFrame(summary['measurements']),hide_index=True,use_container_width=True)
   chart=pd.DataFrame(summary['measurements']).set_index('date')[['sales','operating_surplus_proxy']]
   st.line_chart(chart)
  st.caption(summary['caution'])
  st.download_button('성과관리 데이터 JSON',json.dumps({'actions':actions(sid),'kpis':summary},ensure_ascii=False,indent=2),file_name=f'bizdna_followup_{sid}.json',mime='application/json')
