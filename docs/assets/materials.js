/* 자료 목록의 단일 원본. 새 자료를 발행하면 이 배열 끝에 한 항목을 추가한다.
   홈(최근 3개)과 과목별 목록 페이지(전체, 최신순)가 모두 이 목록을 읽는다.
   - subject: statistics | data-science | ai | common | life
   - href: docs/ 기준 상대 경로 (예: "statistics/foo.html")
   - date: 발행일 YYYY-MM-DD (같은 날짜면 배열에서 뒤쪽이 더 최신) */
window.MATERIALS = [
  {
    subject: "statistics",
    label: "인터랙티브 실습",
    title: "확률에 대하여",
    description: "표본공간과 사건, 조건부확률과 베이즈, 확률변수와 분포, 표집분포와 추론, 다중검정까지 시뮬레이션으로 확인합니다.",
    href: "statistics/grad-probability-lab.html",
    date: "2026-09-12"
  },
  {
    subject: "statistics",
    label: "인터랙티브 실습",
    title: "점추정과 신뢰구간",
    description: "추정량과 추정치, 좋은 추정량의 성질, 95% 신뢰구간의 의미를 표본 추출 시뮬레이션으로 확인합니다.",
    href: "statistics/point-estimation-confidence-interval.html",
    date: "2026-09-18"
  },
  {
    subject: "statistics",
    label: "인터랙티브 실습",
    title: "통계적 가설검정",
    description: "가설, 유의수준, 검정력, p값과 가설검정 절차를 시뮬레이션으로 확인합니다.",
    href: "statistics/hypothesis-testing.html",
    date: "2026-09-18"
  },
  {
    subject: "statistics",
    label: "인터랙티브 실습",
    title: "회귀분석 조금 깊이 보기 - 최소제곱과 잔차",
    description: "엑셀 추세선에서 출발해 잔차와 제곱합, R², 잔차 진단까지 단순 선형회귀를 직접 조작하며 확인합니다.",
    href: "statistics/least-squares-residuals.html",
    date: "2026-09-21"
  },
  {
    subject: "statistics",
    label: "인터랙티브 실습",
    title: "t 분포와 자유도",
    description: "자유도가 2, 8, 16, 32로 커질 때 t 분포가 표준정규분포에 가까워지는 모습을 겹쳐 확인합니다.",
    href: "statistics/t-distribution-degrees-of-freedom.html",
    date: "2026-09-21"
  },
  {
    subject: "ai",
    label: "인공지능 작동이해",
    title: "LLM은 무엇을 배우고, 배운 것을 어떻게 쓰나",
    description: "대규모 언어 모델이 사전학습부터 배포까지 무엇을 배우고, 그 배운 것을 답으로 어떻게 만들어 내는지 단계별 체험과 예시로 확인합니다.",
    href: "ai/llm-what-it-learns.html",
    date: "2026-09-25"
  },
  {
    subject: "ai",
    label: "인공지능 작동이해",
    title: "코딩 에이전트는 어떻게 일하나",
    description: "코딩 에이전트 안의 LLM이 도구 호출과 반복 실행을 통해 실제 작업을 해내는 구조를 단계별 체험과 예시로 확인합니다.",
    href: "ai/coding-agent-how-it-works.html",
    date: "2026-09-26"
  },
  {
    subject: "ai",
    label: "MNIST 예제",
    title: "흉부 X선 28×28로 배우는 딥러닝",
    description: "28×28 흉부 X선(PneumoniaMNIST)으로 데이터, 전처리, 모델, 손실, 학습, 평가까지 딥러닝의 전 과정을 단계별로 체험합니다.",
    href: "ai/pneumoniamnist-deep-learning.html",
    date: "2026-09-26"
  },
  {
    subject: "statistics",
    label: "인터랙티브 실습",
    title: "지리학과 졸업생의 평균 연봉이 가장 높았다!",
    description: "평균 연봉 1위 이야기를 실제 정부 통계에 조던을 넣어 다시 계산하며, 평균을 읽을 때 먼저 물어볼 것을 확인합니다.",
    href: "statistics/geography-graduate-salary-outlier.html",
    date: "2026-09-26"
  }
];
