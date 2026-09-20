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

## 자료 목록: 홈(최근 3개)과 과목별 목록 페이지

카드는 HTML에 직접 쓰지 않고 **`docs/assets/materials.js`** 한 곳의 목록에서
`docs/assets/cards.js`가 그린다. 새 자료를 발행하면 `materials.js`의
`window.MATERIALS` 배열 끝에 한 항목만 추가한다.

```js
{
  subject: "statistics",            // statistics | data-science | ai | common | life
  label: "인터랙티브 실습",
  title: "제목",
  description: "한 줄 설명",
  href: "statistics/파일명.html",     // docs/ 기준 상대 경로
  date: "2026-09-21"                // 같은 날짜면 배열에서 뒤쪽이 더 최신
}
```

- 항상 **최신순**으로 보여 준다. 카드 번호는 발행 순서(가장 오래된 것이 01)다.
- **홈** `docs/index.html`: 과목 섹션마다 `data-limit="3"` 컨테이너로 최근
  3개만 보여 주고, 아래 "○○ 자료 전체 보기 →" 링크가 목록 페이지로 연결된다.
- **과목별 목록 페이지** `docs/{subject}/index.html`(`statistics/`,
  `data-science/`, `ai/`, `common/`, `life/`): 해당 과목 전체를 최신순으로
  보여 주며, `.card-grid-3`로 **한 행에 카드 3개**(1000px 이하 2개, 640px
  이하 1개)를 세로형 카드로 배치한다. 헤더 내비게이션은 각 목록 페이지로
  연결되고 현재 과목에 `.is-active`가 붙는다.
- 자료가 없는 과목은 grid를 `hidden`으로 두고 `.section-empty`("채우는
  중입니다") 문단을 보여 준다. 자료가 생기면 `cards.js`가 grid를 보이고
  안내 문단을 지운다. HTML을 고칠 필요는 없다.
- 목록 페이지의 컨테이너는 `data-base="../"`로 docs 루트까지의 상대 경로를
  준다. 새 과목을 추가하면 `docs/{subject}/index.html`도 같은 형태로 만든다.

## 실제 자료 페이지 연결

실제 자료(인터랙티브 실습 HTML 등)는 `docs/{subject}/`(예:
`docs/statistics/`) 아래에 두고 `materials.js`에 항목을 추가해 연결한다.
카드는 `<a class="material-card">`로 그려지며 카드 전체가 클릭 영역이고,
`.card-status`는 과목 강조색 배경의 흰 글씨 칩("바로가기 →")이 된다.

자료 페이지 자체가 별도 디자인 시스템(자체 `<style>`)을 갖고 있다면,
다음 기본 레이아웃과 스타일을 따른다.

### 자료 페이지 기본 레이아웃: 좌측 레일

새 인터랙티브 수업 자료는 `docs/statistics/grad-probability-lab.html` 및
`docs/statistics/point-estimation-confidence-interval.html`처럼 **좌측 고정
레일 + 본문** 구조를 기본으로 사용한다. 레일은 자료의 제목과 목차를 계속
보이게 해 긴 실습에서 현재 위치와 다른 주제를 빠르게 오갈 수 있게 한다.

```html
<aside class="rail">
  <a class="rail-back" href="../index.html#statistics">← 처음으로</a>
  <h1>자료 제목</h1>
  <nav id="rail-nav" aria-label="자료 목차">
    <a href="#section-1"><b>01</b><span>첫 번째 주제</span></a>
  </nav>
  <footer>자료 사용 안내</footer>
</aside>
<main>...</main>
```

- 데스크톱에서는 레일을 화면 왼쪽에 고정하고, 본문에는 레일 너비만큼의
  왼쪽 여백을 둔다.
- 레일의 배경은 `--navy`(`#0b1220`), 현재 목차의 테두리와 강조는
  `--amber`(`#ffb020`)를 사용한다. 본문 안의 주요 인터랙션에는 해당 과목의
  강조색을 사용한다.
- 목차는 `IntersectionObserver`로 현재 읽는 섹션에 `.on`을 적용한다.
- 860px 이하에서는 레일을 상단 영역으로 바꾸고, 목차는 가로 스크롤이 가능한
  한 줄로 전환한다. 이때 레일 푸터는 숨긴다.
- 한 화면 안에 끝나는 아주 짧은 자료처럼 레일이 탐색에 도움이 되지 않는 경우만
  예외로 하며, 예외 여부는 구현 시 명시한다.

- **색상**: 본문 팔레트를 이 문서의 색상 변수 값으로 맞추고, 어두운
  레일은 `--navy`(`#0b1220`) + `--amber`(`#ffb020`) 조합으로(= 이 사이트의
  `.guide` 섹션과 동일한 배색) 통일한다.
  해당 자료의 과목 강조색(예: 통계 `#2f6fed`)이 있다면 그 안에서도
  주요 강조색으로 재사용한다.
- **타이포그래피**: 세리프 대신 `Pretendard, "Noto Sans KR", Inter,
  system-ui, sans-serif`로 통일하고(프로젝터 가독성), 외부 웹폰트
  로딩(Google Fonts 등)은 제거한다.
- **돌아가기 링크**: 레일 상단에 `docs/index.html`의 해당 과목 섹션으로
  돌아가는 링크(`../index.html#statistics`)를 넣는다. 사이드바
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
   만들고 `card-grid`(`data-subject-list`, `data-limit="3"`, hidden) +
   `section-empty` + `section-more` 링크를 넣는다.
6. `docs/{subject}/index.html` 목록 페이지를 만들고 각 목록 페이지의 헤더
   내비게이션에도 링크를 추가한다.

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
