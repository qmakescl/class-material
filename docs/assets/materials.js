/* 자료 목록의 단일 원본. 새 자료를 발행하면 이 배열 끝에 한 항목을 추가한다.
   홈(최근 3개)과 과목별 목록 페이지(전체, 최신순)가 모두 이 목록을 읽는다.
   - subject: statistics | data-science | ai | things | life
   - href: docs/ 기준 상대 경로 (예: "statistics/foo.html")
   - tags: 과목 1개 + 유형 1개 + 주제 2~5개 (DESIGN.md "태그" 참고)
   - date: 발행일 YYYY-MM-DD (같은 날짜면 배열에서 뒤쪽이 더 최신)
   - practice: true 이면 카드에 '실습 포함' 배지를 단다 (선택) */
window.MATERIALS = [
  {
    subject: "statistics",
    label: "인터랙티브 실습",
    title: "확률에 대하여",
    description: "표본공간과 사건, 조건부확률과 베이즈, 확률변수와 분포, 표집분포와 추론, 다중검정까지 시뮬레이션으로 확인합니다.",
    href: "statistics/grad-probability-lab.html",
    tags: ["통계", "시뮬레이션", "확률", "조건부확률", "베이즈정리", "확률분포"],
    date: "2026-09-12"
  },
  {
    subject: "statistics",
    label: "인터랙티브 실습",
    title: "점추정과 신뢰구간",
    description: "추정량과 추정치, 좋은 추정량의 성질, 95% 신뢰구간의 의미를 표본 추출 시뮬레이션으로 확인합니다.",
    href: "statistics/point-estimation-confidence-interval.html",
    tags: ["통계", "시뮬레이션", "점추정", "신뢰구간", "표본오차"],
    date: "2026-09-18"
  },
  {
    subject: "statistics",
    label: "인터랙티브 실습",
    title: "통계적 가설검정",
    description: "모평균에 대한 검정을 예로 가설, 유의수준, 검정력, p값과 가설검정 절차를 시뮬레이션으로 확인합니다.",
    href: "statistics/hypothesis-testing.html",
    tags: ["통계", "시뮬레이션", "가설검정", "유의수준", "검정력", "p값", "효과크기"],
    date: "2026-09-18"
  },
  {
    subject: "statistics",
    label: "인터랙티브 실습",
    title: "회귀분석 조금 깊이 보기 - 최소제곱과 잔차",
    description: "엑셀 추세선에서 출발해 잔차와 제곱합, R², 잔차 진단까지 단순 선형회귀를 직접 조작하며 확인합니다.",
    href: "statistics/least-squares-residuals.html",
    tags: ["통계", "시각화", "회귀분석", "최소제곱", "잔차", "결정계수"],
    date: "2026-09-21"
  },
  {
    subject: "statistics",
    label: "인터랙티브 실습",
    title: "t 분포와 자유도",
    description: "자유도가 2, 8, 16, 32로 커질 때 t 분포가 표준정규분포에 가까워지는 모습을 겹쳐 확인합니다.",
    href: "statistics/t-distribution-degrees-of-freedom.html",
    tags: ["통계", "시각화", "t분포", "자유도", "표본분포"],
    date: "2026-09-21"
  },
  {
    subject: "ai",
    label: "인공지능 작동이해",
    title: "LLM은 무엇을 배우고, 배운 것을 어떻게 쓰나",
    description: "대규모 언어 모델이 사전학습부터 배포까지 무엇을 배우고, 그 배운 것을 답으로 어떻게 만들어 내는지 단계별 체험과 예시로 확인합니다.",
    href: "ai/llm-what-it-learns.html",
    tags: ["인공지능", "개념정리", "LLM", "사전학습", "파라미터", "토큰"],
    date: "2026-09-25"
  },
  {
    subject: "ai",
    label: "인공지능 작동이해",
    title: "코딩 에이전트는 어떻게 일하나",
    description: "코딩 에이전트를 모델(LLM)과 그것을 감싸는 하네스로 나누어, 글만 쓰는 모델이 도구 호출과 반복으로 실제 작업을 해내는 구조를 단계별 체험과 예시로 확인합니다.",
    href: "ai/coding-agent-how-it-works.html",
    tags: ["인공지능", "개념정리", "코딩에이전트", "하네스", "LLM", "도구호출", "컨텍스트창"],
    date: "2026-09-26"
  },
  {
    subject: "ai",
    label: "MNIST 예제",
    title: "흉부 X선 28×28로 배우는 딥러닝",
    description: "28×28 흉부 X선(PneumoniaMNIST)으로 데이터, 전처리, 모델, 손실, 학습, 평가까지 딥러닝의 전 과정을 단계별로 체험합니다.",
    href: "ai/pneumoniamnist-deep-learning.html",
    tags: ["인공지능", "시각화", "딥러닝", "이미지분류", "손실함수", "모델평가"],
    date: "2026-09-26"
  },
  {
    subject: "ai",
    label: "인터랙티브 실습",
    title: "회귀에서 딥러닝으로 - 직선 하나가 신경망이 되기까지",
    description: "회귀직선을 뉴런 하나로 다시 읽고, 경사하강법·은닉층·소프트맥스를 거쳐 MNIST 분류기까지 실측 자료로 직접 움직여 봅니다.",
    href: "ai/regression-to-deep-learning.html",
    practice: true,
    tags: ["인공지능", "시뮬레이션", "딥러닝", "회귀분석", "경사하강법", "손실함수", "신경망"],
    date: "2026-09-30"
  },
  {
    subject: "data-science",
    label: "인터랙티브 실습",
    title: "지리학과 졸업생의 평균 연봉이 가장 높았다!",
    description: "평균 연봉 1위 이야기를 실제 정부 통계에 조던을 넣어 다시 계산하며, 평균을 읽을 때 먼저 물어볼 것을 확인합니다.",
    href: "data-science/geography-graduate-salary-outlier.html",
    tags: ["데이터과학", "사례분석", "평균", "이상치", "통계해석"],
    date: "2026-09-26"
  },
  {
    subject: "data-science",
    label: "개념 정리",
    title: "데이터로 세상을 읽을 때 조심할 것들",
    description: "평균으로의 회귀, 표집 편향, 심슨의 역설 — 숫자는 맞는데 결론이 틀리는 상황들을 2025년 KBO 실측 기록을 살펴보며, 데이터로 세상 읽기와 깊이 살펴보기로 나누어 확인합니다.",
    href: "data-science/analysis-traps-three-paradoxes.html",
    tags: ["데이터과학", "개념정리", "통계해석", "표본오차", "평균으로의회귀", "심슨의역설", "선택편향"],
    date: "2026-09-30"
  },
  {
    subject: "data-science",
    label: "R·Python 실습",
    title: "R과 Python 을 이용해 세상읽기",
    description: "비 오는 날 지하철 승객은 줄어들까? 2025년 서울 지하철 승하차 인원과 기상청 관측 자료를 찾고, 읽고, 다듬고, 요약하는 과정을 여섯 장과 과제로 나누어 R과 Python으로 나란히 따라 합니다.",
    href: "data-science/readtheworld/index.html",
    practice: true,
    tags: ["데이터과학", "사례분석", "R", "Python", "공공데이터", "데이터전처리", "기술통계"],
    date: "2026-10-07"
  }
];
