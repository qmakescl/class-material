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
  몇 편으로 나뉜 자료는 항목 하나에 `parts`를 적으면 한 카드 안에 편마다 링크가
  나뉘어 그려집니다(예: "R을 이용한 평균검정"의 데이터 준비 · 분석).
- 공통 스타일: `docs/assets/styles.css`
- 용어: 자료에서 쓰는 용어는 [GLOSSARY.md](GLOSSARY.md)를 따릅니다(예: 영가설, 대안가설).
- 형광펜과 메모: 자료 페이지는 `<head>` 끝에 `<script defer src="../assets/annotate.js"></script>`
  한 줄을 넣습니다. 본문을 드래그해 형광펜을 칠하고 메모를 달 수 있고, 내용은 읽는 사람의
  브라우저(`localStorage`)에만 저장됩니다. 자세한 규칙은 [DESIGN.md](DESIGN.md)의 "형광펜과 메모".
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

## 범주형 자료의 가설검정 실습 데이터

`src/R/categorical_sample_data.R`가 `datasets/categorical/`의 원자료로 실습용
자료를 만듭니다. 원자료는 저장소에 올리지 않습니다(`.gitignore`).

- 서울 사망 교통사고: TAAS에서 받은 `taas_2024_seoul_deaths.xlsx`(파일 이름과
  달리 2025년 1~12월 발생 211건)에서 실습에 쓰는 15개 열만 남겨
  `docs/downlodable/서울-사망교통사고-2025.csv`(UTF-8, BOM)로 배포합니다.
- 국민건강영양조사 2024: 기본 DB `hn24_all.sas7bdat`에서 19세 이상의 McNemar
  실습 변수만 뽑아 `datasets/categorical/knhanes24_body_sample.csv`로 둡니다.
  재배포가 금지된 자료라 배포하지 않습니다. 같은 폴더의 `hn24_24rc.sas7bdat`는
  24시간 회상 식품섭취 자료라 쓰지 않습니다.

실습 폴더 뼈대 `skeleton/categorical-tests/`(폴더 구조, 실습용 CSV, `.gitignore`, 안내 README)는
학생이 받아 그대로 쓰는 작업 폴더다. 사이트에서 받을 zip은 아래 명령으로 다시 만든다
(`docs/downlodable/categorical-tests.zip`). 뼈대 안의 파일을 고치면 zip도 다시 만든다.

```sh
uv run python src/python/build_skeleton_zip.py
```

받는 방법(zip, `npx degit qmakescl/class-material/skeleton/categorical-tests`, git sparse checkout)은
자료 페이지 02절 "이 폴더를 한 번에 받기"에 있다.

`src/R/categorical_check.R`는 `docs/statistics/categorical-test-with-r.html`
본문의 수치를 다시 계산해 콘솔에 출력합니다.

```sh
Rscript src/R/categorical_sample_data.R
Rscript src/R/categorical_check.R
```

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

`docs/data-science/normal-error-regression-intro.html`(측정의 흔들림에서 회귀직선까지)은
위의 `galton-father-son.js`와 아래 R 스크립트가 만드는 마이컬슨 측정 자료를 읽는다.

```sh
Rscript src/R/prepare_michelson_morley.R   # docs/assets/data/michelson-morley.js
```

- `prepare_michelson_morley.R`는 R 기본 자료 `datasets::morley`(Michelson 1879년의 빛의
  속도 측정 100회)를 km/s로 바꿔 평균·표준편차, 평균 ±1·±2 표준편차 안의 비율과 함께
  내보낸다. 별도 원자료 파일이 필요 없다.
- 같은 자료의 10절 R 실습은 실습 폴더 뼈대 `skeleton/nd_lm/`(폴더 구조, 갈턴 원자료
  `dataset/raw/Galton.tsv` 사본, `.gitignore`, 안내 README, 코딩 에이전트 규칙 `AGENTS.md`와 이를 불러오는 `CLAUDE.md`)을 쓴다. 사이트에서 받을
  `docs/downlodable/nd_lm.zip`은 `uv run python src/python/build_skeleton_zip.py nd_lm`으로
  다시 만든다. 뼈대 안의 파일을 고치면 zip도 다시 만든다.

`docs/data-science/mendel-chi-square-intro.html`(멘델의 독립 법칙은 조작일까? - 카이제곱 통계량 소개)의 10절 "컴퓨터로 확인하기"(멘델 검정, 폴더 받는 방법도 이 절에 있다)와 11절 "주사위로 실험하기"(웰던의 주사위 실험 재현)는
실습 폴더 뼈대 `skeleton/chisq-dice/`를 쓴다. 래비(2009)의 실제 주사위 기록 `dataset/raw/labby_2009_faces.csv`(눈별 개수 6행, Rundel 2013
Duke STA 102 Lecture 13 5쪽의 표), 빈 `scripts/`·`dataset/working/`·`output/`, `.gitignore`(흉내 낸 결과 `dataset/working/*.rds` 제외),
안내 README, 코딩 에이전트 규칙 `AGENTS.md`(R·tidyverse·ggplot2·showtext의 Noto Sans KR, 시드를 정하고 흉내 낸 결과를 실측 자료와
섞지 않는 규칙)와 이를 불러오는 `CLAUDE.md`가 들어 있다. 웰던 본인의 집계는 없어 컴퓨터로 흉내 내어 재현한다.
페이지의 "주사위 12개 던지기" 위젯은 웰던(1894)의 실험처럼 주사위 12개를 한 번에 던지는 횟수(20~200,000번)를 골라 브라우저에서 1/6 확률로 흉내 내는 시연이며, 비교용 "래비의 실제 기록"은 같은 표의 실측 개수를 쪽 스크립트에 그대로 적은 것이다.
사이트에서 받을 `docs/downlodable/chisq-dice.zip`은 `uv run python src/python/build_skeleton_zip.py chisq-dice`로 다시 만든다.
뼈대 안의 파일을 고치면 zip도 다시 만든다. 11절의 참고 R 코드 세 편(`weldon_sim.R`, `labby_compare.R`, `weldon_successes.R`)은 이 뼈대의 사본에서 실행해 확인했다.

`docs/statistics/regression-analysis.html`(회귀분석 - 상관에서 위계적 회귀까지)은 갈턴 자녀
898명과 Beat the Blues 임상시험(R 패키지 HSAUR3의 `BtheB`) 97명을 읽고, 회귀계수는 쪽의
스크립트가 직접 계산한다. 본문의 수치는 검산 스크립트로 대조한다.

```sh
Rscript src/R/prepare_regression_data.R   # docs/assets/data/regression-galton-btheb.js (HSAUR3 필요)
Rscript src/R/regression_check.R          # 본문 수치 검산 (HSAUR3, car, emmeans, lmtest가 없으면 그 부분만 건너뜀)
```

같은 자료의 01–08절 끝 "프롬프트로 따라 하기"(분석 → 보고서, 원자료를 다듬거나 factor 순서를 정하는 01·05·07절만 그 앞에 데이터 처리)는 이 자료 전용 실습 폴더 뼈대 `skeleton/regression/`을 쓴다. 갈턴 원자료 `dataset/raw/Galton.tsv` 사본, 빈 `scripts/`·`dataset/working/`·`output/`, `.gitignore`, 안내 README, 코딩 에이전트 규칙 `AGENTS.md`(R·그림·한글·패키지·factor·보고서 규칙)와 이를 불러오는 `CLAUDE.md`가 들어 있다. 페이지 00절의 보고서 규칙은 이 `AGENTS.md`의 "보고서 규칙" 절을 그대로 옮긴 것이므로, 한쪽을 고치면 다른 쪽도 고친다. 사이트에서 받을 `docs/downlodable/regression.zip`은 `uv run python src/python/build_skeleton_zip.py regression`으로 다시 만든다. 09절 부록의 R 코드 11편과 출력은 이 뼈대의 사본에서 실행한 그대로다(07절만 HSAUR3가 더 필요).

「숫자로 읽는 세상」 레포트 과제 "금쪽같은 휴일, 우리는 어떻게 움직이나?"(2025년 서울
지하철·기상 자료, R 전용, 마감 2026-11-28)의 작업 폴더 뼈대는 `skeleton/report-sno/`다.
질문과 제공 수치는 뼈대에 넣지 않고 수업 노션의 과제 안내 페이지에만 둔다(에이전트가 과제를 대신 풀지 않게). `AGENTS.md`가 에이전트에게 요청마다
`dialogues/YYYY-MM-DD.md`에 요청 원문·응답 요약·바꾼 파일·실행 결과를 남기게 하고,
출처 없는 바깥 숫자를 쓰지 못하게 한다. 지하철·기상 원자료는 넣지 않고(학생이 직접 받는다),
2025년 휴일 목록 `dataset/raw/holidays-2025.csv`(공휴일·대체공휴일·임시공휴일·근로자의 날)만 넣는다. 배포는 zip으로만 하며
`uv run python src/python/build_skeleton_zip.py report-sno`로
`docs/downlodable/report-sno.zip`을 다시 만든다.

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

`docs/ai/mnist-classifier-practice.html`(MNIST 손글씨 분류기 만들기)이 읽는 데이터는 아래 스크립트가
만든다(`window.MNIST_PRACTICE`를 정의하는 생성 파일이므로 직접 수정하지 않는다).

```sh
uv run --with torch python src/python/prepare_mnist_practice.py   # docs/assets/data/mnist-practice.js
```

- 자료 페이지의 실습과 같은 순서·같은 설정으로 PyTorch로 학습한다. 훈련 60,000장을 시드 42로
  훈련 54,000장·검증 6,000장으로 나누고, 은닉층 신경망(784 → 64 → 10, 30에폭)과 작은 합성곱
  신경망(Conv 16 → Conv 32 → Linear 10, 15에폭)을 미니배치 100, SGD 학습률 0.1로 학습한다.
  에폭별 훈련·검증 손실, 검증 손실이 가장 낮았던 에폭의 시험 정확도, 혼동행렬과 오답 사례,
  시험 사진을 오른쪽으로 0~4칸 밀었을 때의 정확도, 첫 합성곱 층의 필터 16개를 기록한다.
  덧붙여 255로 나누지 않고 1에폭 학습한 결과와, 은닉층 신경망을 같은 출발점에서 100에폭까지
  학습한 기록(오래 학습하면 검증 손실이 다시 오르는 것을 보이는 데 쓴다)도 남긴다.
- `torch`는 저장소 의존성(`pyproject.toml`)에 넣지 않고 `--with torch`로 실행할 때만 불러온다.
  MNIST 원본은 `prepare_mnist_bridge.py`가 받아 둔 `datasets/mnist/*.gz`를 쓴다. CPU로 1~2분 걸린다.

## R과 Python 을 이용해 세상읽기 (여러 쪽 자료)

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
