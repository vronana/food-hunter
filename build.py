#!/usr/bin/env python3
"""원본(src/app.html) + 데이터(data/rows.json, data/edits.json) -> 두 가지 결과물
  suji/index.html   : 링크용 보기 전용 (삭제/보류 제외, 별표 반영) — 주소 .../food-hunter/suji/
  index.html        : 옛 주소(.../food-hunter/)를 suji/ 로 보내는 안내 페이지
  dist/editor.html  : 클로드 페이지용 편집 버전 (전체 데이터, DB에 저장)
"""
import json,os
here=os.path.dirname(os.path.abspath(__file__))
rows=json.load(open(f'{here}/data/rows.json'))
ed=json.load(open(f'{here}/data/edits.json')) if os.path.exists(f'{here}/data/edits.json') else {}
src=open(f'{here}/src/app.html').read()
view=[];stars=[]
extra=[dict(id=k,n=e['n'],a=e.get('a',''),dg=e['dg'],m=0,d='',s=e.get('s','기타'),g=1 if e.get('g') else 0,f='',manual=1) for k,e in ed.items() if e.get('manual') and e.get('n') and e.get('dg')]
for r in rows+extra:
    e=ed.get(r['id'],{}); h=e['h'] if 'h' in e else (e.get('s',r['s'])=='기타' or r.get('y',9)<5 or bool(r.get('sm')))
    if e.get('x'): continue
    hs=False
    if h:
        if e.get('star') and not e.get('x'): hs=True
        else: continue
    r=dict(r); r['s']=e.get('s',r['s'])
    if hs: r['hs']=1
    if 'c' in e: r['c']=bool(e['c'])
    view.append(r)
    if e.get('star'): stars.append(r['id'])
j=lambda o:json.dumps(o,ensure_ascii=False)
VERSION=open(f'{here}/VERSION').read().strip()
def make(data,static,st): return src.replace('__VERSION__',VERSION).replace('__DATA__',j(data)).replace('__STATIC__',static).replace('__STARS__',j(st))
BASE='https://vronana.github.io/food-hunter/'
def head(region,rel):
    return f'''<meta name="theme-color" content="#f7f5f2">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="오늘 뭐먹지">
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
REGION='suji'
mark='<meta name="color-scheme" content="only light">\n'
idx=make(view,'true',stars).replace(mark,mark+head(REGION+'/','../'),1)
os.makedirs(f'{here}/{REGION}',exist_ok=True)
open(f'{here}/{REGION}/index.html','w').write(idx)
mf=open(f'{here}/manifest.webmanifest').read().replace('"icons/','"../icons/')
open(f'{here}/{REGION}/manifest.webmanifest','w').write(mf)
# 옛 주소(루트)는 수지 페이지로 보내 주는 안내 페이지 (링크 미리보기용 정보는 그대로 둠)
root=f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>오늘 뭐먹지</title>
<meta name="color-scheme" content="only light">
<meta name="theme-color" content="#f7f5f2">
<meta property="og:type" content="website">
<meta property="og:site_name" content="오늘 뭐먹지">
<meta property="og:title" content="오늘 뭐먹지">
<meta property="og:description" content="오늘 뭐 먹지? 고민되면 뽑기로 정해 보세요.">
<meta property="og:url" content="{BASE}">
<meta property="og:image" content="{BASE}icons/icon-512.png?v=22">
<meta property="og:locale" content="ko_KR">
<meta name="description" content="오늘 뭐 먹지? 고민되면 뽑기로 정해 보세요.">
<link rel="icon" type="image/png" href="icons/icon-192.png?v=22">
<link rel="apple-touch-icon" href="icons/icon-180.png?v=22">
<meta http-equiv="refresh" content="0;url={REGION}/">
<script>location.replace("{REGION}/"+location.search+location.hash);</script>
<style>body{{margin:0;background:#f7f5f2;font-family:system-ui,sans-serif;color:#2b2622;display:grid;place-items:center;min-height:100vh}}a{{color:#d9622b}}</style>
</head><body><p><a href="{REGION}/">오늘 뭐먹지 열기</a></p></body></html>
'''
open(f'{here}/index.html','w').write(root)
os.makedirs(f'{here}/dist',exist_ok=True)
open(f'{here}/dist/editor.html','w').write(make(rows,'false',[]))
print('viewer',len(view),'stars',len(stars),'| editor',len(rows))
