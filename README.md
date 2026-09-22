# Class Material

수업에서 사용할 정적 HTML 자료를 관리하고 GitHub Pages로 배포하는
프로젝트입니다. 실제 사이트 파일은 `docs/`에 있습니다.

## 로컬 미리보기

Python 3.12와 [`uv`](https://docs.astral.sh/uv/)가 필요합니다.

```sh
uv sync
uv run python main.py
```

브라우저에서 <http://127.0.0.1:8000>을 열어 확인합니다. 다른 포트를
사용하려면 `uv run python main.py --port 8080`처럼 실행합니다.

## 자료 편집

- 페이지 내용: `docs/index.html`
- 자료 목록: `docs/assets/materials.js`에 항목을 추가하면 홈(과목별 최근 3개)과
  과목별 목록 페이지(`docs/statistics/`, `docs/data-science/`, `docs/ai/`,
  `docs/common/`, `docs/life/`, 최신순 · 한 행 3개)에 자동 반영됩니다.
- 공통 스타일: `docs/assets/styles.css`
- 이미지와 첨부 자료: `docs/assets/` 아래에 추가

수식은 `docs/assets/katex/`의 KaTeX로 표기합니다(`\\( ... \\)`, `\\[ ... \\]`).
사용법은 [DESIGN.md](DESIGN.md)의 "수식 표기"를 참고하세요.

GitHub Pages의 프로젝트 사이트 경로에서도 동작하도록 내부 링크에는 `/`로
시작하는 절대 경로 대신 상대 경로를 사용합니다.

공유 미리보기(Open Graph)는 `docs/assets/images/`의 과목별 PNG 아이콘을
사용합니다. 페이지를 새로 추가할 때는 [DESIGN.md](DESIGN.md)의 과목별
아이콘 매핑과 절대 URL 규칙을 함께 적용합니다.

## 회귀분석 실습용 연간 평균기온 데이터셋

`src/python/build_temperature_dataset.py`가 NASA GISTEMP(GISS Surface
Temperature Analysis v4)의 공개 월별 편차표에서 연평균(J-D)만 뽑아
`docs/downlodable/연간평균기온-실습데이터.xlsx`를 생성합니다. 1880–2025년,
146개 연도의 "연도–지구 연평균기온편차(℃)"이며, 최소제곱과 잔차 실습처럼
연도를 x로 둔 단순 선형회귀 실습에 바로 쓸 수 있습니다.

```sh
uv sync
uv run python src/python/build_temperature_dataset.py
```

원본 자료는 `datasets/temperature/GLB.Ts+dSST.csv`이며, 최신 자료로 갱신하려면
<https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv>를 다시
내려받아 덮어쓰고 스크립트를 재실행합니다. 인용: GISTEMP Team, 2026: GISS
Surface Temperature Analysis (GISTEMP), version 4. NASA Goddard Institute for
Space Studies.

## KBO 2025 타석 탐색 대시보드 (로컬 전용)

`src/python/kbo_dashboard/`에 있는 로컬 전용 도구로, Hugging Face
[`slothman3878/kbo_playbyplay`](https://huggingface.co/datasets/slothman3878/kbo_playbyplay)
(CC BY 4.0) 2025시즌 데이터를 sqlite3 DB로 변환해 팀·타자·주자 상황·타석 결과
(events)·타석당 득점을 필터링해 보여준다. GitHub Pages로 배포되지 않으며,
원본 데이터를 재배포하지 않는다 (`datasets/*.parquet`, `datasets/*.sqlite3`는
`.gitignore` 처리됨).

```sh
uv sync
uv run python src/python/kbo_dashboard/ingest.py   # datasets/kbo_dashboard.sqlite3 생성
uv run python src/python/kbo_dashboard/app.py       # http://127.0.0.1:5050
```

## GitHub Pages 배포

`main` 브랜치에 `docs/` 또는 Pages 워크플로 변경 사항이 푸시되면
`.github/workflows/deploy-pages.yml`이 사이트를 자동 배포합니다. Actions
탭에서 수동으로 실행할 수도 있습니다.

최초 한 번은 GitHub 저장소의 **Settings → Pages → Build and deployment →
Source**를 **GitHub Actions**로 설정해야 합니다. 배포가 완료되면 사이트는
다음 주소에서 제공됩니다.

<https://qmakescl.github.io/class-material/>
