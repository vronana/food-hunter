# 오늘 뭐먹지 (food-hunter)

가족 외식 맛집 목록. 링크: https://vronana.github.io/food-hunter/suji/ (옛 주소 .../food-hunter/ 는 자동으로 여기로 이동)

- `src/app.html` — 화면과 기능의 원본 (여기만 고치면 됨)
- `data/rows.json` — 지역별 가게 데이터 (현재: 수지구)
- `data/edits.json` — 주인이 정한 분류·별표·보류·삭제 (편집 페이지에서 가져옴)
- `build.py` — 위 파일들로 `suji/index.html`(링크용 보기 전용), `index.html`(옛 주소 안내/이동), `dist/editor.html`(편집용)을 만듦
- 운중동: `tools/make_unjung.py`(성남시 CSV 2개 → `data/unjung/rows.json`), `build_unjung.py`(src/app.html에 운중동용 패치를 메모리에서 적용해 `unjung/index.html`, `dist/unjung-editor.html` 생성). 수지 파일은 건드리지 않음
- 새 지역은 `src/app.html` 의 `REGION` 과 `build.py` 의 `REGION`, 데이터 폴더를 지역별로 나눠 같은 방식으로 추가
