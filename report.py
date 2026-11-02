"""A4 PDF basic and detailed reports using ReportLab."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing,Rect,String
from reportlab.lib.enums import TA_CENTER
from engine import AREAS
NAVY=colors.HexColor('#123354');TEAL=colors.HexColor('#087E89');PALE=colors.HexColor('#EAF4F5');GRAY=colors.HexColor('#526579')
FONT='Helvetica'
for path in ['/usr/share/fonts/truetype/nanum/NanumGothic.ttf','/usr/share/fonts/truetype/nanum/NanumSquareR.ttf']:
 if Path(path).exists():
  try:pdfmetrics.registerFont(TTFont('BizKo',path));FONT='BizKo';break
  except Exception:pass
styles={
 'title':ParagraphStyle('t',fontName=FONT,fontSize=22,leading=31,textColor=NAVY,spaceAfter=18),
 'h':ParagraphStyle('h',fontName=FONT,fontSize=13,leading=21,textColor=NAVY,spaceBefore=16,spaceAfter=9),
 'body':ParagraphStyle('b',fontName=FONT,fontSize=9,leading=16,textColor=NAVY,spaceAfter=7),
 'small':ParagraphStyle('s',fontName=FONT,fontSize=8,leading=13,textColor=GRAY,spaceAfter=6),
 'white':ParagraphStyle('w',fontName=FONT,fontSize=9,leading=15,textColor=colors.white)}
def P(s,sty='body'):return Paragraph(escape(str(s)),styles[sty])
def tbl(rows,widths=None):
 rows=[[P(c,'white' if i==0 else 'body') for c in row] for i,row in enumerate(rows)]
 t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,-1),(-1,-1),.4,colors.HexColor('#C8D9E0'))]));return t
def bars(scores):
 d=Drawing(490,242)
 for i,(k,v) in enumerate(scores.items()):
  y=220-i*29
  d.add(String(0,y,k,fontName=FONT,fontSize=9,fillColor=NAVY))
  d.add(Rect(132,y-2,292,12,fillColor=PALE,strokeColor=None))
  d.add(Rect(132,y-2,292*v/100,12,fillColor=TEAL,strokeColor=None))
  d.add(String(438,y,f'{v:.1f}',fontName=FONT,fontSize=9,fillColor=NAVY))
 return d
def footer(canvas,doc):
 canvas.setStrokeColor(colors.HexColor('#C6D8DF'));canvas.line(42,43,A4[0]-42,43)
 canvas.setFont(FONT,8);canvas.setFillColor(GRAY);canvas.drawString(42,29,'Biz-DNA | 소상공인 경영진단');canvas.drawRightString(A4[0]-42,29,str(doc.page))
def build_pdf(result,detailed=False):
 out=BytesIO();doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=42,rightMargin=42,topMargin=49,bottomMargin=57)
 s=[P('Biz-DNA 소상공인 경영진단 보고서','title'),P('정밀형 | 경영개선 실행전략' if detailed else '기본형 | 핵심진단 및 경영개선','h'),Spacer(1,12)]
 s.append(tbl([['기업명','업종','DNA 유형'],[result['name'],result['sector'],result['dna_code']]],widths=[170,160,181]));s.append(Spacer(1,16))
 s.append(P(f"종합 경영역량 {result['overall']:.2f}점 / 100점",'h'))
 s.append(P('기업 DNA는 경영성향을 나타내며 우수·열위 등급이 아닙니다.'))
 s.append(P('성장단계: '+result['stage']['label']+' / '+result['stage']['reason']))
 s.append(P('진단 신뢰도: '+result.get('confidence',{}).get('level','제한적')))
 s.append(P('종합진단 요약','h'))
 s.append(P('강점 영역: '+', '.join(result['strengths'])+' / 우선 보완 영역: '+', '.join(result['weaknesses'])))
 s.append(P('월간 매출-비용 차액: '+f"{result['profit_proxy']:,.0f}"+'만원. 세무상 영업이익과 다를 수 있습니다.'))
 s.append(P('8대 경영역량 프로파일','h'));s.append(bars(result['scores']))
 s.append(P('주요 경영위험','h'))
 for r in result['risks']:s.append(P('• '+r['text']))
 if not result['risks']:s.append(P('입력자료에 근거한 자동 위험규칙 미발동. 객관자료 확인 필요.'))
 s.append(P('맞춤형 경영개선 전략','h'))
 s.append(tbl([['순위','추천전략','우선점수']]+[[str(i),x['title'],f"{x['priority']:.1f}"] for i,x in enumerate(result['strategies'][:3],1)],widths=[48,352,111]))
 s.append(PageBreak())
 s.append(P('전략별 실행과제 및 성과관리','title'))
 for i,x in enumerate(result['strategies'][:3],1):
  s.append(P(f"{i}. {x['title']}",'h'));s.append(P('실행과제: '+x['action']));s.append(P('성과지표: '+x['kpi'],'small'))
 s.append(P('90일 실행 로드맵','h'))
 s.append(tbl([['기간','핵심 실행방향'],['1~30일','경영자료 정리·문제원인 확인·기준선 측정'],['31~60일','우선 전략 시범실행·주간 성과점검'],['61~90일','실행결과 비교·개선안 보완·차기 계획 수립']],widths=[105,406]))
 if detailed:
  s.append(PageBreak());s.append(P('심층 경영역량 진단','title'))
  for a,v in result['scores'].items():
   level='우선 개선 필요' if v<50 else '보완 검토' if v<70 else '상대적 강점'
   s.append(P(f'{a} | {v:.1f}점 | {level}','h'))
   s.append(P('현재 점수는 점주 자가응답에 따른 역량수준을 의미하며, 동종업종 평균이나 객관적 성과수준을 의미하지 않습니다.'))
  s.append(PageBreak());s.append(P('성장전략 및 위험관리 상세','title'))
  for x in result['strategies']:
   s.append(P(f"{x['title']} | 추천점수 {x['priority']:.1f}",'h'))
   s.append(P('개선 방향: '+x['action']));s.append(P('성과관리 지표: '+x['kpi']))
  s.append(P('진단 신뢰도 및 해석 한계','h'))
  s.append(P(result['evidence']))
  s.append(P('향후 객관적 매출·상권·경쟁점포 데이터 연계 및 전문가 검증을 권고합니다.'))
 s.append(Spacer(1,12));s.append(P('유의사항: '+result['evidence'],'small'))
 doc.build(s,onFirstPage=footer,onLaterPages=footer)
 return out.getvalue()

def build_v5_pdf(result,detailed=False):
 """ReportLab PDF with a supplemental evidence/AI page for v5."""
 from reportlab.pdfgen import canvas
 from pypdf import PdfReader, PdfWriter
 from io import BytesIO
 base=build_pdf(result,detailed)
 writer=PdfWriter();reader=PdfReader(BytesIO(base))
 for page in reader.pages:writer.add_page(page)
 extra=BytesIO();c=canvas.Canvas(extra,pagesize=A4)
 c.setFont(FONT,17);c.setFillColor(NAVY);c.drawString(45,780,'Biz-DNA | 상권비교 및 AI 분석')
 def lines(text,y):
  import textwrap
  c.setFillColor(NAVY);c.setFont(FONT,9)
  for line in str(text).splitlines():
   for chunk in textwrap.wrap(line,width=60) or ['']:
    if y<75: c.showPage();y=775;c.setFont(FONT,9)
    c.drawString(45,y,chunk);y-=17
  return y-13
 y=742
 m=result.get('market_comparison')
 if m:
  y=lines(f"비교기간: {m['first_month']} ~ {m['last_month']} / 점포 {m['store_change_pct']}% / 상권 {m['market_change_pct']}% / 격차 {m['gap_pp']}%p",y)
  y=lines('판정: '+m['interpretation'],y);y=lines('해석 주의: '+m['caution'],y)
 else:y=lines('상권 비교 데이터 미입력. 외부 평균이나 경쟁력을 추정하지 않음.',y)
 ai=result.get('ai_narrative',{})
 y=lines('AI 서술형 분석: '+('연결됨' if ai.get('status')=='ok' else '미연결 / 규칙기반 보고서'),y)
 if ai.get('status')=='ok':y=lines(ai['text'],y)
 y=lines('본 자료는 자가진단 및 사용자 제공 자료 기반 시범결과이며 전문가 확인이 필요합니다.',y)
 c.save();extra.seek(0)
 for page in PdfReader(extra).pages:writer.add_page(page)
 output=BytesIO();writer.write(output);return output.getvalue()
