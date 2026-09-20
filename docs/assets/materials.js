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
  }
];
