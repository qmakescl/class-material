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
| 알아두면 좋을만한 | `--things` `#e2662a` | `--things-tint` |

과목 키(`things`)와 화면에 쓰는 이름("알아두면 좋을만한 :)")은 다를 수 있다.
키는 폴더명·CSS 변수·`materials.js`의 `subject`에, 이름은 내비게이션·제목·
태그에 쓴다.
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
| 사이트 홈 및 통계 | `stat.png` | 통계 자료 아이콘 |
| 데이터과학 | `data.png` | 데이터과학 자료 아이콘 |
| 인공지능 | `ai.png` | 인공지능 자료 아이콘 |

- 각 HTML 문서의 `<head>`에 `og:title`, `og:description`, `og:url`,
  `og:image`, `og:image:type`, `og:image:width`, `og:image:height`,
  `og:image:alt`를 함께 선언한다.
- **제목·설명 문구**는 사이트 전체가 같은 톤을 쓴다. 이 자료실은 수업만이
  아니라 워크숍·이야기 모임에서도 함께 보므로 "수업 자료"로 한정하지 않는다.

  | 항목 | 값 |
  | --- | --- |
  | `<title>` / `og:title` / `twitter:title` | `자료 제목 \| Q의 아카이브` |
  | `og:site_name` | `Q의 데이터 이야기 자료` |
  | `description` | 그 자료가 무엇을 다루는지 한 문장. 끝맺음은 "…하는 통계 자료입니다."처럼 과목명 + 자료 |
  | `og:image:alt` / `twitter:image:alt` | `{과목} 자료 아이콘` |

- 페이지 안의 공통 문구도 같은 톤으로 맞춘다: 헤더 브랜드는 "Data를 주제로
  이야기하기"(`aria-label="첫페이지"`), 푸터는 "Q's Material" + "데이터를
  주제로 이야기를 나누는 자료실", 자료 페이지 머리말(`.eyebrow`)은
  "통계적 추론 · 이야기 자료"처럼 쓴다.
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
  subject: "statistics",            // statistics | data-science | ai | things | life
  label: "인터랙티브 실습",
  title: "제목",
  description: "한 줄 설명",
  href: "statistics/파일명.html",     // docs/ 기준 상대 경로
  tags: ["통계", "시뮬레이션", "주제1"],  // 과목 1 + 유형 1 + 주제 2~5 ("태그" 참고)
  date: "2026-09-21",               // 같은 날짜면 배열에서 뒤쪽이 더 최신
  practice: true                    // 선택. 직접 해 보는 실습 절이 있으면 카드에 "실습 포함" 배지
}
```

- 항상 **최신순**으로 보여 준다. 카드 번호는 발행 순서(가장 오래된 것이 01)다.
- **홈** `docs/index.html`: 과목 섹션마다 `data-limit="3"` 컨테이너로 최근
  3개만 보여 주고, 아래 "○○ 자료 전체 보기 →" 링크가 목록 페이지로 연결된다.
- **과목별 목록 페이지** `docs/{subject}/index.html`(`statistics/`,
  `data-science/`, `ai/`, `things/`, `life/`): 해당 과목 전체를 최신순으로
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

## 자료 페이지 공통 테마 (`docs/assets/material.css`)

`docs/{subject}/`의 자료 페이지(실습·해설 HTML)는 모두 **`docs/assets/material.css`**
한 파일을 공유한다. 목록/홈 페이지는 `styles.css`, 자료 페이지는
`material.css`다. 페이지마다 팔레트·본문·박스·레일을 새로 정의하지 않는다.

```html
<head>
  ...
  <link rel="stylesheet" href="../assets/katex/katex.min.css">  <!-- 수식이 있으면, material.css보다 앞 -->
  <link rel="stylesheet" href="../assets/material.css">
  <style>/* 이 자료 고유의 위젯 스타일만 */</style>
</head>
```

**`material.css`가 제공하는 것**

| 영역 | 내용 |
| --- | --- |
| 토큰 | `--paper` `--surface` `--soft` `--ink` `--muted` `--line` `--navy` `--amber` `--accent`/`--accent-soft` `--pos` `--neg` `--ok` `--warn`(각 `-soft`) `--shadow` `--sans` `--mono` `--rail` `--radius` |
| 기본 | `body`, `h1`~`h4`(산세리프 800, 자간 -0.02em), `p`, `a`, `code`/`.mono`/`.num`, `.muted`, `.note`, `.lede`, `.eyebrow`, `.katex-display` |
| 레이아웃 | `.rail`(레일·목차·모바일 전환), `main`(레일 폭만큼 왼쪽 여백, 최대 1060px), `main > section` |
| 박스 | `.panel`(기본 박스), `.panel.raised`(그림자), `.callout`(`.warn`), `.recap`, `.row`/`.col`, `.scroll` |
| 조각 | `.tag`, `.readout`(`.math`), `.metrics`, `.legend`, `.nav` |
| 입력 | `.btn`(`.ghost`), `.controls`, `input[type=range]` |
| 표·기타 | `table`/`th`/`td`/`td.n`, `details`, `pre`, `ol.refs` |

**규칙**

- **문단 `p`에는 `max-width`를 주지 않는다.** 박스(`.panel`)의 패딩 안쪽 폭을
  문단이 꽉 채우는 것이 기본이다. 가독성을 위해 줄을 좁히고 싶으면 문단이 아니라
  박스나 열 자체의 폭으로 조절한다. 글자 수 단위(`ch`/`em`) 폭 제한은 쓰지 않는다.
- 페이지 `<style>`에는 **그 자료에만 있는 위젯**(차트, 시각화, 특수 그리드)만 둔다.
  이미 `material.css`에 있는 것(본문, 제목, 박스, 레일, 표, 버튼…)을 다시
  정의하지 않는다. 색은 자체 팔레트를 만들지 말고 토큰을 쓴다. 차트 계열색처럼
  그 자료 안에서만 쓰는 값만 지역 변수로 둔다.
- 과목 강조색이 기본(통계 파랑 `#2f6fed`)과 다르면 페이지 `:root`에서
  `--accent`/`--accent-soft`만 덮어쓴다.
- 공통 이름과 충돌하는 지역 클래스를 만들지 않는다. 특히 `.row`(flex 줄),
  `.col`(`flex:1 1 260px`), `.readout`(한 줄 mono 박스), `.metrics`(수치 카드
  격자)를 공통이 이미 정의한다. 다른 뜻으로 쓰려면 `.brow`, `.kv`, `.stack`처럼
  다른 이름을 쓴다.
- 글꼴은 산세리프만 쓰고 외부 웹폰트(Google Fonts)·세리프·다크 모드/테마
  토글을 두지 않는다.
- 여러 자료에서 반복되는 규칙이 페이지 `<style>`에 생기면 그 자리에서 복사하지
  말고 `material.css`로 올린다.
- 공통 테마를 바꾸면 모든 자료 페이지에 영향을 주므로, 바꾼 뒤 자료 페이지를
  몇 개 열어 레일·박스·본문 폭을 확인한다.

자료 페이지가 위 공통 테마 위에 추가로 지켜야 할 기본 레이아웃과 스타일은
다음과 같다.

### 자료 페이지 기본 레이아웃: 좌측 레일

새 인터랙티브 수업 자료는 `docs/statistics/grad-probability-lab.html` 및
`docs/statistics/point-estimation-confidence-interval.html`처럼(모두 `material.css`의 `.rail`/`main`을 쓴다) **좌측 고정
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
- 레일 맨 아래에는 라이선스 한 줄(`.rail-license`)을 둔다. 자료는 모두
  CC BY-SA 4.0을 따르므로 다음 markup을 레일 `footer` 바로 뒤에 넣는다.

  ```html
  <p class="rail-license">이 자료는 <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.ko"
    target="_blank" rel="noopener noreferrer">CC BY-SA 4.0</a> 라이선스를 따릅니다.</p>
  ```

  10.5px / `#7c88a8`에 위쪽 구분선(`#22304f`)을 두고, 링크는 `#9fb0d0`,
  hover·focus에서 `--amber`로 바뀐다. 레일 푸터와 달리 **860px 이하에서도
  숨기지 않는다**(라이선스 고지는 모든 화면에서 보여야 한다).
- 한 화면 안에 끝나는 아주 짧은 자료처럼 레일이 탐색에 도움이 되지 않는 경우만
  예외로 하며, 예외 여부는 구현 시 명시한다.

- **색상**: 본문 팔레트는 `material.css`의 토큰을 그대로 쓰고, 어두운
  레일은 `--navy`(`#0b1220`) + `--amber`(`#ffb020`) 조합으로(= 이 사이트의
  `.guide` 섹션과 동일한 배색) 통일한다.
  해당 자료의 과목 강조색(예: 통계 `#2f6fed`)이 있다면 그 안에서도
  주요 강조색으로 재사용한다.
- **타이포그래피**: `material.css`의 `--sans`(`Pretendard, "Noto Sans KR",
  Inter, system-ui, sans-serif`)로 통일하고(프로젝터 가독성), 외부 웹폰트
  로딩(Google Fonts 등)은 두지 않는다.
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

## 태그

자료를 주제로 찾을 수 있도록 모든 배포 문서는 태그를 갖는다. 태그는 **자료를
만들 때 LLM이 먼저 정하고**(본문을 쓰기 전에 정한다), 두 곳에 같은 값을 넣는다.

1. 자료 페이지 좌측 레일의 `.rail-tags` (사람이 보는 표시)
2. `docs/assets/materials.js`의 `tags` 배열 (목록·검색이 읽는 데이터)

### 구성 규칙

한 자료의 태그는 **과목 1개 + 유형 1개 + 주제 2~5개**(총 4~7개)로 만든다.
순서도 과목 → 유형 → 주제로 고정한다.

| 자리 | 어휘 |
| --- | --- |
| 과목 | `통계` `데이터과학` `인공지능` `알아두면좋을만한` `이것저것` (`materials.js`의 `subject`와 1:1) |
| 유형 | `개념정리` `시뮬레이션` `시각화` `사례분석` 중 하나 |
| 주제 | 그 자료의 핵심 개념 (아래 표기 규칙) |

- 표시는 `#태그명`, 저장은 `#` 없이 태그명만 쓴다.
- 한 태그는 공백 없이 붙여 쓴다(`조건부확률`, `최소제곱`). 한글을 기본으로 하고,
  통용되는 약어·기호만 그대로 쓴다(`LLM`, `p값`, `t분포`, `R²`는 `결정계수`로).
- 새 주제 태그를 만들기 전에 아래 목록에 이미 있는 태그를 먼저 찾아 재사용한다.
  비슷한 말(`가설검정`/`가설 검정`, `표본오차`/`표준오차`)을 새로 만들지 않는다.

### 마크업과 스타일

레일 목차(`nav`) 바로 아래, 레일 푸터 위에 둔다.

```html
<nav id="rail-nav" aria-label="자료 목차">...</nav>
<div class="rail-tags" aria-label="태그">
  <span class="rail-tag">#통계</span>
  <span class="rail-tag">#시뮬레이션</span>
</div>
<footer>...</footer>
```

- `.rail-tags` / `.rail-tag`는 `docs/assets/material.css`에 정의한다. 페이지
  `<style>`에서 다시 정의하지 않는다.
- pill badge: `border-radius: 999px`, 배경 `#16213d`, 테두리 `#2b3a5e`, 글자
  `#9fb0d0`, `font-size: 11px` / `font-weight: 600` — 어두운 레일 위에서 목차
  (13.5px)보다 작고 한 단계 약한 대비로 둔다. 목차와 구분되도록 위쪽에
  `border-top: 1px solid #22304f`로 얇은 구분선을 둔다.
- 크기·색을 `font` 단축 속성으로 쓰지 않는다. `font: 600 11px var(--sans)`처럼
  쓰면 일부 브라우저에서 `var()` 때문에 선언 전체가 무시되어 태그가 본문 크기의
  맨 텍스트로 보일 수 있다. 각 속성을 따로 쓴다.
- 태그는 현재 링크가 아닌 표시 전용이다. 태그로 거르는 화면을 붙일 때는
  `.rail-tag`를 `<a>`로 바꾸고 `materials.js`의 `tags`를 기준으로 필터링한다.
- 860px 이하(레일이 상단으로 바뀌는 폭)에서도 태그는 그대로 보인다. 레일
  푸터만 숨긴다.

### 현재 태그

| 자료 | 태그 |
| --- | --- |
| 확률에 대하여 | 통계 · 시뮬레이션 · 확률 · 조건부확률 · 베이즈정리 · 확률분포 |
| 점추정과 신뢰구간 | 통계 · 시뮬레이션 · 점추정 · 신뢰구간 · 표본오차 |
| 통계적 가설검정 | 통계 · 시뮬레이션 · 가설검정 · 유의수준 · 검정력 · p값 · 효과크기 |
| 회귀분석 조금 깊이 보기 | 통계 · 시각화 · 회귀분석 · 최소제곱 · 잔차 · 결정계수 |
| t 분포와 자유도 | 통계 · 시각화 · t분포 · 자유도 · 표본분포 |
| LLM은 무엇을 배우나 | 인공지능 · 개념정리 · LLM · 사전학습 · 파라미터 · 토큰 |
| 코딩 에이전트는 어떻게 일하나 | 인공지능 · 개념정리 · 코딩에이전트 · LLM · 도구호출 · 컨텍스트창 |
| 흉부 X선 28×28로 배우는 딥러닝 | 인공지능 · 시각화 · 딥러닝 · 이미지분류 · 손실함수 · 모델평가 |
| 회귀에서 딥러닝으로 | 인공지능 · 시뮬레이션 · 딥러닝 · 회귀분석 · 경사하강법 · 손실함수 · 신경망 |
| 지리학과 졸업생의 평균 연봉 | 데이터과학 · 사례분석 · 평균 · 이상치 · 통계해석 |
| 데이터로 세상을 읽을 때 조심할 것들 | 데이터과학 · 개념정리 · 통계해석 · 표본오차 · 평균으로의회귀 · 심슨의역설 · 선택편향 |

## 수식 표기 (KaTeX)

수식은 HTML/CSS로 흉내 내지 않고 **KaTeX**로 표기한다. KaTeX는 CDN이 아니라
`docs/assets/katex/`에 포함되어 있고(폰트는 woff2만), 오프라인·GitHub Pages
하위 경로에서도 동작한다.

- 자료 페이지 `<head>`에 다음을 넣는다(경로는 페이지 위치에 맞춰 상대 경로로).

  ```html
  <link rel="stylesheet" href="../assets/katex/katex.min.css">   <!-- 페이지 <style>보다 앞 -->
  <script defer src="../assets/katex/katex.min.js"></script>
  <script defer src="../assets/katex/contrib/auto-render.min.js"></script>
  <script defer src="../assets/math.js"></script>
  ```

- 인라인 수식은 `\( ... \)`, 블록 수식은 `\[ ... \]`로 쓴다. 예:
  `\(\hat{\beta}_1 = \dfrac{S_{xy}}{S_{xx}}\)`. 한글은 `\text{...}`로 감싼다.
- `docs/assets/math.js`가 페이지 로드 시 전체를 렌더링하고, JS가 나중에
  `innerHTML`/`textContent`로 넣는 문자열도 자동으로 다시 렌더링한다. JS 문자열
  안에서는 백슬래시를 두 번 쓴다(`'\\(x^{2}\\)'`).
- **SVG `<text>`와 canvas 글자에는 수식 구분자를 쓰지 않는다.** 축 라벨 등은
  유니코드 글자(`β₁`, `x̄`)를 그대로 쓴다.
- `.katex`는 `text-transform: none`이므로 대문자 변환(`uppercase`)되는 라벨
  안에서도 수식이 깨지지 않는다.
- KaTeX 버전을 올리려면 `npm pack katex@<버전>`의 `dist/`에서
  `katex.min.js`, `contrib/auto-render.min.js`, `fonts/*.woff2`를 교체하고
  `katex.min.css`에서 woff/ttf `src`를 제거한다(woff2만 사용).

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
