# 편집 파일 (edits/)

배포된 자료 쪽에서 고칠 곳을 모아 두는 폴더다. 로컬 편집 서버(`src/python/edit_server.py`)가 만들고,
Publish할 때 고친 HTML과 함께 커밋되어 기록으로 남는다. GitHub Pages에는 배포되지 않는다(`docs/` 밖).

## 쓰는 법

```sh
uv run python src/python/edit_server.py      # http://127.0.0.1:8001
```

1. 브라우저에서 `http://127.0.0.1:8001/statistics/anova-with-r.html`처럼 고칠 쪽을 연다.
2. 왼쪽 아래 **편집**을 눌러 편집 모드를 켜고, 고칠 글을 드래그한 뒤 바꿀 글을 적고 저장한다.
3. **검사**로 항목마다 원문에서 찾았는지 확인하고, **편집본 보기**로 고친 쪽을 미리 본다.
4. **Publish**를 두 번 누르면 그 쪽만 반영되어 `main`에 커밋·푸시된다.

Publish는 그 쪽의 HTML에 커밋하지 않은 다른 변경이 있으면 멈춘다. 먼저 커밋하거나 되돌린 뒤 다시 한다.
푸시 없이 커밋만 하려면 `--no-push`를 붙여 서버를 연다.

## 파일 구조

`docs/` 기준 경로를 따라 쪽마다 JSON 파일 하나를 둔다.

```text
edits/
└── statistics/
    └── anova-with-r.json      ← docs/statistics/anova-with-r.html 의 편집 파일
```

```json
{
  "page": "statistics/anova-with-r.html",
  "items": [
    {
      "id": "3f9c1a2b7d",
      "created": "2026-11-09T14:00:00+09:00",
      "mode": "text",
      "find": "원래 글",
      "replace": "바꿀 글",
      "before": "고른 글 앞의 문맥",
      "after": "고른 글 뒤의 문맥",
      "note": "메모",
      "status": "published",
      "published_at": "2026-11-09T14:10:00+09:00"
    }
  ],
  "history": [{ "at": "2026-11-09T14:10:00+09:00", "applied": 1, "left": 0 }]
}
```

- `mode`가 `text`이면 화면에 보이는 글에서 찾는다. 같은 글이 여러 번 나오면 `before`, `after` 문맥으로 고르고,
  그래도 정해지지 않으면 `occurrence`(몇 번째)를 적는다. 찾은 자리가 태그를 걸치면 반영하지 않는다.
- `mode`가 `source`이면 HTML 원문에서 글자 그대로 찾고, 바꿀 글도 HTML 그대로 넣는다. 수식, 스크립트가 그리는 글,
  태그를 걸친 곳을 고칠 때 쓴다.
- `status`는 `pending`(대기)과 `published`(반영됨)이다. 반영된 항목은 지우지 않고 기록으로 남는다.
