"""Evidence-bound local market comparison. No invented benchmark data."""
import csv, io, math
REQUIRED={'month','store_sales','market_sales'}
def analyze_market_csv(raw):
    if isinstance(raw,bytes): raw=raw.decode('utf-8-sig')
    rows=list(csv.DictReader(io.StringIO(raw)))
    if not rows or not REQUIRED.issubset(rows[0]):
        raise ValueError('CSV 필수 열: month, store_sales, market_sales')
    out=[]; seen=set()
    for row in rows:
        m=row['month'].strip()
        if len(m)!=7 or m[4]!='-' or not m[:4].isdigit() or not m[5:].isdigit() or not 1<=int(m[5:])<=12 or m in seen:
            raise ValueError('월 형식은 YYYY-MM이며 중복이 없어야 합니다')
        seen.add(m)
        try: a=float(row['store_sales']); b=float(row['market_sales'])
        except (TypeError,ValueError): raise ValueError(f'{m}: 매출은 숫자여야 합니다')
        if not all(math.isfinite(x) and x>=0 for x in (a,b)):raise ValueError('매출은 0 이상의 유한한 수여야 합니다')
        out.append({'month':m,'store_sales':a,'market_sales':b})
    out.sort(key=lambda x:x['month'])
    if len(out)<2:raise ValueError('서로 다른 월의 데이터가 최소 2개 필요합니다')
    first,last=out[0],out[-1]
    def growth(k):return round((last[k]/first[k]-1)*100,2) if first[k]>0 else None
    sg,mg=growth('store_sales'),growth('market_sales')
    gap=round(sg-mg,2) if sg is not None and mg is not None else None
    if gap is None: label='비교불가'
    elif gap>=5:label='상권 대비 상대적 개선'
    elif gap<=-5:label='상권 대비 상대적 부진'
    else:label='상권 변화와 유사'
    return {'months':len(out),'first_month':first['month'],'last_month':last['month'],'store_change_pct':sg,'market_change_pct':mg,'gap_pp':gap,'interpretation':label,'series':out,'caution':'최초·최종월 변화율 비교이며 인과관계 판정 아님. 동일 기간·업종·매출 정의·상권 경계의 일치 여부를 확인해야 함.'}
