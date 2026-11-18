# AGENTS.md

이 폴더에서 일하는 코딩 에이전트(Codex, Claude Code 등)가 따르는 규칙이다.
사람이 R 코드를 직접 쓸 때도 같은 규칙을 따른다.

## 이 폴더

[측정의 흔들림에서 회귀직선까지](https://qmakescl.github.io/class-material/data-science/normal-error-regression-intro.html)
자료의 10절 "R로 다시 해 보기"를 따라 하는 실습 폴더다.

- 1단계: R 내장 자료 `morley`(마이컬슨의 빛의 속도 측정 100회)로 오차가 정규분포를 이루는지 확인한다.
- 2단계: `dataset/raw/Galton.tsv`(갈턴의 부모와 자녀 키)로 아버지 키와 아들 키의 회귀분석을 한다.

## 폴더와 경로

```text
nd_lm/
├── AGENTS.md        # 이 규칙
├── scripts/         # R 스크립트 (.R)
├── dataset/
│   ├── raw/         # 원자료. 읽기만 한다
│   └── working/     # 정리한 분석용 자료
└── output/          # 표(CSV)와 그림(PNG)
```

- 작업 폴더는 언제나 `nd_lm/`이다. 스크립트 안의 경로는 이 폴더를 기준으로 한 상대 경로로
  적는다. 예: `dataset/raw/Galton.tsv`, `output/galton-regression.png`.
- `setwd()`나 사용자 컴퓨터의 절대 경로(`/Users/...`, `C:\...`)를 쓰지 않는다.
- `dataset/raw/`의 파일은 고치거나 덮어쓰지 않는다. 단위 변환(인치 → cm, `× 2.54`)처럼
  고칠 것은 코드에서 처리하고, 저장이 필요하면 `dataset/working/`에 새 파일로 쓴다.
- 스크립트는 `scripts/`에, 그림과 표는 `output/`에 둔다. 파일 이름은 영문 소문자와 `-`, `_`로 쓴다.

## R 규칙

- **tidyverse를 쓴다.** 스크립트 맨 위에서 `library(tidyverse)`로 불러온다.
  - 파일은 readr(`read_tsv()`, `read_csv()`, `write_csv()`)로 읽고 쓴다.
  - 자료 가공은 dplyr(`filter()`, `mutate()`, `select()`, `summarise()`, `across()`)로 한다.
  - 파이프는 tidyverse(magrittr)의 `%>%`를 쓴다. R 기본 파이프 `|>`는 쓰지 않는다.
  - base R의 `read.delim()`, `subset()`, `$<-`로 열 만들기, `apply` 계열로 요약하기는 쓰지 않는다.
- 모형 적합(`lm()`, `predict()`, `resid()`, `sigma()` 등)은 R 기본 함수를 그대로 쓴다.
- 표의 숫자가 잘려 보이지 않도록 스크립트 앞부분에 `options(pillar.sigfig = 7)`을 둔다.
- 결과를 사람에게 보일 때는 단위(km/s, cm)를 함께 적는다.

## 시각화 규칙

- **그림은 tidyverse에 들어 있는 ggplot2로만 그린다.** base 그래픽(`plot()`, `hist()`,
  `curve()`, `barplot()`)과 다른 그래픽 패키지는 쓰지 않는다.
- 그림은 `ggsave()`로 `output/`에 PNG로 저장한다. 크기는 인치로 정한다(예: `width = 7, height = 5`).
- 축 이름과 제목은 한국어로 쓰고, 단위를 괄호로 붙인다. 예: `"아버지 키 (cm)"`.
- 색은 자료 점·막대에 `#2f6fed`(파랑), 정규분포 곡선에 `#e2662a`(주황), 직선·평균에 `#0b1220`을 쓴다.

## 한글 글꼴 규칙

- **한글은 showtext로 Google Fonts의 Noto Sans KR을 쓴다.** 스크립트 앞부분에 다음을 둔다.

  ```r
  library(showtext)
  font_add_google("Noto Sans KR", "notosanskr")
  showtext_auto()
  showtext_opts(dpi = 300)   # ggsave()의 기본 해상도와 맞춘다
  ```

- ggplot의 테마에는 `base_family = "notosanskr"`를 준다. 예: `theme_minimal(base_family = "notosanskr")`.
- extrafont, 시스템에 설치된 다른 한글 글꼴, `par(family = ...)`는 쓰지 않는다.
- `font_add_google()`은 처음 한 번 인터넷에서 글꼴을 내려받는다. 인터넷이 없어 실패하면
  다른 글꼴로 바꾸지 말고 그 사실을 사용자에게 알린다.

## 패키지

- 필요한 패키지는 tidyverse와 showtext 두 가지다.
- 설치되어 있지 않으면 마음대로 설치하지 말고, 설치 명령
  `install.packages(c("tidyverse", "showtext"))`을 사용자에게 알려 동의를 받은 뒤 실행한다.

## 실행과 보고

- 스크립트를 쓰면 `nd_lm/`에서 `Rscript scripts/<파일>.R`로 실제로 실행해 오류가 없는지 확인한다.
- 사용자에게는 실행한 명령, 콘솔에 나온 주요 수치, 저장한 파일 경로를 알린다.
  숫자를 지어내거나 실행하지 않은 결과를 적지 않는다.
- 설명은 한국어로 한다. 통계 용어는 자료 페이지의 표기를 따른다(예: 영가설, 대안가설, z 점수).
