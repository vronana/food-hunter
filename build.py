#!/usr/bin/env python3
"""원본(src/app.html) + 데이터(data/rows.json, data/edits.json) -> 두 가지 결과물
  index.html        : 링크용 보기 전용 (삭제/보류 제외, 별표 반영)
  dist/editor.html  : 클로드 페이지용 편집 버전 (전체 데이터, DB에 저장)
"""
import json,os
here=os.path.dirname(os.path.abspath(__file__))
rows=json.load(open(f'{here}/data/rows.json'))
ed=json.load(open(f'{here}/data/edits.json')) if os.path.exists(f'{here}/data/edits.json') else {}
src=open(f'{here}/src/app.html').read()
view=[];stars=[]
for r in rows:
    e=ed.get(r['id'],{}); h=e['h'] if 'h' in e else e.get('s',r['s'])=='기타'
    if e.get('x'): continue
    if h: continue
    r=dict(r); r['s']=e.get('s',r['s'])
    if 'c' in e: r['c']=bool(e['c'])
    view.append(r)
    if e.get('star'): stars.append(r['id'])
j=lambda o:json.dumps(o,ensure_ascii=False)
VERSION=open(f'{here}/VERSION').read().strip()
def make(data,static,st): return src.replace('__VERSION__',VERSION).replace('__DATA__',j(data)).replace('__STATIC__',static).replace('__STARS__',j(st))
HEAD='''<meta name="theme-color" content="#f7f5f2">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="오늘 뭐먹지">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta property="og:type" content="website">
<meta property="og:site_name" content="오늘 뭐먹지">
<meta property="og:title" content="오늘 뭐먹지">
<meta property="og:description" content="오늘 뭐 먹지? 고민되면 뽑기로 정해 보세요.">
<meta property="og:url" content="https://vronana.github.io/food-hunter/">
<meta property="og:image" content="https://vronana.github.io/food-hunter/icons/icon-512.png?v=22">
<meta property="og:locale" content="ko_KR">
<meta name="description" content="오늘 뭐 먹지? 고민되면 뽑기로 정해 보세요.">
<link rel="manifest" href="manifest.webmanifest?v=22">
<link rel="icon" type="image/png" href="icons/icon-192.png?v=22">
<link rel="apple-touch-icon" href="icons/icon-180.png?v=22">
'''
idx=make(view,'true',stars).replace('<meta name="color-scheme" content="light">\n','<meta name="color-scheme" content="light">\n'+HEAD,1)
open(f'{here}/index.html','w').write(idx)
os.makedirs(f'{here}/dist',exist_ok=True)
open(f'{here}/dist/editor.html','w').write(make(rows,'false',[]))
print('viewer',len(view),'stars',len(stars),'| editor',len(rows))
