# report-sno: 「숫자로 읽는 세상」 레포트 작업 폴더

레포트 과제 **"금쪽같은 휴일, 우리는 어떻게 움직이나?"**의 작업 폴더 뼈대다.
2025년 서울 지하철 승하차 인원, 서울의 기온·강수량, 2025년 휴일 자료로 수업 노션의 **과제 안내 페이지**에 실린 질문에 답한다.
분석은 **코딩 에이전트와 함께 R로** 하고, 결과는 **각자의 노션 페이지**로 낸다.

> **먼저 할 일: 폴더 이름 바꾸기.** 압축을 풀면 생기는 `report-sno` 폴더의 이름을
> **`report-본인의학번`**으로 바꾼다. 예: 학번이 2026123456이면 `report-2026123456`.
> VS Code(Antigravity)로 열기 **전에** 바꾼다. 이미 열었다면 창을 닫고 바꾼 뒤 다시 연다.
> 제출하는 압축 파일 이름도 이 폴더 이름을 따라 `report-본인의학번.zip`이 된다.

## 시작하기

1. 압축을 풀고 폴더 이름 `report-sno`를 `report-본인의학번`으로 바꾼다. 예: `report-2026123456`.
2. 이 폴더를 VS Code(Antigravity)로 **폴더째** 연다. 에이전트는 `AGENTS.md`의 규칙을 읽고 따른다.
3. 수업 노션의 과제 안내 페이지에서 질문과 제공 수치를 읽는다.
   과제 질문을 대화에 붙여 넣어도 된다. 그중 지금 확인하려는 것과 받고 싶은 결과를 자기 말로 덧붙인다.
4. 아래 "데이터 받기"에 따라 원자료 두 개를 `dataset/raw/`에 넣는다.
5. 에이전트에게 요청할 때마다 `dialogues/`에 그날 기록이 남는지 확인한다.

## 폴더 구조

```text
report-sno/
├── AGENTS.md          # 코딩 에이전트가 따를 규칙 (대화 기록, 바깥 숫자, R, ggplot, showtext)
├── CLAUDE.md          # Claude Code용: AGENTS.md를 불러온다
├── dialogues/         # 에이전트와 나눈 대화 기록 (날짜별 .md)
│   ├── README.md      # 기록 규칙
│   └── _template.md   # 기록 서식 견본
├── scripts/           # R 스크립트 (처음엔 비어 있다)
├── dataset/
│   ├── raw/           # 원자료. 손대지 않는다
│   │   └── holidays-2025.csv   # 들어 있음: 2025년 휴일 목록과 유형
│   └── working/       # 정리한 분석용 파일
├── output/            # 표(CSV)와 그림(PNG)
└── report/
    └── outline.md     # 보고서 뼈대
```

`.gitkeep`은 빈 폴더를 유지하려고 둔 빈 파일이다. 지워도 된다.

## 데이터 받기

자료실에서 원자료를 다시 나눠 주지 않는다. [2장 데이터셋 가져오기](https://qmakescl.github.io/class-material/data-science/readtheworld/ch2.html)를
따라 직접 받고, 이름을 바꿔 `dataset/raw/`에 넣는다. 내용은 엑셀로 열어 저장하지 않는다.

| 받는 곳 | 받을 파일 | 바꿀 이름 |
| --- | --- | --- |
| 서울 열린데이터광장, 「서울교통공사_역별 일별 시간대별 승하차인원 정보」 | 2025년 파일(약 24MB) | `seoul-subway-2025.csv` |
| 기상청 기상자료개방포털, 종관기상관측(ASOS) 일 자료 | 서울(108) 지점만, 2025-01-01~2025-12-31, 평균기온·최고기온·일강수량 | `seoul-temp-raining-2025.csv` |

두 파일 모두 EUC-KR로 저장되어 있다. 읽는 법은 2장 2.5절에 있다.

`dataset/raw/holidays-2025.csv`(2025년의 공휴일, 대체공휴일, 임시공휴일, 근로자의 날)는 들어 있다.
UTF-8이고, 열은 `날짜`(2025-01-01 꼴), `요일`, `휴일명`, `유형`(`공휴일`, `대체공휴일`, `임시공휴일`, `근로자의 날`)이다.
주말과 겹친 공휴일(예: 3월 1일 토요일)도 들어 있고, 토요일과 일요일은 따로 적지 않았다.

## 쓸 수 있는 방법

[R과 Python 을 이용해 세상읽기](https://qmakescl.github.io/class-material/data-science/readtheworld/index.html)의
1–6장과 과제, 그리고 수업에서 다룬 자료의 방법을 쓴다. 이 과제는 R만 쓴다.

- 전처리와 조인, 넓은 형식 ↔ 긴 형식, 날짜와 시간대 다루기
- 평균·중앙값·퍼짐, 분포, 집단별 비교, 상관
- 집단을 나누어 다시 보기 ([데이터로 세상을 읽을 때 조심할 것들](https://qmakescl.github.io/class-material/data-science/analysis-traps-three-paradoxes.html))
- ggplot2 시각화 ([ggplot 시각화](https://qmakescl.github.io/class-material/data-science/ggplot-visualization.html))

## 코딩 규칙

`AGENTS.md`에 이 폴더의 규칙이 있다. 요점은 다음과 같다.

- 에이전트는 요청마다 `dialogues/YYYY-MM-DD.md`에 요청 원문, 응답 요약, 바꾼 파일, 실행 결과를 남긴다.
  **내가 확인한 것** 칸은 학생이 직접 쓴다.
- R 코드는 tidyverse로 쓰고(파이프는 `%>%`), 그림은 ggplot2로만 그려 `output/`에 PNG로 저장한다.
- 한글은 showtext로 Google Fonts의 Noto Sans KR을 쓴다.
- 에이전트는 요청한 작업만 하고 권고하지 않는다. 분석의 기준, 방법, 해석은 모두 학생이 정한다.
- 가상 데이터를 만들지 않는다.
- 자료에 없는 바깥 숫자(인구, 분담률 등)는 학생이 출처와 함께 알려 준 것만 쓴다. 과제 안내 페이지의 제공 수치를 쓸 때는 출처와 함께 에이전트에게 알려 준다.

Claude Code는 `CLAUDE.md`를 읽으므로, 그 안의 `@AGENTS.md` 한 줄로 같은 규칙을 불러온다.

## 제출

1. `report/outline.md`의 순서로 각자의 노션에 보고서 페이지를 만든다. 대화 기록과 스크립트는 노션에 붙이지 않는다.
2. 노션의 게시(웹에 게시) 기능으로 공개 URL을 만들고, 로그인하지 않은 창에서 열리는지 확인한다.
3. 작업 폴더를 압축한다(아래 "작업 폴더 압축하기").
4. [제출 양식](https://forms.gle/Sx23qK3XPN19Y1sz6)에 학번과 노션 공개 URL을 적고, 압축 파일을 올린다.
   **노션 URL과 압축 파일이 모두 있어야 제출로 인정한다.** 파일을 올리려면 Google 계정으로 로그인해야 한다.

- **마감: 2026년 11월 28일(토) 23:59.** 이후에는 제출 양식이 닫힌다.
- 마감 뒤에 노션 페이지를 고치면 고친 것으로 본다. 제출한 뒤에는 페이지를 고치지 않는다.

### 작업 폴더 압축하기

작업 폴더(`report-본인의학번/`)를 **통째로** 압축한다. 안의 파일을 고르지 않아도 된다.

- Windows: 작업 폴더에서 마우스 오른쪽 단추 → **ZIP 파일로 압축**(Windows 10은 **보내기 → 압축(ZIP) 폴더**).
- macOS: 작업 폴더에서 마우스 오른쪽 단추 → **압축**.
- 압축 파일 이름이 `report-본인의학번.zip`인지 확인한다. 예: `report-2026123456.zip`.
- 올릴 수 있는 크기는 **100MB까지**다. 넘으면 `dataset/working/`의 큰 파일을 지우고 다시 압축한다.
  이 파일들은 `scripts/`의 스크립트를 다시 실행하면 만들어진다. `dialogues/`와 `scripts/`는 지우지 않는다.
- 올리기 전에 압축 파일을 한 번 풀어 `dialogues/`와 `scripts/`가 들어 있는지 확인한다.

## 필요한 것

- R과 VS Code(또는 Antigravity), R 확장. 설치는 [VS Code에서 R 실행하기](https://qmakescl.github.io/class-material/data-science/VScode-R-languageserver.html)를 따른다.
- R 패키지: tidyverse, showtext. 그림의 한글은 Noto Sans KR 글꼴을 내려받아 쓰므로 처음 한 번은 인터넷이 필요하다.

자료: [Q의 데이터 이야기 자료](https://qmakescl.github.io/class-material/) · CC BY-SA 4.0
