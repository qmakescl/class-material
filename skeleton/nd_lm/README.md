# nd_lm: 정규분포와 회귀분석 실습 폴더

[측정의 흔들림에서 회귀직선까지 - 정규분포로 여는 회귀분석](https://qmakescl.github.io/class-material/data-science/normal-error-regression-intro.html)
자료의 10절 "R로 다시 해 보기"를 따라 하기 위한 작업 폴더의 뼈대다. 1단계(마이컬슨 측정의 오차)와 2단계(갈턴의 아버지–아들 키 회귀)를 이 폴더에서 한다. 폴더 구조와 갈턴의 키 자료가 미리 들어 있다.
이 폴더를 VS Code로 **폴더째** 열고, 자료에 실린 프롬프트를 코딩 에이전트에 붙여 넣거나 R 코드를 직접 실행한다.

## 폴더 구조

```text
nd_lm/
├── AGENTS.md             # 코딩 에이전트가 따를 규칙 (tidyverse, ggplot, showtext)
├── CLAUDE.md             # Claude Code용: AGENTS.md를 불러온다
├── scripts/              # R 스크립트 (처음엔 비어 있다)
├── dataset/
│   ├── raw/              # 원본. 손대지 않는다
│   │   └── Galton.tsv    # 들어 있음: 갈턴(1886)의 부모와 자녀 키 자료
│   └── working/          # 정리한 분석용 파일을 둘 곳
└── output/               # 표(CSV)와 그림(PNG)
```

- 스크립트 안의 경로는 이 폴더(`nd_lm/`)를 기준으로 적는다. VS Code에서 폴더를 열면
  R 터미널의 작업 폴더가 여기가 되어 `dataset/raw/Galton.tsv` 같은 상대 경로가 그대로 통한다.
- `dataset/raw/`의 원본은 고치지 않는다. 단위 변환처럼 고칠 것은 코드로 처리한다.
- `scripts/`, `dataset/working/`, `output/`의 `.gitkeep`은 빈 폴더를 유지하려고 둔 빈 파일이다. 지워도 된다.

## 코딩 규칙

`AGENTS.md`에 이 폴더의 규칙을 적어 두었다. 코딩 에이전트는 이 파일을 먼저 읽고 따른다.

- R 코드는 tidyverse로 쓴다(readr로 읽고 dplyr로 가공, 파이프는 `%>%`).
- 그림은 ggplot2로만 그리고 `output/`에 PNG로 저장한다.
- 한글은 showtext로 Google Fonts의 Noto Sans KR을 쓴다.

Claude Code는 `CLAUDE.md`를 읽으므로, 그 안에 `@AGENTS.md` 한 줄을 넣어 같은 규칙을 불러오게 했다.

## 들어 있는 자료

| 파일 | 내용 |
| --- | --- |
| `dataset/raw/Galton.tsv` | 갈턴(Galton, 1886)이 모은 197가족 898명의 키. 탭으로 구분한 텍스트, 단위는 인치. 열: `Family`(가족 번호), `Father`(아버지 키), `Mother`(어머니 키), `Gender`(자녀 성별, M/F), `Height`(자녀 키), `Kids`(자녀 수). 원자료: <https://www.randomservices.org/random/data/Galton.tsv> |
| (R 내장) `morley` | 마이컬슨(1879)의 빛의 속도 측정 100회. R에 들어 있어 파일이 필요 없다. `Speed`는 빛의 속도(km/s)에서 299,000을 뺀 값 |

## 필요한 것

- R과 VS Code, R 확장. 설치는 [VS Code에서 R 실행하기](https://qmakescl.github.io/class-material/data-science/VScode-R-languageserver.html)를 따른다.
- R 패키지: tidyverse(ggplot2 포함), showtext. 그림의 한글은 showtext로 Noto Sans KR 글꼴을 내려받아 쓰므로 처음 한 번은 인터넷이 필요하다.

자료: [Q의 데이터 이야기 자료](https://qmakescl.github.io/class-material/) · CC BY-SA 4.0
