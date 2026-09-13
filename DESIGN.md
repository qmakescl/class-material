# 디자인 가이드

`docs/`(GitHub Pages 사이트)의 시각 디자인 원칙과 컴포넌트 패턴을 정리한
문서다. 사이트에 새 섹션·과목·컴포넌트를 추가할 때 이 가이드를 따른다.

## 디자인 목표

- **경쾌함**: 차분한 세리프/저채도 톤이 아니라, 흰색 계열 배경 위에 채도
  높은 과목별 색으로 생동감을 준다.
- **프로젝터 가시성**: 옅은 회색 텍스트를 지양하고 진한 남색 잉크
  (`--ink: #0b1220`)와 굵은 산세리프를 기본으로 쓴다. 연한 파스텔 위 저대비
  텍스트를 만들지 않는다.
- **탐색 용이성**: 단일 페이지 + 앵커 내비게이션. 스크롤 위치에 따라 현재
  섹션이 내비게이션에서 강조되고(scroll-spy), 모바일에서는 햄버거 메뉴로
  접힌다.

## 색상 시스템 (`docs/assets/styles.css`의 `:root`)

| 용도 | 변수 | 값 |
| --- | --- | --- |
| 기본 텍스트 | `--ink` | `#0b1220` |
| 보조 텍스트 | `--muted` | `#45506b` |
| 페이지 배경 | `--paper` | `#f4f6fb` |
| 카드/서피스 | `--surface` | `#ffffff` |
| 구분선 | `--line` | `#dbe1ee` |
| 브랜드 강조 | `--brand` / `--brand-dark` | `#2f5bff` / `#1c3fd6` |
| 어두운 섹션 배경 | `--navy` | `#0b1220` |
| 어두운 섹션 강조 | `--amber` | `#ffb020` |

과목(subject)마다 고유 색 + 옅은 tint 배경을 갖는다. 새 과목을 추가하면 이
표에 맞춰 색을 하나 더 정의한다.

| 과목 | 강조색 변수 | tint 변수 |
| --- | --- | --- |
| 통계 | `--statistics` `#2f6fed` | `--statistics-tint` |
| 데이터과학 | `--data-science` `#0ea968` | `--data-science-tint` |
| 인공지능 | `--ai` `#8b3ff0` | `--ai-tint` |
| 일반적인것들 | `--common` `#e2662a` | `--common-tint` |
| 이것저것 | `--life` `#e0367a` | `--life-tint` |

과목 색은 다음 요소에 일관되게 적용된다: 내비게이션 `.dot-{subject}`, 히어로
`.pill-{subject}`, 섹션 배경 `.subject[data-subject="{subject}"]`, 섹션
`.eyebrow` 색, 카드 좌측 보더(`.material-card` `border-left-color`), 빈
상태 박스(`.section-empty`) 색.

## 타이포그래피

- 폰트: Pretendard → Noto Sans KR → Inter → system-ui (세리프 사용 안 함,
  거리를 두고 보는 프로젝터 화면에서 산세리프가 더 잘 읽힘).
- 제목은 항상 `font-weight: 800`, `letter-spacing: -0.03em` 근처로 굵고
  타이트하게.
- `h1`은 `clamp(2.8rem, 7vw, 6rem)`처럼 뷰포트에 비례해 큼직하게 유지한다.

## Open Graph 미리보기 이미지

공유 링크의 Open Graph/Twitter 미리보기에는 과목별 512×512 PNG 아이콘을
사용한다. 아이콘은 `docs/assets/images/`에 보관한다.

| 콘텐츠 | 이미지 | `og:image:alt` |
| --- | --- | --- |
| 사이트 홈 및 통계 | `stat.png` | 통계 수업 자료 아이콘 |
| 데이터과학 | `data.png` | 데이터과학 수업 자료 아이콘 |
| 인공지능 | `ai.png` | 인공지능 수업 자료 아이콘 |

- 각 HTML 문서의 `<head>`에 `og:title`, `og:description`, `og:url`,
  `og:image`, `og:image:type`, `og:image:width`, `og:image:height`,
  `og:image:alt`를 함께 선언한다.
- Twitter/X 미리보기에도 같은 이미지를 사용하도록 `twitter:card`와
  `twitter:image` 계열 메타데이터를 함께 선언한다.
- `og:image`와 `og:url`은 크롤러가 접근할 수 있는 완전한 HTTPS URL을
  사용한다. 이 저장소의 기본 주소는
  `https://qmakescl.github.io/class-material/`이다.
- 프로젝트 하위 경로(`/class-material/`)를 포함해야 하므로 루트 상대 경로를
  사용하지 않는다. 커스텀 도메인을 추가하면 모든 절대 URL을 함께 갱신한다.
- 새 과목 페이지를 만들 때는 해당 과목 아이콘을 매핑하고 `og:image:alt`를
  과목명에 맞게 작성한다. 홈페이지는 사이트를 대표하는 `stat.png`를
  기본 이미지로 사용한다.
- 아이콘은 정사각형 원본을 유지한다. 미리보기 서비스가 자르거나 축소할 수
  있으므로 중요한 시각 정보는 가장자리에 배치하지 않는다.

## 내비게이션 패턴

- `.site-header`는 `position: sticky; top: 0;`로 항상 보이게 한다.
- 각 섹션은 `id`를 갖고, 내비게이션 링크는 `data-nav-link` 속성과
  `href="#섹션id"`로 연결한다.
- `docs/assets/nav.js`가 `IntersectionObserver`로 현재 보이는 섹션의 링크에
  `.is-active`를 부여한다. 섹션을 추가/삭제해도 이 스크립트는 그대로
  동작한다(선택자가 `[data-nav-link]` 기반이라 자동 인식).
- 860px 이하에서는 `.nav-toggle` 햄버거 버튼이 나타나고 `nav`가
  `.is-open` 클래스로 펼쳐진다.
- 우측 하단 `.to-top` 버튼은 스크롤 480px 이상일 때만 보인다.

## 콘텐츠가 아직 없는 섹션(빈 상태) 패턴

과목 섹션에 실을 실제 자료가 아직 없을 때는 카드 템플릿을 지우지 않고
`hidden` 속성으로 숨긴 뒤, 같은 자리에 `.section-empty` 안내 문단
("채우는 중입니다")을 보여준다.

```html
<!-- 실제 자료가 준비되면 아래 card-grid에서 hidden 속성을 지우고,
     다음 줄의 section-empty 문단을 삭제하세요. -->
<div class="card-grid" hidden>
  <article class="material-card">...</article>
  ...
</div>
<p class="section-empty">채우는 중입니다</p>
```

자료가 실제로 채워지면 `hidden` 속성을 지우고 `.section-empty` 문단을
삭제한다. `.section-empty`는 과목별 강조색으로 테두리/텍스트 색이 자동
지정된다(`.subject[data-subject="..."] .section-empty` 규칙).

## 실제 자료 페이지 연결 (링크형 카드)

실제 자료(인터랙티브 실습 HTML 등)는 `docs/{subject}/`(예:
`docs/statistics/`) 아래에 두고, `docs/index.html`의 해당 과목 카드를
`<article>` 대신 `<a class="material-card" href="...">`로 바꿔 연결한다.
카드 전체가 클릭 영역이 되며, `.card-status`는 자동으로 과목 강조색
배경의 흰 글씨 칩으로 바뀐다("준비 중" 대신 "바로가기 →" 같은 문구 사용).

```html
<a class="material-card" href="./statistics/grad-probability-lab.html">
  <span class="card-number">01</span>
  <div>
    <p class="card-label">인터랙티브 실습</p>
    <h3>제목</h3>
    <p>한 줄 설명</p>
  </div>
  <span class="card-status">바로가기 →</span>
</a>
```

자료 페이지 자체가 별도 디자인 시스템(자체 `<style>`)을 갖고 있다면,
최소한 다음 두 가지는 이 가이드에 맞춘다.

- **색상**: 본문 팔레트를 이 문서의 색상 변수 값으로 맞추고, 어두운
  네비게이션/사이드바가 있다면 `--navy`(`#0b1220`) + `--amber`
  (`#ffb020`) 조합으로(= 이 사이트의 `.guide` 섹션과 동일한 배색) 통일한다.
  해당 자료의 과목 강조색(예: 통계 `#2f6fed`)이 있다면 그 안에서도
  주요 강조색으로 재사용한다.
- **타이포그래피**: 세리프 대신 `Pretendard, "Noto Sans KR", Inter,
  system-ui, sans-serif`로 통일하고(프로젝터 가독성), 외부 웹폰트
  로딩(Google Fonts 등)은 제거한다.
- **돌아가기 링크**: 상단(또는 사이드바)에 `docs/index.html`의 해당 과목
  섹션으로 돌아가는 링크(`../index.html#statistics`)를 넣는다. 사이드바
  폭이 좁아 한 줄로 잘리기 쉬우므로 문구는 "처음으로"처럼 짧게 쓴다.

**CSS 특이도 주의**: AI로 생성한 자료 페이지는 보통 `.rail a`처럼 넓게
잡힌 자체 선택자(클래스+태그, 특이도 `(0,1,1)`)를 이미 갖고 있다. 새로
추가하는 버튼/링크에 클래스 하나만 주면(`(0,1,0)`) 그 넓은 선택자한테
그리드 레이아웃 등을 그대로 뺏겨 텍스트가 좁은 칸에 눌려 줄바꿈되는
문제가 생길 수 있다(`grad-probability-lab.html`의 "처음으로" 링크에서
실제로 발생). 새 요소는 `.rail .rail-back`처럼 부모 클래스를 포함해
특이도를 그 선택자보다 높여서 확실히 이기게 하고, `white-space: nowrap`도
같이 준다. `!important`는 쓰지 않는다.

## 새 과목(섹션) 추가 체크리스트

1. `docs/assets/styles.css`의 `:root`에 `--{subject}` / `--{subject}-tint`
   색상 변수 추가.
2. `.dot-{subject}`, `.pill-{subject}` 규칙 추가.
3. `.subject[data-subject="{subject}"]` 배경/`.eyebrow`/`.material-card`
   보더/`.section-empty` 규칙 추가.
4. `docs/index.html`의 `nav`와 히어로 `.hero-actions`에 링크 추가.
5. 새 `<section class="subject" id="{subject}" data-subject="{subject}">`를
   만들고, 위의 "빈 상태 패턴"대로 `card-grid`(hidden) + `section-empty`
   문단을 넣는다.

## 푸터 패턴

`docs/index.html`의 `<footer>`는 세 블록으로 구성된다.

1. `.footer-main` — 사이트/자료실 이름과 한 줄 설명 (좌우 정렬, 모바일에서
   세로로 쌓임).
2. `.footer-credit` — 제작 크레딧 한 줄.
3. `.footer-contact` — Email·GitHub·Instagram·Facebook 등 연락처 목록.
   `<li>`마다 대문자 라벨(`<span>`, 필요 시 `text-transform: uppercase`)과
   링크로 구성하고, 외부 링크는 `target="_blank" rel="noopener noreferrer"`를
   붙인다. 860px 이하에서는 세로로 쌓인다.

연락처나 크레딧 문구를 바꿀 때는 이 구조(라벨 + 링크)를 유지한다.

## 실제로 반영된 예시

- **통계 → 확률에 대하여**(`docs/statistics/grad-probability-lab.html`):
  "실제 자료 페이지 연결" 패턴을 실제로 적용한 첫 사례. 원래 세리프 +
  세이지그린 팔레트였던 외부 생성 HTML을 이 가이드의 색상·폰트로
  리틴트하고, 사이드바를 `--navy`+`--amber` 조합으로 맞춘 뒤
  `docs/index.html`의 통계 카드에서 링크로 연결했다. 다른 과목의 실습
  자료를 붙일 때 참고할 기준 사례로 삼는다.

## 접근성 · 축소 모션

- `.skip-link`로 본문 바로가기 제공.
- `@media (prefers-reduced-motion: reduce)`에서 `scroll-behavior: auto`,
  pill hover 이동 효과 제거.
