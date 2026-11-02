"""Optional external AI narrative; never used for scoring or unsupported statistics."""
import json, urllib.request, urllib.error

def generate_narrative(result, api_key=None, model='gpt-4.1-mini'):
    if not api_key:
        return {'status':'not_configured','text':'AI API 키가 없어 규칙기반 분석만 제공합니다.'}
    evidence={k:result.get(k) for k in ['sector','dna_code','overall','scores','risks','stage','strategies','market_comparison','confidence']}
    instructions=('당신은 소상공인 경영컨설턴트다. 한국어로 1) 종합평가 2) 원인 가설과 검증자료 3) 우선전략 3개 4) 90일 실행과제 5) 불확실성을 작성한다. '
                  '제공 JSON 밖의 수치·업종평균·실제 관측치를 만들지 말 것. 자가진단은 객관적 사실로 단정하지 말 것. 매출변화 원인을 상권변화로 단정하지 말 것. '
                  '기업의 개인정보, 주소, 고객정보를 요청하지 말 것. 소제목 포함 900~1400자.')
    body=json.dumps({'model':model,'instructions':instructions,'input':json.dumps(evidence,ensure_ascii=False),'max_output_tokens':1400},ensure_ascii=False).encode('utf-8')
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=body,headers={'Authorization':'Bearer '+api_key,'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=40) as resp:data=json.load(resp)
        pieces=[p.get('text','') for item in data.get('output',[]) for p in item.get('content',[]) if p.get('type')=='output_text']
        text='\n'.join(pieces).strip()
        return {'status':'ok','text':text} if text else {'status':'error','text':'AI 응답에서 텍스트를 찾지 못했습니다.'}
    except (urllib.error.URLError,ValueError,TimeoutError) as e:
        return {'status':'error','text':f'AI 분석 연결 실패: {type(e).__name__}'}
