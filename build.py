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
    if h and not e.get('star'): continue
    r=dict(r); r['s']=e.get('s',r['s'])
    if 'c' in e: r['c']=bool(e['c'])
    view.append(r)
    if e.get('star'): stars.append(r['id'])
j=lambda o:json.dumps(o,ensure_ascii=False)
def make(data,static,st): return src.replace('__DATA__',j(data)).replace('__STATIC__',static).replace('__STARS__',j(st))
open(f'{here}/index.html','w').write(make(view,'true',stars))
os.makedirs(f'{here}/dist',exist_ok=True)
open(f'{here}/dist/editor.html','w').write(make(rows,'false',[]))
print('viewer',len(view),'stars',len(stars),'| editor',len(rows))
