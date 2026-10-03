#!/usr/bin/env python3
"""개업 5년 미만(0~4년차) 가게를 원본 CSV에서 뽑아 data/rows_new.json 으로 저장 (전부 보류함 대상)
사용: python3 tools/make_new.py 인허가.csv 모범.csv
"""
import sys,re,json,os
import pandas as pd
NOW=pd.Timestamp('2026-10-03')
ALLOW={'한식','식육(숯불구이)','중국식','경양식','분식','일식','횟집','외국음식전문점(인도,태국등)','패스트푸드','냉면집','김밥(도시락)','탕류(보신용)','패밀리레스트랑','뷔페식'}
BAR=re.compile(r'포차|주점|호프|맥주|홀덤|펍|이자카야|술집|bar\b|BAR|카페|커피|coffee|COFFEE|Cafe|cafe|치킨|투썸|바나프레소')
def has(s,k): return re.search(k,s) is not None
def cls(n,t):
    if t=="중국식": return ("중식","중식")
    if t in("일식","횟집"): return ("일식","일식·회")
    if t in("경양식","패스트푸드","패밀리레스트랑","뷔페식"):
        if "김도사불백" in n: return ("한식","고기·구이")
        return ("양식","양식")
    if t.startswith("외국"): return ("세계음식","세계음식")
    if t=="식육(숯불구이)": return ("한식","고기·구이")
    if t=="분식" or t=="김밥(도시락)": return ("한식","분식")
    if t=="냉면집": return ("한식","면류")
    if t=="탕류(보신용)": return ("한식","탕류")
    if has(n,"마라탕|짬뽕"): return ("중식","중식")
    if has(n,"돈까스|돈부리|깡우동|대광어|횟집|제주뿔소라"): return ("일식","일식·회")
    if has(n,"쌀국수 파스타|올드델리"): return ("세계음식","세계음식")
    if has(n,"국밥|해장|설렁탕|설농탕|곰탕|순대|감자탕|추어|삼계탕|탕$|육개장|소머리|흑염소|누룽지탕|동태탕|진국"): return ("한식","탕류")
    if has(n,"칼국수|국수|냉면|막국수|소바|수제비|면옥|면채반|제면소|밀면"): return ("한식","면류")
    if has(n,"김밥|떡볶이|분식|만두|본죽"): return ("한식","분식")
    if has(n,"찌개|찌게|백반|한정식|밥상|보리밥|쌈밥|집밥|청국장|순두부|한식뷔페|곤드레|정식"): return ("한식","찌개·백반")
    if has(n,"쭈꾸미|낙지|아구|코다리|찜|해물|꼼장어|장어|홍어|골뱅이|뽈탕|수산|오징어"): return ("한식","해산물·찜")
    if has(n,"고기|갈비|삼겹|족발|보쌈|구이|막창|곱창|오리|정육|한우|돼지|양꼬치|냉삼|대패|육회|야키니쿠|항정|등심|소고기|숯불|불백|꼬치|고깃|화로|돈가네|무쇠돈|정한돈|돈지|구어|연탄로|도야지|축산|샤브|닭"): return ("한식","고기·구이")
    return ("한식","한식 기타")
def to_s(big,sub):
    if big in("중식","일식","양식","세계음식"): return big
    return {"고기·구이":"육류","탕류":"탕류","찌개·백반":"밥류","면류":"면류"}.get(sub,"기타")

def norm(s): return re.sub(r'[\s\(\)\[\]·\-\.,]','',str(s))
def main(lic,mob,out,exclude_ids):
    df=pd.read_csv(lic,encoding='cp949',low_memory=False)
    d=df[df['영업상태명'].astype(str).str.contains('영업')].copy()
    d['m']=pd.to_numeric(d['소재지면적'],errors='coerce'); d=d[d['m']>=50]
    d=d[d['도로명주소'].astype(str).str.contains('수지구')]
    d['dt']=pd.to_datetime(d['인허가일자'].astype(str),errors='coerce')
    d=d[d['dt']>pd.Timestamp('2021-10-03')]          # 5년 미만
    d=d[d['업태구분명'].isin(ALLOW)]
    d['n']=d['사업장명'].astype(str)
    d=d[~d['n'].apply(lambda s:bool(BAR.search(s)))]
    d=d[~d['관리번호'].isin(exclude_ids)]
    mo=pd.read_csv(mob,encoding='cp949',low_memory=False)
    mo=mo[mo['영업상태명'].astype(str).str.contains('영업')]
    mo['k']=mo['업소명'].map(norm); mo['rd']=mo['도로명주소'].astype(str).str.replace('경기도 용인시 수지구 ','',regex=False).map(lambda s:norm(s.split('(')[0]))
    mmap={(r.k,r.rd):str(r.주된음식종류) for r in mo.itertuples()}
    rows=[]
    for _,x in d.iterrows():
        road=str(x['도로명주소']).replace('경기도 용인시 수지구 ','')
        a=re.sub(r'\s*\([^()]*\)\s*$','',road).strip()
        mj=re.search(r'수지구\s+(\S+동)',str(x['지번주소']))
        if not mj: continue
        big,sub=cls(x['n'],x['업태구분명'])
        k=(norm(x['n']),norm(road.split('(')[0]))
        g=1 if k in mmap else 0
        yrs=int((NOW-x['dt']).days//365.25)
        rows.append(dict(id=x['관리번호'],n=x['n'],a=a,dg=mj.group(1),m=round(float(x['m']),1),d=x['dt'].strftime('%Y-%m'),s=to_s(big,sub),g=g,f=(mmap[k] if g else ''),y=max(0,min(4,yrs))))
    json.dump(rows,open(out,'w'),ensure_ascii=False)
    return rows
if __name__=='__main__':
    here=os.path.dirname(os.path.abspath(__file__))+'/..'
    old={r['id'] for r in json.load(open(here+'/data/rows.json'))}
    rows=main(sys.argv[1],sys.argv[2],here+'/data/rows_new.json',old)
    import collections
    print(len(rows),sorted(collections.Counter(r['y'] for r in rows).items()),collections.Counter(r['s'] for r in rows),sum(r['g'] for r in rows),collections.Counter(r['dg'] for r in rows))
