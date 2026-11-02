"""Biz-DNA small business rules engine. All cutoffs are provisional, not validated norms."""
from math import isfinite
AREAS={"상권·입지":15,"상품·서비스":15,"고객관리":15,"마케팅·판로":10,"재무·수익":20,"점포운영":10,"디지털":5,"경영자·미래대응":10}
QUESTIONS={
"상권·입지":["주변 핵심 고객층과 시간대별 수요를 파악한다","주요 경쟁점포의 가격·상품·강점을 파악한다","점포의 접근성과 가시성 문제를 확인한다","상권 변화에 맞춰 영업방식을 조정한다"],
"상품·서비스":["주력상품의 차별화 요소가 명확하다","고객 의견을 제품·서비스 개선에 반영한다","상품별 원가와 마진을 파악한다","가격과 상품구성을 정기적으로 점검한다"],
"고객관리":["단골고객 비중과 재방문을 파악한다","고객의 재방문을 유도하는 활동을 운영한다","고객 불만을 기록하고 개선한다","고객 이탈 원인을 분석한다"],
"마케팅·판로":["지도·검색·온라인 점포정보를 최신으로 관리한다","홍보활동의 유입·매출 효과를 측정한다","신규고객 확보 채널을 운영한다","채널별 판매실적을 비교한다"],
"재무·수익":["월별 매출과 비용을 기록한다","고정비와 손익분기점을 파악한다","현금흐름과 지급일정을 관리한다","상품별 원가·마진을 관리한다"],
"점포운영":["재고·발주를 체계적으로 관리한다","서비스 품질기준을 지킨다","업무별 소요시간과 생산성을 점검한다","성수기·비수기 운영계획이 있다"],
"디지털":["POS·회계 등 디지털 도구를 활용한다","온라인 고객정보를 적절히 관리한다","반복업무의 자동화를 활용한다","데이터를 경영 의사결정에 활용한다"],
"경영자·미래대응":["향후 1년 경영목표가 구체적이다","매출감소에 대한 대응계획이 있다","교육·컨설팅 등 외부자원을 활용한다","시장변화에 대비한 개선계획이 있다"]}
DNA={
"G/S":[("안정적 수익 유지","매출 확대를 위한 투자"),("현재 규모 유지","사업규모 확대"),("안정적 운영","성장기회 선점"),("재무안정 우선","성장투자 우선")],
"D/E":[("가격·운영효율","차별화된 고객경험"),("비용 절감","상품 혁신"),("표준상품 중심","특화상품 중심"),("운영 생산성","브랜드 차별성")],
"N/R":[("단골고객 심화","신규고객 확대"),("기존 상권 집중","신규 상권·채널 개척"),("기존 고객 유지","새로운 고객군 발굴"),("재방문 관리","신규고객 유입")],
"P/O":[("점주 직접 결정","직원·시스템에 권한 분산"),("경험 중심 운영","데이터·매뉴얼 중심 운영"),("점주 직접 고객응대","표준화된 고객관리"),("개인 판단 중심","역할분담 중심")],}
STRATEGIES={
"재무·수익":("수익구조 및 현금흐름 개선","상품별 공헌이익과 고정비를 점검하고 13주 현금흐름표 작성","영업현금수지·상품별 마진"),
"상권·입지":("상권수요 대응 및 입지전략","시간대별 수요와 경쟁점포를 분석해 상품·영업시간 재설계","시간대별 매출·유입고객"),
"상품·서비스":("주력상품 경쟁력 강화","고객평가를 반영하고 저수익 상품을 정비","주력상품 재구매율·마진"),
"고객관리":("단골고객 및 재방문 확대","재방문율을 측정하고 고객불만 개선·단골 프로그램 실행","재방문율·고객만족"),
"마케팅·판로":("신규고객 유입 강화","지도·리뷰·SNS 노출을 정비하고 유입경로별 성과 측정","신규고객 수·채널별 전환율"),
"점포운영":("점포 운영효율 개선","발주·재고·서비스 매뉴얼을 표준화하고 낭비시간 절감","재고회전·폐기율·처리시간"),
"디지털":("디지털 경영관리 도입","POS·매출자료를 정리하고 반복업무를 자동화","데이터 기록률·업무시간"),
"경영자·미래대응":("경영목표 및 대응계획 수립","분기 목표·우선 실행과제·매출악화 대응계획 마련","월별 목표달성률·위험대응 실행률")}
SECTOR_BONUS={"외식업":{"재무·수익":6,"상품·서비스":4,"고객관리":3},"도소매업":{"재무·수익":5,"점포운영":5,"상권·입지":3},"생활서비스업":{"고객관리":6,"점포운영":4,"마케팅·판로":3},"기타":{}}

def diagnose(payload):
    profile=payload['profile']; responses=payload['responses']; dna=payload['dna']
    for area,qs in QUESTIONS.items():
        values=responses.get(area,[])
        if len(values)!=len(qs) or any(type(v)!=int or not 1<=v<=5 for v in values):raise ValueError(f'{area}: 1~5점 정수 4개 필요')
    for axis,qs in DNA.items():
        values=dna.get(axis,[])
        if len(values)!=len(qs) or any(type(v)!=int or not 1<=v<=5 for v in values):raise ValueError(f'{axis}: 1~5점 정수 4개 필요')
    sales=float(profile['monthly_sales']); cost=float(profile['monthly_cost']); rent=float(profile['monthly_rent'])
    if not all(isfinite(x) for x in (sales,cost,rent)):raise ValueError('금액은 유한한 숫자여야 합니다')
    if min(sales,cost,rent)<0 or rent>cost:raise ValueError('금액은 음수일 수 없으며 임대료는 총비용 이하이어야 합니다')
    scores={a:round(sum(v-1 for v in responses[a])/16*100,2) for a in AREAS}
    overall=round(sum(scores[a]*w for a,w in AREAS.items())/100,2)
    dna_scores={k:round(sum(v-1 for v in dna[k])/16*100,2) for k in DNA}
    # G/S: high G; D/E: high D; N/R: high N; P/O: high P
    code=''.join(('G' if dna_scores['G/S']>=50 else 'S','D' if dna_scores['D/E']>=50 else 'E','N' if dna_scores['N/R']>=50 else 'R','P' if dna_scores['P/O']>=50 else 'O'))
    border=[k for k,v in dna_scores.items() if 40<v<60]
    profit=sales-cost; margin=profit/sales*100 if sales else None
    rent_ratio=rent/sales*100 if sales else None
    risks=[]
    if sales==0:risks.append({'code':'NO_SALES','level':'high','text':'매출이 없어 수익성·임대료비율 산정 불가'})
    if profit<0:risks.append({'code':'NEGATIVE_CASH','level':'high','text':'입력한 월간 수입·지출 차액이 음수: 확장투자보다 유동성 점검 우선'})
    if sales and rent_ratio>20:risks.append({'code':'RENT_BURDEN','level':'medium','text':'매출 대비 임대료 20% 초과: 임시 경고기준에 따른 고정비 점검 필요'})
    if sales>0 and cost>sales*0.95:risks.append({'code':'LOW_BUFFER','level':'medium','text':'월 매출 대비 비용 비중이 95%를 초과하여 여유자금이 부족할 수 있음'})
    if scores['재무·수익']<40:risks.append({'code':'WEAK_FINANCE','level':'medium','text':'재무·수익 관리역량이 낮아 원가·현금흐름 점검 필요'})
    sector=profile.get('sector','기타')
    if sector not in SECTOR_BONUS:sector='기타'
    target=profile.get('target','수익성 개선')
    goal_area={'수익성 개선':'재무·수익','매출확대':'마케팅·판로','단골확보':'고객관리','운영효율':'점포운영','사업전환':'경영자·미래대응'}.get(target,'재무·수익')
    # 경영단계는 관측 가능한 성장률·반복매출 자료 없이 확정할 수 없어 '미판정'으로 둠
    stage={'code':'UNDETERMINED','label':'성장단계 미판정','reason':'매출추세·반복고객·영업지속성 데이터 추가 필요'}
    strategy=[]
    for area,score in scores.items():
        urgency=100-score
        fit=50+SECTOR_BONUS.get(sector,{}).get(area,0)*4
        if area=='재무·수익' and profit<0:fit=100;urgency=max(urgency,95)
        if area=='재무·수익' and rent_ratio is not None and rent_ratio>20:fit=min(100,fit+15)
        if area=='마케팅·판로' and profit<0:fit=20
        if area=='점포운영' and sector=='외식업':fit+=8
        if area==goal_area:fit=min(100,fit+18)
        feasibility=70 if area not in ('상권·입지','디지털') else 60
        priority=round(.45*urgency+.35*fit+.20*feasibility,2)
        gated=False
        if profit<0 and area in ('마케팅·판로','상권·입지'):
            gated=True;priority=min(priority,35)
        rationale=f'역량 {score:.1f}점, 격차 {urgency:.1f}점, 적합도 {fit:.0f}점, 실행가능성 {feasibility:.0f}점'
        if gated:rationale+='; 적자상태로 확장성 지출 우선순위 제한'
        title,action,kpi=STRATEGIES[area]
        strategy.append({'area':area,'title':title,'action':action,'kpi':kpi,'priority':priority,'gap':urgency,'fit':fit,'feasibility':feasibility,'gated':gated,'rationale':rationale})
    strategy.sort(key=lambda x:(-x['priority'],x['area']))
    strengths=sorted(scores,key=lambda a:-scores[a])[:2]
    weaknesses=sorted(scores,key=lambda a:scores[a])[:2]
    return {'name':profile.get('name','미입력 점포'),'sector':sector,'profile':profile,'dna_code':code,'dna_scores':dna_scores,'border_axes':border,'scores':scores,'overall':overall,'profit_proxy':round(profit,2),'margin_proxy':round(margin,2) if margin is not None else None,'rent_ratio':round(rent_ratio,2) if rent_ratio is not None else None,'risks':risks,'stage':stage,'model_version':'3.0-prototype','strategies':strategy[:5],'strengths':strengths,'weaknesses':weaknesses,'evidence':'자가응답·점주 입력값 기반 예비진단. 상권·카드매출·세무자료 미연계. 임계값과 가중치는 미검증 시범기준.'}
