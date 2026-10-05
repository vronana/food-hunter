#!/usr/bin/env python3
"""운중동 페이지 만들기. 수지 파일은 읽지도 쓰지도 않음 (src/app.html 은 읽기만 함).
원본(src/app.html)은 그대로 두고, 운중동용으로 달라지는 부분만 아래 PATCHES 로 덮어 씁니다.
  data/unjung/rows.json, data/unjung/edits.json -> 세 가지 결과물
  unjung/index.html            : 링크용 보기 전용 (보류함·삭제 제외, 별표 반영) — 주소 .../food-hunter/unjung/
  unjung/manifest.webmanifest  : 홈 화면 추가용
  dist/unjung-editor.html      : 클로드 페이지용 편집 버전 (전체 데이터, 보류함 포함)
PATCHES 가 원본과 안 맞으면(원본 app.html 이 바뀌었을 때) 조용히 넘어가지 않고 멈춥니다.
"""
import json,os,sys
here=os.path.dirname(os.path.abspath(__file__))
rows=json.load(open(f'{here}/data/unjung/rows.json'))
edp=f'{here}/data/unjung/edits.json'
ed=json.load(open(edp)) if os.path.exists(edp) else {}
src=open(f'{here}/src/app.html').read()

CAFE_ICON=("<svg viewBox='0 0 64 64' aria-hidden='true'>"
 "<path d='M20 19C16 16 24 13 20 8M30 19C26 16 34 13 30 8M40 19C36 16 44 13 40 8' stroke='#cdbfb2' stroke-width='2.6' stroke-linecap='round' fill='none'/>"
 "<path d='M48 29c9-1 10 11 0 13' stroke='#7fb8c4' stroke-width='4' stroke-linecap='round' fill='none'/>"
 "<path d='M8 26h40v12c0 11-9 18-20 18S8 49 8 38z' fill='#7fb8c4'/>"
 "<ellipse cx='28' cy='26' rx='20' ry='6' fill='#e4f3f6'/><ellipse cx='28' cy='26.5' rx='17' ry='4.4' fill='#8b5a3c'/>"
 "<circle cx='22' cy='41' r='2.1' fill='#4a3b32'/><circle cx='34' cy='41' r='2.1' fill='#4a3b32'/>"
 "<path d='M25 45Q28 48.5 31 45' stroke='#4a3b32' stroke-width='1.9' stroke-linecap='round' fill='none'/>"
 "<circle cx='17.5' cy='45.5' r='2.6' fill='#ff8f7a' opacity='.55'/><circle cx='38.5' cy='45.5' r='2.6' fill='#ff8f7a' opacity='.55'/>"
 "</svg>")

BREAD_ICON=("<svg viewBox='0 0 64 64' aria-hidden='true'><g transform='translate(0 5)'>"
 "<path d='M6 38c0-15 11-25 26-25s26 10 26 25c0 4-3 6-6 6H12c-3 0-6-2-6-6z' fill='#e0a458'/>"
 "<path d='M22 20l4 8M33 17l3 9M44 21l2 8' stroke='#f6dcae' stroke-width='3' stroke-linecap='round' fill='none'/>"
 "<circle cx='23' cy='36' r='2.3' fill='#4a3b32'/><circle cx='41' cy='36' r='2.3' fill='#4a3b32'/>"
 "<path d='M28 40Q32 44 36 40' stroke='#4a3b32' stroke-width='2' stroke-linecap='round' fill='none'/>"
 "<circle cx='17' cy='40' r='2.8' fill='#ff8f7a' opacity='.55'/><circle cx='47' cy='40' r='2.8' fill='#ff8f7a' opacity='.55'/>"
 "</g></svg>")

EXTRA_CSS="""/* 운중동 전용 */
.pills .selw:first-child{display:none}
.pb-chars{grid-template-columns:repeat(10,minmax(0,1fr))}
.grid .cc:last-child:nth-child(odd){grid-column:1/-1}
"""

# (원본 문구, 바꿀 문구, 원본에서 정확히 몇 번 나와야 하는지)
CHARS_OLD='["육류","탕류","밥류","면류","중식","일식","양식","세계음식"].forEach('
PATCHES=[
 ('<span class="region">수지구</span>','<span class="region">운중동</span>',1),
 ('{k:"세계음식",label:"세계식"},{k:"기타",label:"분류 안 됨"}','{k:"세계음식",label:"세계식"},{k:"카페"},{k:"베이커리"},{k:"기타",label:"분류 안 됨"}',1),
 ('const DONGS = ["풍덕천동","죽전동","동천동","상현동","성복동","신봉동","고기동"];','const DONGS = ["운중동"];',1),
 ('"세계음식":["#e8b100","#fff1c2"],"기타":','"세계음식":["#e8b100","#fff1c2"],"카페":["#b5764a","#f4e3d3"],"베이커리":["#c9893a","#fbeccd"],"기타":',1),
 ('const ICONS = {"chain":','const ICONS = {"카페": "'+CAFE_ICON+'", "베이커리": "'+BREAD_ICON+'", "chain":',1),
 ('["중식","일식","양식","세계음식"].forEach(k=>g2.append(card(k)))','["중식","일식","양식","세계음식","카페","베이커리"].forEach(k=>g2.append(card(k)))',1),
 (CHARS_OLD,'["육류","탕류","밥류","면류","중식","일식","양식","세계음식","카페","베이커리"].forEach(',2),
 ('encodeURIComponent("수지구 "+r.n)','encodeURIComponent("운중동 "+r.n)',1),
 ('const REGION="suji";','const REGION="unjung";',1),
 # 보류함: 분류 대기(기타) / 범위 밖(hg=1) / 요리주점(hg=2)
 ('function hold0(r,s){ return s==="기타" || !!r.sm || (r.y!==undefined && r.y<5); }','function hold0(r,s){ return s==="기타" || !!r.hg; }',1),
 ('[4,3,2,1,0,-1,-2].forEach(y=>{','[-2,-3,-1].forEach(y=>{',1),
 ('(i.r.sm?-2:(i.r.y===undefined?-1:i.r.y))===y','(i.r.hg===2?-1:(i.r.hg===1?-3:-2))===y',1),
 ('text:y===-2?"50㎡ 미만":(y<0?"요리주점":y+"년차")','text:y===-2?"분류 대기":(y===-3?"범위 밖":"요리주점")',1),
 # 면적을 모르는 가게는 ㎡ 표시 없이 연도만
 ('text:Math.round(r.m)+"㎡ · "+r.d.slice(0,4)+"년 허가"','text:(r.m>0?Math.round(r.m)+"㎡ · ":"")+r.d.slice(0,4)+"년 허가"',1),
 ('(r.d?Math.round(r.m)+"㎡ · "+r.d.slice(0,4)+"년 허가":','(r.d?(r.m>0?Math.round(r.m)+"㎡ · ":"")+r.d.slice(0,4)+"년 허가":',1),
 # 직접 추가할 때 이름에 카페/커피 등이 있으면 카페로 자동 분류
 ('const t=(re)=>re.test(n);','const t=(re)=>re.test(n);\n  if(t(/베이커리|빵|브레드|제과|케이크|디저트|쿠키|스콘|도넛|꽈배기|젤라또|마카롱/)) return "베이커리";\n  if(t(/카페|커피/)) return "카페";',1),
 # 양식(햄버거) 양상추를 좌우대칭으로
 ('<path d=\\"M7 31q6 5 12 0t12 0 12 0 12 0v3H7z\\" fill=\\"#93c978\\"/>','<path d=\\"M6 34.2a6.5 5.2 0 0 1 13 0a6.5 5.2 0 0 1 13 0a6.5 5.2 0 0 1 13 0a6.5 5.2 0 0 1 13 0V35.5H6z\\" fill=\\"#93c978\\"/>',1),
 # 즐겨찾기가 없어도 0곳으로 보여줌
 ('(x[0]!=="fav"||x[2]>0)','true',1),
 # 동네가 하나뿐이라 목록을 접지 않고 항상 펼침
 ('const fold=ngroups>1 && key!=="hold";','const fold=false;',1),
 ('</style>',EXTRA_CSS+'</style>',1),
]
for old,new,cnt in PATCHES:
    n=src.count(old)
    if n!=cnt: sys.exit(f'패치가 원본과 안 맞아요 (원본에 {n}곳, 기대 {cnt}곳): {old[:70]}')
    src=src.replace(old,new)

view=[];stars=[]
extra=[dict(id=k,n=e['n'],a=e.get('a',''),dg=e['dg'],m=0,d='',s=e.get('s','기타'),g=1 if e.get('g') else 0,f='',manual=1) for k,e in ed.items() if e.get('manual') and e.get('n') and e.get('dg')]
for r in rows+extra:
    e=ed.get(r['id'],{}); h=e['h'] if 'h' in e else (e.get('s',r['s'])=='기타' or bool(r.get('hg')))
    if e.get('x'): continue
    hs=False
    if h:
        if e.get('star') and not e.get('x'): hs=True
        else: continue
    r=dict(r); r['s']=e.get('s',r['s'])
    if not h: r.pop('hg',None)          # 보류함에서 올린 가게는 링크에서도 보이게
    if hs: r['hs']=1
    if 'c' in e: r['c']=bool(e['c'])
    view.append(r)
    if e.get('star'): stars.append(r['id'])
j=lambda o:json.dumps(o,ensure_ascii=False)
VERSION=open(f'{here}/VERSION').read().strip()+' · 운중동'
def make(data,static,st): return src.replace('__VERSION__',VERSION).replace('__DATA__',j(data)).replace('__STATIC__',static).replace('__STARS__',j(st))
BASE='https://vronana.github.io/food-hunter/'
REGION='unjung'
def head(region,rel):
    return f'''<meta name="theme-color" content="#f7f5f2">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="뭐먹지 운중">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta property="og:type" content="website">
<meta property="og:site_name" content="오늘 뭐먹지">
<meta property="og:title" content="오늘 뭐먹지">
<meta property="og:description" content="오늘 뭐 먹지? 고민되면 뽑기로 정해 보세요.">
<meta property="og:url" content="{BASE}{region}">
<meta property="og:image" content="{BASE}icons/icon-512.png?v=22">
<meta property="og:locale" content="ko_KR">
<meta name="description" content="오늘 뭐 먹지? 고민되면 뽑기로 정해 보세요.">
<link rel="manifest" href="manifest.webmanifest?v=23">
<link rel="icon" type="image/png" href="{rel}icons/icon-192.png?v=22">
<link rel="apple-touch-icon" href="{rel}icons/icon-180.png?v=22">
'''
mark='<meta name="color-scheme" content="only light">\n'
idx=make(view,'true',stars).replace(mark,mark+head(REGION+'/','../'),1)
os.makedirs(f'{here}/{REGION}',exist_ok=True)
open(f'{here}/{REGION}/index.html','w').write(idx)
mf=open(f'{here}/manifest.webmanifest').read().replace('"icons/','"../icons/')
mf=mf.replace('"name": "오늘 뭐먹지"','"name": "오늘 뭐먹지 운중동"').replace('"short_name": "오늘 뭐먹지"','"short_name": "뭐먹지 운중"')
open(f'{here}/{REGION}/manifest.webmanifest','w').write(mf)
os.makedirs(f'{here}/dist',exist_ok=True)
open(f'{here}/dist/unjung-editor.html','w').write(make(rows,'false',[]))
print('viewer',len(view),'stars',len(stars),'| editor',len(rows))
