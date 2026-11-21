# chisq-dice: 카이제곱 검정 실습 폴더

[멘델의 독립 법칙은 조작일까? - 카이제곱 통계량 소개](https://qmakescl.github.io/class-material/data-science/mendel-chi-square-intro.html)
자료의 10절 "컴퓨터로 확인하기"와 11절 "주사위로 실험하기"를 따라 하기 위한 작업 폴더의 뼈대다.

- 10절: 멘델의 완두 556개로 적합도 검정을 R로 확인한다(숫자는 프롬프트에 있어 자료 파일이 필요 없다).
- 11절: 웰던(1894)이 주사위 12개를 한 번에 던지기를 26,306번 되풀이한 실험을 컴퓨터로 재현한다.
  던진 횟수를 20번에서 200,000번까지 늘려 가며 이론(각 눈 1/6)과 실제의 차이, 카이제곱 통계량이
  어떻게 달라지는지 보고, 같은 실험을 실제 주사위로 되풀이한 래비(2009)의 기록과 견준다.

이 폴더를 VS Code로 **폴더째** 열고, 자료에 실린 프롬프트를 코딩 에이전트에 붙여 넣는다.

## 폴더 구조

```text
chisq-dice/
├── AGENTS.md                     # 코딩 에이전트가 따를 규칙 (R, tidyverse, ggplot2, showtext)
├── CLAUDE.md                     # Claude Code용: AGENTS.md를 불러온다
├── scripts/                      # R 스크립트 (처음엔 비어 있다)
├── dataset/
│   ├── raw/
│   │   └── labby_2009_faces.csv  # 래비(2009)의 실제 주사위 기록: 눈별 개수
│   └── working/                  # 컴퓨터로 흉내 낸 결과를 둘 곳
└── output/                       # 표(CSV)와 그림(PNG)
```

- 스크립트 안의 경로는 이 폴더(`chisq-dice/`)를 기준으로 적는다. VS Code에서 폴더를 열면
  R 터미널의 작업 폴더가 여기가 되어 `dataset/raw/labby_2009_faces.csv` 같은 상대 경로가 그대로 통한다.
- `scripts/`, `dataset/working/`, `output/`의 `.gitkeep`은 빈 폴더를 유지하려고 둔 빈 파일이다. 지워도 된다.
- 흉내 낸 결과(`dataset/working/*.rds`)는 크고 같은 시드로 다시 만들 수 있어 `.gitignore`에 넣었다.

## 들어 있는 자료

| 파일 | 내용 |
| --- | --- |
| `dataset/raw/labby_2009_faces.csv` | 래비(Labby, 2009)가 기계로 주사위 12개를 한 번에 던지기를 26,306번 되풀이해 센 눈별 개수(모두 315,672개). 열: `face`(눈, 1~6), `observed`(나온 횟수). 출처: Rundel, C. (2013). [Lecture 13 – χ² Tests](https://www2.stat.duke.edu/courses/Spring13/sta102.001/Lec/Lec13.pdf), Statistics 102, Duke University, 5쪽의 표. 실측 자료이므로 고치지 않는다. |

웰던 본인의 집계는 들어 있지 않다. 웰던의 실험은 컴퓨터로 흉내 내어 재현한다.

## 코딩 규칙

`AGENTS.md`에 이 폴더의 규칙을 적어 두었다. 코딩 에이전트는 이 파일을 먼저 읽고 따른다.

- R 코드는 tidyverse로 쓴다(readr로 읽고 dplyr로 가공, 파이프는 `%>%`).
- 그림은 ggplot2로만 그리고 `output/`에 PNG로 저장한다.
- 한글은 showtext로 Google Fonts의 Noto Sans KR을 쓴다.
- 난수를 쓸 때는 시드를 정하고 알린다. 흉내 낸 결과는 `dataset/working/`에 두고 실측 자료와 섞지 않는다.

Claude Code는 `CLAUDE.md`를 읽으므로, 그 안에 `@AGENTS.md` 한 줄을 넣어 같은 규칙을 불러오게 했다.

## 필요한 것

- R과 VS Code, R 확장. 설치는 [VS Code에서 R 실행하기](https://qmakescl.github.io/class-material/data-science/VScode-R-languageserver.html)를 따른다.
- R 패키지: tidyverse(ggplot2 포함), showtext. 그림의 한글은 showtext로 Noto Sans KR 글꼴을 내려받아 쓰므로 처음 한 번은 인터넷이 필요하다.

자료: [Q의 데이터 이야기 자료](https://qmakescl.github.io/class-material/) · CC BY-SA 4.0
