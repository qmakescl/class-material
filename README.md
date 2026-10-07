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
  `docs/things/`, `docs/life/`, 최신순 · 한 행 3개)에 자동 반영됩니다.
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

## 자료 페이지용 데이터 생성 스크립트

`docs/data-science/analysis-traps-three-paradoxes.html`(데이터로 세상을 읽을 때 조심할 것들)은 가상 데이터를 쓰지 않고 실측 자료만 사용한다. 페이지가 읽는
`docs/assets/data/*.js`는 아래 스크립트가 만든다(각각 `window.KBO_REGRESSION`,
`window.GALTON`을 정의하는 생성 파일이므로 직접 수정하지 않는다).

```sh
uv run python src/python/prepare_kbo_regression.py      # docs/assets/data/kbo-regression.js
uv run python src/python/prepare_kbo_traps23.py         # docs/assets/data/kbo-traps23.js
uv run python src/python/prepare_galton_father_son.py   # docs/assets/data/galton-father-son.js
```

- `prepare_kbo_regression.py`는 `datasets/kbo_dashboard.sqlite3`에서 함정 1 데이터를
  만든다. 대상 타자는 **규정타석**(팀당 경기수의 3.1배, 2025 시즌은 144 × 3.1 = 446.4
  → 447타석 이상, 43명)으로 정한다. "전·후반기 모두 충분히 출전"처럼 분석자가 임의로
  정하는 기준을 피하기 위한 선택이며, 이 코호트는 전원이 전·후반기 양쪽에 충분한
  타수를 갖는다. 전·후반기 상·하위 10명의 이동, 선발 타수 N별 (첫 N타수 타율, 이후
  타율) 쌍과 상·하위 25% 집단의 이동, 분산 분해와 축소추정 예측오차를 계산한다.
  이 DB는 `.gitignore` 대상이므로, 먼저 위의 `kbo_dashboard/ingest.py`를 실행해야
  재생성할 수 있다. 그래서 **생성된 `.js`는 저장소에 포함한다.**
- `prepare_kbo_traps23.py`는 같은 DB에서 함정 2·3 데이터를 만든다. 크기 편향을 볼 수
  있는 실측 수량 5종(타석당 투구수, 이닝당 타석수, 한 경기 투수 1명의 투구수, 타자별
  시즌 타석수, 투수별 시즌 투구수), 손으로 검산할 수 있는 실제 한 경기의 투수별
  투구수, 층화 방식 5종별 심슨 역전 쌍 개수와 대표 쌍, 주전 기준 타수를 바꿀 때의
  윌 로저스 현상을 계산한다. 크기 편향 항등식 \(\mu + \sigma^2/\mu\)에는 모집단
  분산(`ddof=0`)을 쓴다.
- `prepare_galton_father_son.py`는 `datasets/galton/Galton.tsv`에서 아버지–아들
  465쌍을 뽑아 기술통계, 양방향 회귀선, 양방향 극단 집단의 이동(대칭성), 겹침
  통계, 중부모 기준 비교를 계산한다. 원자료는 Galton(1886)이며
  <https://www.randomservices.org/random/data/Galton.tsv>에서 받았다.

`docs/ai/regression-to-deep-learning.html`(회귀에서 딥러닝으로)이 읽는 데이터는 아래
두 스크립트가 만든다(`window.GISTEMP_ANNUAL`, `window.MNIST_BRIDGE`를 정의하는 생성
파일이므로 직접 수정하지 않는다).

```sh
uv run python src/python/prepare_gistemp_annual.py   # docs/assets/data/gistemp-annual.js
uv run python src/python/prepare_mnist_bridge.py     # docs/assets/data/mnist-bridge.js
```

- `prepare_gistemp_annual.py`는 위 기온 실습과 같은 원본
  (`datasets/temperature/GLB.Ts+dSST.csv`)에서 연평균 편차 146개 연도를 뽑는다.
- `prepare_mnist_bridge.py`는 MNIST 원본(`datasets/mnist/*.gz`, 약 12MB)이 없으면
  <https://ossci-datasets.s3.amazonaws.com/mnist/>에서 내려받는다(`.gitignore` 대상).
  소프트맥스 회귀(784 → 10)와 은닉층 신경망(784 → 64 → 10)을 같은 설정(시드 2026,
  미니배치 100, 학습률 0.1, 10에폭 SGD)으로 학습해 선형 모형 가중치, 에폭별 훈련 손실·시험
  정확도, 시험 이미지 일부와 오답 사례를 기록한다. numpy만 쓰며 몇 초 안에 끝난다.

## 지하철과 날씨로 배우는 R·Python (여러 쪽 자료)

`docs/data-science/readtheworld/`는 차례(`index.html`)와 여섯 장(`ch1`~`ch6.html`),
과제(`hw.html`)로 된 묶음 자료다. 여덟 쪽이 `docs/assets/readtheworld.css`를 함께
쓰고, `materials.js`에는 차례를 가리키는 항목 하나만 있다.

본문의 코드는 가상 데이터가 아니라 아래 두 원본 파일로 확인했다. 이 파일들은
`docs/`로 배포하지 않으며, 학생은 2장의 안내에 따라 직접 내려받는다.

- `datasets/readtheworld/seoul-subway-2025.csv`: 서울교통공사, 「서울교통공사_역별
  일별 시간대별 승하차인원 정보」 2025년 파일(EUC-KR).
  [서울 열린데이터광장](https://data.seoul.go.kr/dataList/OA-12921/S/1/datasetView.do)
- `datasets/readtheworld/seoul-temp-raining-2025.csv`: 기상청 종관기상관측(ASOS) 일
  자료, 서울(108) 지점, 2025-01-01~2025-12-31, 평균기온·최고기온·일강수량(EUC-KR).
  [기상자료개방포털](https://data.kma.go.kr/data/grnd/selectAsosRltmList.do?pgmNo=36)에서
  **로그인한 뒤** 받는다. 고를 항목은 `docs/assets/images/kma-download.png` 화면과 같다.

두 자료 모두 2025년 한 해(365일)다. 기간을 바꿔 다시 받으면 본문에 적어 둔 행 수와
날짜 수(365, 빈칸 205일 등)도 함께 고친다.

## GitHub Pages 배포

`main` 브랜치에 `docs/` 또는 Pages 워크플로 변경 사항이 푸시되면
`.github/workflows/deploy-pages.yml`이 사이트를 자동 배포합니다. Actions
탭에서 수동으로 실행할 수도 있습니다.

최초 한 번은 GitHub 저장소의 **Settings → Pages → Build and deployment →
Source**를 **GitHub Actions**로 설정해야 합니다. 배포가 완료되면 사이트는
다음 주소에서 제공됩니다.

<https://qmakescl.github.io/class-material/>
