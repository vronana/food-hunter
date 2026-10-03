# 오늘 뭐먹지 (food-hunter)

가족 외식 맛집 목록. 링크: https://vronana.github.io/food-hunter/

- `src/app.html` — 화면과 기능의 원본 (여기만 고치면 됨)
- `data/rows.json` — 지역별 가게 데이터 (현재: 수지구)
- `data/edits.json` — 주인이 정한 분류·별표·보류·삭제 (편집 페이지에서 가져옴)
- `build.py` — 위 파일들로 `index.html`(링크용 보기 전용)과 `dist/editor.html`(편집용)을 만듦
