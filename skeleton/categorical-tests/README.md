# categorical-tests: 범주형 자료의 가설검정 실습 폴더

[범주형 자료의 가설검정](https://qmakescl.github.io/class-material/statistics/categorical-test-with-r.html)
자료를 따라 하기 위한 작업 폴더의 뼈대다. 폴더 구조와 실습용 사고 자료가 미리 들어 있다.
이 폴더를 VS Code로 **폴더째** 열고, 자료에 실린 프롬프트를 코딩 에이전트에 붙여 넣어 시작한다.

## 폴더 구조

```text
categorical-tests/
├── scripts/              # 에이전트가 만든 R 스크립트 (처음엔 비어 있다)
├── dataset/
│   ├── raw/              # 내려받은 원본. 손대지 않는다
│   │   ├── 서울-사망교통사고-2025.csv   # 들어 있음: 2025년 서울 사망 교통사고 211건
│   │   └── knhanes/      # 국민건강영양조사 hn24_all.sas7bdat 를 각자 넣는다
│   └── working/          # 정리한 분석용 파일 (.rds)
└── output/               # 표(CSV)와 그림(PNG)
```

- 스크립트 안의 경로는 이 폴더(`categorical-tests/`)를 기준으로 적는다. VS Code에서 폴더를 열면
  R 터미널의 작업 폴더가 여기가 되어 `dataset/raw/...` 같은 상대 경로가 그대로 통한다.
- `dataset/raw/`의 원본은 고치지 않는다. 고칠 것이 있으면 코드로 고쳐 `dataset/working/`에 저장한다.
- `scripts/`, `dataset/working/`, `output/`의 `.gitkeep`은 빈 폴더를 유지하려고 둔 빈 파일이다. 지워도 된다.

## 들어 있는 자료와 각자 준비할 자료

| 파일 | 내용 | 준비 |
| --- | --- | --- |
| `dataset/raw/서울-사망교통사고-2025.csv` | 도로교통공단 교통사고분석시스템(TAAS)의 2025년 서울 사망 교통사고 211건, 15개 열. UTF-8 | 들어 있음 |
| `dataset/raw/knhanes/hn24_all.sas7bdat` | 국민건강영양조사 2024 기본 DB | 각자 신청해 내려받는다 ([안내](dataset/raw/knhanes/README.md)) |
| `dataset/raw/btheb.csv` | 우울증 임상시험 BtheB (R 패키지 HSAUR3) | 05절 프롬프트가 스크립트로 만든다 |

## 필요한 것

- R과 VS Code, R 확장. 설치는 [VS Code에서 R 실행하기](https://qmakescl.github.io/class-material/data-science/VScode-R-languageserver.html)를 따른다.
- R 패키지: tidyverse, haven, janitor, effectsize, showtext. 05절은 HSAUR3, car, emmeans도 쓴다.
  에이전트가 설치 전에 허락을 구하도록 프롬프트에 적어 두었다.

## 이 폴더를 자기 저장소로 관리할 때

`.gitignore`가 국민건강영양조사 원시자료(`dataset/raw/knhanes/`)와 그 가공본(`dataset/working/kn_*.rds`)을
커밋하지 않게 막는다. 이 자료는 이용 조건상 다시 나눠 줄 수 없으므로 이 설정을 지우지 않는다.

자료: [Q의 데이터 이야기 자료](https://qmakescl.github.io/class-material/) · CC BY-SA 4.0
