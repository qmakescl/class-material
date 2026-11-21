# regression: 회귀분석 실습 폴더

[회귀분석 - 상관에서 위계적 회귀까지](https://qmakescl.github.io/class-material/statistics/regression-analysis.html)
자료의 01–08절 "프롬프트로 따라 하기"를 하기 위한 작업 폴더의 뼈대다. 폴더 구조, 갈턴의 키 자료,
코딩 에이전트가 따를 규칙(`AGENTS.md`)이 미리 들어 있다.
이 폴더를 VS Code로 **폴더째** 열고, 자료에 실린 프롬프트를 코딩 에이전트에 차례로 붙여 넣는다.

## 폴더 구조

```text
regression/
├── AGENTS.md             # 코딩 에이전트가 따를 규칙 (R, 그림, 한글, 패키지, 보고서)
├── CLAUDE.md             # Claude Code용: AGENTS.md를 불러온다
├── scripts/              # R 스크립트 (처음엔 비어 있다)
├── dataset/
│   ├── raw/              # 원본. 손대지 않는다
│   │   └── Galton.tsv    # 들어 있음: 갈턴(1886)의 부모와 자녀 키 자료
│   └── working/          # 데이터 처리 단계가 저장한 분석용 파일 (.rds)
└── output/               # 표(CSV), 그림(PNG), 보고서(.md)
```

- 스크립트 안의 경로는 이 폴더(`regression/`)를 기준으로 적는다. VS Code에서 폴더를 열면
  R 터미널의 작업 폴더가 여기가 되어 `dataset/raw/Galton.tsv` 같은 상대 경로가 그대로 통한다.
- `scripts/`, `dataset/working/`, `output/`의 `.gitkeep`은 빈 폴더를 유지하려고 둔 빈 파일이다. 지워도 된다.

## 실습의 순서

절마다 **분석 → 보고서**의 두 프롬프트를 준다. 01절(원자료를 cm로 정리), 05절(성별을 factor로 만들고
기준 범주 정하기), 07절(임상시험 자료 들이기)만 그 앞에 **데이터 처리** 프롬프트가 하나 더 있다.

| 단계 | 하는 일 | 남는 파일 |
| --- | --- | --- |
| 데이터 처리 | 원자료를 들여와 단위·범주·결측을 정리한다 | `dataset/working/*.rds` |
| 분석 | 모형을 적합하고 결과 표와 그림을 저장한다 | `output/regNN_*.csv`, `output/regNN_*.png` |
| 보고서 | 저장된 표만 읽고 결과 문단과 표를 쓴다 | `output/regNN_report.md` |

02–06, 08절은 01절이 만든 `dataset/working/galton_cm.rds`를 읽으므로 01절부터 시작한다.

## 코딩 규칙

`AGENTS.md`에 이 폴더의 규칙을 적어 두었다. 코딩 에이전트는 이 파일을 먼저 읽고 따른다.

- R 코드는 tidyverse로 쓰고, 모형 결과는 broom으로 표로 정리해 `output/`에 CSV로 저장한다.
- 범주형 변수는 factor로 만들고 범주의 순서(기준 범주)를 직접 정한다.
- 그림은 ggplot2로만 그리고, 한글은 showtext로 Google Fonts의 Noto Sans KR을 쓴다.
- 보고서는 APA 양식으로, 회귀모형이면 모형의 유의성 표와 계수표를 반드시 넣는다.

Claude Code는 `CLAUDE.md`를 읽으므로, 그 안에 `@AGENTS.md` 한 줄을 넣어 같은 규칙을 불러오게 했다.

## 들어 있는 자료

| 파일 | 내용 |
| --- | --- |
| `dataset/raw/Galton.tsv` | 갈턴(Galton, 1886)이 모은 197가족 898명의 키. 탭으로 구분한 텍스트, 단위는 인치. 열: `Family`(가족 번호), `Father`(아버지 키), `Mother`(어머니 키), `Gender`(자녀 성별, M/F), `Height`(자녀 키), `Kids`(자녀 수). 원자료: <https://www.randomservices.org/random/data/Galton.tsv> |
| (R 패키지 HSAUR3) `BtheB` | Beat the Blues 우울증 임상시험(Proudfoot 외, 2003) 100명. 07절에서 패키지에서 꺼내 `dataset/raw/btheb.csv`로 사본을 남긴다 |

## 필요한 것

- R과 VS Code, R 확장. 설치는 [VS Code에서 R 실행하기](https://qmakescl.github.io/class-material/data-science/VScode-R-languageserver.html)를 따른다.
- R 패키지: tidyverse(ggplot2, broom 포함), showtext. 07절만 HSAUR3가 더 필요하다.
  그림의 한글은 showtext로 Noto Sans KR 글꼴을 내려받아 쓰므로 처음 한 번은 인터넷이 필요하다.

자료: [Q의 데이터 이야기 자료](https://qmakescl.github.io/class-material/) · CC BY-SA 4.0
