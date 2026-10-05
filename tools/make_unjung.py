#!/usr/bin/env python3
"""운중동 데이터 만들기: 성남시 일반음식점 + 휴게음식점 CSV -> data/unjung/rows.json
사용: python3 tools/make_unjung.py 일반음식점.csv 휴게음식점.csv
- 영업 중인 운중동 가게만 (연차·면적 제한 없음)
- 술집·편의점·푸드트럭·PC방은 뺌
- 카페(커피·차)와 베이커리(빵·디저트)는 따로.
- 보류함: 이름으로 분류 못 한 곳(기타), 요리주점, 지도 범위 밖(hg=1). hg=2 는 요리주점.
"""
import sys,re,json,os,collections
import pandas as pd

here=os.path.dirname(os.path.abspath(__file__))+'/..'
# 걸어서 갈 수 있는 지도 범위 (CSV의 좌표계 값). 이 밖의 운중동 가게는 전부 보류함(범위 밖)
BOX=dict(x0=206600,x1=207420,y0=431980,y1=432350)

NAME_RULES=[
 ('카페',r'카페|까페|커피|coffee|cafe|베이커리|디저트|브런치|다방|찻집|티하우스'),
 ('세계음식',r'쌀국수|베트남|태국|타이|인도|네팔|멕시|타코|케밥|퍼|포메인|사이공|커리하우스|파키스'),
 ('일식',r'스시|초밥|사시미|회|횟집|오마카세|우동|소바|돈까스|돈카츠|가츠|라멘|라면|이자카야|일식|카츠|덮밥|규|야키|텐동|참치'),
 ('중식',r'짜장|짬뽕|중화|중국|마라|탕수육|양꼬치|반점|딤섬|훠궈|차이'),
 ('면류',r'국수|칼국수|냉면|막국수|면옥|밀면|수제비|파스타면|메밀|비빔국수|라면'),
 ('탕류',r'탕|국밥|해장국|순대국|찌개|전골|샤브|곰탕|설렁탕|감자탕|추어|백숙|삼계|닭한마리|찜|아구|뚝배기|죽'),
 ('육류',r'고기|갈비|삼겹|곱창|막창|족발|보쌈|치킨|통닭|닭갈비|닭발|오리|한우|숯불|구이|정육|불고기|돼지|소고기|육|바비큐|bbq|BBQ|목살|항정'),
 ('양식',r'피자|파스타|스테이크|버거|브런치|이탈리|양식|샌드위치|리스토란테|트라토리아|비스트로|그릴|햄버거|버거'),
 ('밥류',r'밥|김밥|비빔밥|한정식|정식|도시락|분식|떡볶이|덮밥|백반|국시|쌈|한식뷔페|식당'),
]
BY_TYPE={'까페':'카페','라이브카페':'카페','전통찻집':'카페','경양식':'양식','일식':'일식','중국식':'중식','횟집':'일식',
 '식육(숯불구이)':'육류','통닭(치킨)':'육류','호프/통닭':'육류','분식':'밥류','외국음식전문점(인도,태국등)':'세계음식','패스트푸드':'양식'}

# 사람이 확인해서 고친 것 (가게 이름 기준)
FIX={'본죽앤비빔밥카페서판교점':'밥류','퍼프':'카페','물만난 물고기':'일식','청정상회':'일식','쇼우민':'일식',
     '우대포 판교직영점':'밥류','우봉집 판교':'탕류'}
DESSERT=['바닐라 브라운 Vanilla Brown','쿠키앤코[COOKIE & CO]','닙스(nibs)','파머스마켓팥집','더블크림(Double cream)','앙떡&부뚜막',
         '오페뜨 서판교운중점','디자인무아','루나드블랑','아프레(APPRET)','헤이롤','프리힐리(Frihili)']
BAR_OUT={'생활맥주 서판교운중점','아트비어','보틀맥(Bottle Mac)','더노벰버라운지(판교운중점)(THE NOVEMBER LOUNGE)'}   # 술집: 목록에서 뺌
UNSURE={'주','P!VE(파이브)','진달래'}                      # 술집인지 식당인지 모름 -> 보류함(기타)
PUB_TYPES={'호프/통닭','정종/대포집/소주방','라이브카페'}  # 이 업태 + 분류 못 함 -> 요리주점
# 휴게음식점
REST_FIX={'삼동소바 판교점':'일식','써브웨이 서판교점':'양식','만두전골과칼국수미가온':'탕류','새쟁이꽈배기':'카페','짱구네떡볶이':'밥류',
 '팔복 황제누룽지탕':'탕류','피자스쿨(판교산운마을점)':'양식','맥도날드 서판교DT점':'양식','프랭크버거 서판교점':'양식','샐러디 서판교점':'양식',
 '이삭토스트 성남서판교점':'밥류','리얼케익 서판교점':'카페','파파젤라또':'카페','배스킨라빈스 판교운중점':'카페'}
# 빵·디저트집 -> 베이커리 (이름으로 추측, 틀리면 편집기에서 고침)
BAKERY=set(DESSERT)|{'퍼프','새쟁이꽈배기','리얼케익 서판교점','파파젤라또','배스킨라빈스 판교운중점','카페투브레드',
 '스크루지라이크스콘(SCROOGE LIKES SCONE)','비스위트'}
REST_HOLD={'라이트하우스(Light House)','라일락 향기','장모집','로이맘도라지가게 분당2호점','보돌미역블랙 판교운중점'}

def cat_general(n,t):
    for cat,pat in NAME_RULES:
        if re.search(pat,n,re.I): return cat
    return BY_TYPE.get(t,'기타')

def kind_general(n,t):
    c=FIX.get(n) or cat_general(n,t)
    if n in DESSERT: c='카페'
    if n in FIX: c=FIX[n]
    if n in BAR_OUT: return '술집'
    if n in UNSURE: return '기타'
    if c=='기타' and t in PUB_TYPES: return '요리주점'
    return c

def kind_rest(n,t):
    if t=='편의점' or t=='푸드트럭': return '제외'
    if '씨방' in n or '만화카페' in n: return '제외'
    if n in REST_FIX: return REST_FIX[n]
    if n in REST_HOLD: return '기타'
    if t in ('커피숍','전통찻집'): return '카페'
    return '기타'

def load(path,fn):
    d=pd.read_csv(path,encoding='cp949',low_memory=False)
    addr=d['지번주소'].fillna('')+' '+d['도로명주소'].fillna('')
    d=d[addr.str.contains('운중동')&(d['영업상태명']=='영업/정상')].copy()
    d['kind']=[fn(n,t) for n,t in zip(d['사업장명'],d['위생업태명'])]
    return d

def main(gen,rest,out):
    d=pd.concat([load(gen,kind_general),load(rest,kind_rest)])
    d['kind']=['베이커리' if n in BAKERY and k=='카페' else k for n,k in zip(d['사업장명'],d['kind'])]
    d=d.drop_duplicates('사업장명')          # 두 파일에 다 있는 가게는 한 곳으로
    d=d[~d['kind'].isin(['술집','제외'])]
    d['x']=pd.to_numeric(d['좌표정보(X)'],errors='coerce'); d['y']=pd.to_numeric(d['좌표정보(Y)'],errors='coerce')
    rows=[]
    for _,r in d.iterrows():
        inside=(BOX['x0']<=r.x<=BOX['x1']) and (BOX['y0']<=r.y<=BOX['y1'])
        k=r['kind']
        road=re.sub(r'^경기도\s*성남시\s*분당구\s*','',str(r['도로명주소']))
        i=road.find('(운중동')                       # "(운중동, 건물명 ...)" 부분은 떼고 도로명 주소만
        a=(road[:i] if i>=0 else re.sub(r'\s*\([^()]*\)\s*$','',road)).strip().rstrip(',').strip()
        m=pd.to_numeric(r['소재지면적'],errors='coerce'); m=0.0 if pd.isna(m) else round(float(m),1)
        dt=pd.to_datetime(str(r['인허가일자']),errors='coerce')
        row=dict(id=str(r['관리번호']),n=str(r['사업장명']),a=a,dg='운중동',m=m,d=(dt.strftime('%Y-%m') if pd.notna(dt) else ''),
                 s=('기타' if k=='요리주점' else k),g=0,f='')
        if k=='요리주점': row['hg']=2
        elif k!='기타' and not inside: row['hg']=1
        rows.append(row)
    ids=[r['id'] for r in rows]; assert len(ids)==len(set(ids)),'id 중복'
    os.makedirs(os.path.dirname(out),exist_ok=True)
    json.dump(rows,open(out,'w'),ensure_ascii=False)
    return rows

if __name__=='__main__':
    rows=main(sys.argv[1],sys.argv[2],here+'/data/unjung/rows.json')
    held=lambda r:r['s']=='기타' or r.get('hg')
    print('전체',len(rows))
    print('메인(보이는 곳)',collections.Counter(r['s'] for r in rows if not held(r)))
    print('보류함',collections.Counter(('요리주점' if r.get('hg')==2 else '범위 밖' if r.get('hg')==1 else '기타(분류 대기)') for r in rows if held(r)))
    print('면적 없음',sum(1 for r in rows if r['m']==0),'날짜 없음',sum(1 for r in rows if not r['d']))
