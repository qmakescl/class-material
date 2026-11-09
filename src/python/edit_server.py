"""자료 쪽을 브라우저에서 보며 고칠 곳을 모으고, 쪽마다 반영해 main 에 올리는 로컬 편집 서버.

실행 (저장소 맨 위에서):
    uv run python src/python/edit_server.py            # http://127.0.0.1:8001
    uv run python src/python/edit_server.py --port 8002

동작
- docs/ 의 쪽을 그대로 보여 주되, HTML 을 내보낼 때만 편집 도구(src/editor/)를 끼워 넣는다.
  docs/ 의 파일은 Publish 하기 전까지 바뀌지 않는다.
- 고칠 곳은 쪽마다 edits/<docs 기준 경로>.json 에 모인다.
  예: docs/statistics/anova-with-r.html -> edits/statistics/anova-with-r.json
- Publish 는 한 쪽씩 한다. 대기 중인 항목을 그 쪽의 HTML 에 반영하고,
  그 HTML 과 편집 파일 두 개만 main 에 커밋한 뒤 origin 으로 푸시한다.
- 이 컴퓨터의 git 설정과 인증을 그대로 쓴다. 127.0.0.1 에만 열린다.

항목의 찾는 방식
- text: 화면에 보이는 글(태그를 걷어 내고 엔터티를 푼 글)에서 찾는다. 공백은 한 칸으로 보고,
  같은 글이 여러 번 나오면 저장해 둔 앞뒤 문맥으로 고른다. 찾은 자리가 태그를 걸치면 반영하지 않는다.
- source: HTML 원문에서 글자 그대로 찾는다. 수식, 스크립트가 그리는 글, 태그를 걸친 곳을 고칠 때 쓴다.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

REPO_ROOT = Path(__file__).resolve().parents[2]
EDITOR_ASSETS = REPO_ROOT / "src" / "editor"
API_HEADER = "X-CME"  # 다른 사이트에서 보내는 요청을 막기 위한 머리글

_ENTITY = re.compile(r"&(#\d+|#x[0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);")
_RAW_TEXT_TAGS = ("script", "style", "noscript", "template")


# ---------------------------------------------------------------- 글자 지도 --

def text_map(src: str) -> tuple[str, list[tuple[int, int]]]:
    """HTML 원문에서 화면에 보이는 글을 뽑고, 글자마다 원문의 [시작, 끝) 위치를 함께 돌려준다.

    태그와 주석, script·style 의 내용은 건너뛰고 엔터티는 푼다.
    공백 묶음은 한 칸으로 줄여, 화면에서 고른 글과 비교하기 쉽게 한다.
    """
    chars: list[str] = []
    spans: list[tuple[int, int]] = []
    i, n = 0, len(src)
    lower = src.lower()
    while i < n:
        c = src[i]
        if c == "<":
            if src.startswith("<!--", i):
                j = src.find("-->", i + 4)
                i = n if j < 0 else j + 3
                continue
            j = src.find(">", i + 1)
            if j < 0:
                break
            tag = re.match(r"<\s*([A-Za-z0-9]+)", src[i : j + 1])
            i = j + 1
            if tag and tag.group(1).lower() in _RAW_TEXT_TAGS:
                end = lower.find("</" + tag.group(1).lower(), i)
                i = n if end < 0 else end
            continue
        if c == "&":
            m = _ENTITY.match(src, i)
            if m:
                ch = html.unescape(m.group(0))
                for x in ch:
                    chars.append(x)
                    spans.append((i, m.end()))
                i = m.end()
                continue
        chars.append(c)
        spans.append((i, i + 1))
        i += 1
    # 공백 묶음을 한 칸으로
    out: list[str] = []
    out_spans: list[tuple[int, int]] = []
    for ch, sp in zip(chars, spans):
        if ch.isspace():
            if out and out[-1] == " ":
                out_spans[-1] = (out_spans[-1][0], sp[1])
                continue
            out.append(" ")
            out_spans.append(sp)
        else:
            out.append(ch)
            out_spans.append(sp)
    return "".join(out), out_spans


def norm(s: str) -> str:
    """공백 묶음을 한 칸으로 줄이고 앞뒤 공백을 지운다."""
    return re.sub(r"\s+", " ", s or "").strip()


def _common_suffix(a: str, b: str) -> int:
    k = 0
    while k < len(a) and k < len(b) and a[-1 - k] == b[-1 - k]:
        k += 1
    return k


def _common_prefix(a: str, b: str) -> int:
    k = 0
    while k < len(a) and k < len(b) and a[k] == b[k]:
        k += 1
    return k


def locate(src: str, item: dict, cache: dict | None = None) -> dict:
    """항목이 원문의 어디를 가리키는지 찾는다.

    돌려주는 값: {"status": ok|notfound|ambiguous|tags|empty, "start", "end", "count"}
    """
    find = item.get("find") or ""
    if not find.strip():
        return {"status": "empty", "count": 0}
    if item.get("mode") == "source":
        hits = [m.start() for m in re.finditer(re.escape(find), src)]
        if not hits:
            return {"status": "notfound", "count": 0}
        k = item.get("occurrence")
        if len(hits) > 1 and not (isinstance(k, int) and 1 <= k <= len(hits)):
            return {"status": "ambiguous", "count": len(hits)}
        s = hits[(k - 1) if len(hits) > 1 else 0]
        return {"status": "ok", "start": s, "end": s + len(find), "count": len(hits)}

    if cache is not None and "map" in cache:
        text, spans = cache["map"]
    else:
        text, spans = text_map(src)
        if cache is not None:
            cache["map"] = (text, spans)
    target = norm(find)
    hits = [m.start() for m in re.finditer(re.escape(target), text)]
    if not hits:
        return {"status": "notfound", "count": 0}
    pick = hits[0]
    if len(hits) > 1:
        k = item.get("occurrence")
        if isinstance(k, int) and 1 <= k <= len(hits):
            pick = hits[k - 1]
        else:
            before, after = norm(item.get("before")), norm(item.get("after"))
            def squash(t: str) -> str:  # 공백과 문장부호를 빼고 비교해 작은 차이에 견디게 한다
                return re.sub(r"[\s.,;:!?·'\"()\[\]]+", "", t)
            b, a = squash(before), squash(after)
            scored = []
            for h in hits:
                sc = _common_suffix(squash(text[max(0, h - 120) : h]), b)
                sc += _common_prefix(squash(text[h + len(target) : h + len(target) + 120]), a)
                scored.append((sc, h))
            scored.sort(reverse=True)
            if scored[0][0] == 0 or scored[0][0] == scored[1][0]:
                return {"status": "ambiguous", "count": len(hits)}
            pick = scored[0][1]
    s = spans[pick][0]
    e = spans[pick + len(target) - 1][1]
    if "<" in src[s:e]:
        return {"status": "tags", "start": s, "end": e, "count": len(hits)}
    return {"status": "ok", "start": s, "end": e, "count": len(hits)}


def replacement_of(item: dict) -> str:
    """원문에 넣을 글. text 방식은 HTML 특수문자를 엔터티로 바꾸고, source 방식은 그대로 넣는다."""
    rep = item.get("replace") or ""
    if item.get("mode") == "source":
        return rep
    return rep.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def check_items(src: str, items: list[dict]) -> list[dict]:
    """대기 중인 항목마다 찾은 결과와 바뀌는 부분의 앞뒤를 돌려준다. 서로 겹치는 항목은 뒤의 것을 막는다."""
    cache: dict = {}
    results: list[dict] = []
    taken: list[tuple[int, int]] = []
    for it in items:
        if it.get("status") == "published":
            continue
        r = locate(src, it, cache)
        r["id"] = it.get("id")
        if r["status"] == "ok":
            s, e = r["start"], r["end"]
            if any(not (e <= a or b <= s) for a, b in taken):
                r["status"] = "overlap"
            else:
                taken.append((s, e))
                line = src.count("\n", 0, s) + 1
                pre, post = src[max(0, s - 60) : s], src[e : e + 60]
                r.update(line=line, old=pre + "⟦" + src[s:e] + "⟧" + post,
                         new=pre + "⟦" + replacement_of(it) + "⟧" + post)
        results.append(r)
    return results


def apply_items(src: str, items: list[dict]) -> tuple[str, list[dict]]:
    """반영할 수 있는 항목을 원문에 적용한 결과와 항목별 검사 결과를 돌려준다."""
    results = check_items(src, items)
    by_id = {it.get("id"): it for it in items}
    oks = sorted((r for r in results if r["status"] == "ok"), key=lambda r: r["start"], reverse=True)
    for r in oks:
        src = src[: r["start"]] + replacement_of(by_id[r["id"]]) + src[r["end"] :]
    return src, results


# ------------------------------------------------------------- 파일과 git --

class Workspace:
    """docs/ 와 edits/ 의 위치, 편집 파일 읽기·쓰기, git 실행을 맡는다."""

    def __init__(self, root: Path, push: bool = True) -> None:
        self.root = root.resolve()
        self.docs = self.root / "docs"
        self.edits = self.root / "edits"
        self.push = push

    def page_path(self, page: str) -> Path:
        """docs 기준 경로를 검사해 실제 파일 경로로 바꾼다. docs 밖이나 HTML 이 아니면 오류."""
        page = unquote(page or "").lstrip("/")
        p = (self.docs / page).resolve()
        if not str(p).startswith(str(self.docs) + "/") or p.suffix != ".html" or not p.is_file():
            raise ValueError(f"자료 쪽이 아니다: {page}")
        return p

    def rel(self, p: Path) -> str:
        return p.relative_to(self.docs).as_posix()

    def edits_path(self, page_file: Path) -> Path:
        return (self.edits / self.rel(page_file)).with_suffix(".json")

    def load(self, page_file: Path) -> dict:
        ep = self.edits_path(page_file)
        if ep.is_file():
            return json.loads(ep.read_text(encoding="utf-8"))
        return {"page": self.rel(page_file), "items": [], "history": []}

    def save(self, page_file: Path, data: dict) -> None:
        ep = self.edits_path(page_file)
        ep.parent.mkdir(parents=True, exist_ok=True)
        data["page"] = self.rel(page_file)
        data.setdefault("history", [])
        ep.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True)

    def publish(self, page_file: Path) -> dict:
        """한 쪽의 대기 항목을 반영하고 그 쪽의 HTML 과 편집 파일만 main 에 커밋·푸시한다."""
        branch = self.git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        if branch != "main":
            return {"ok": False, "message": f"지금 브랜치가 main 이 아니다({branch}). main 으로 바꾼 뒤 다시 한다."}
        rel_html = page_file.relative_to(self.root).as_posix()
        dirty = self.git("status", "--porcelain", "--", rel_html).stdout.strip()
        if dirty:
            return {"ok": False, "message": f"{rel_html} 에 커밋하지 않은 다른 변경이 있다. 먼저 커밋하거나 되돌린 뒤 Publish 한다."}
        data = self.load(page_file)
        src = page_file.read_text(encoding="utf-8")
        new_src, results = apply_items(src, data["items"])
        done = [r for r in results if r["status"] == "ok"]
        if not done:
            return {"ok": False, "message": "반영할 수 있는 항목이 없다.", "results": results}
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        ok_ids = {r["id"] for r in done}
        for it in data["items"]:
            if it.get("id") in ok_ids:
                it["status"] = "published"
                it["published_at"] = now
        left = sum(1 for it in data["items"] if it.get("status") != "published")
        data["history"].append({"at": now, "applied": len(done), "left": left})
        page_file.write_text(new_src, encoding="utf-8")
        self.save(page_file, data)
        rel_edits = self.edits_path(page_file).relative_to(self.root).as_posix()
        msg = f"편집 반영: {self.rel(page_file)} ({len(done)}건)"
        add = self.git("add", "--", rel_html, rel_edits)
        commit = self.git("commit", "-m", msg, "--", rel_html, rel_edits)
        if commit.returncode != 0:
            return {"ok": False, "message": "커밋하지 못했다: " + (commit.stderr or commit.stdout or add.stderr).strip(),
                    "results": results}
        sha = self.git("rev-parse", "--short", "HEAD").stdout.strip()
        out = {"ok": True, "commit": sha, "applied": len(done), "left": left, "results": results, "message": msg}
        if self.push:
            pushed = self.git("push", "origin", "main")
            out["pushed"] = pushed.returncode == 0
            if not pushed.returncode == 0:
                out["message"] += " · 커밋은 했지만 푸시하지 못했다: " + pushed.stderr.strip()
        else:
            out["pushed"] = False
        return out


# --------------------------------------------------------------- HTTP 서버 --

def inject(src: str, page: str, preview: bool) -> str:
    """HTML 끝에 편집 도구를 끼워 넣는다. 원본 파일은 바꾸지 않는다."""
    cfg = json.dumps({"page": page, "preview": preview}, ensure_ascii=False)
    snippet = (f'<link rel="stylesheet" href="/__editor__/editor.css">'
               f'<script>window.CME_CONFIG={cfg};</script>'
               f'<script src="/__editor__/editor.js"></script>')
    k = src.lower().rfind("</body>")
    return src[:k] + snippet + src[k:] if k >= 0 else src + snippet


class Handler(SimpleHTTPRequestHandler):
    workspace: Workspace

    def log_message(self, fmt: str, *args) -> None:  # 요청마다 찍히는 줄을 줄인다
        if not self.path.startswith("/__editor__/api"):
            return
        super().log_message(fmt, *args)

    # -- 도우미
    def _send(self, body: bytes, ctype: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj: dict, status: int = 200) -> None:
        self._send(json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", status)

    def _page(self, q: dict) -> Path:
        return self.workspace.page_path((q.get("page") or [""])[0])

    # -- GET
    def do_GET(self) -> None:
        url = urlsplit(self.path)
        q = parse_qs(url.query)
        path = unquote(url.path)
        try:
            if path in ("/__editor__/editor.js", "/__editor__/editor.css"):
                f = EDITOR_ASSETS / path.rsplit("/", 1)[1]
                ctype = "text/javascript; charset=utf-8" if f.suffix == ".js" else "text/css; charset=utf-8"
                return self._send(f.read_bytes(), ctype)
            if path == "/__editor__/api/edits":
                return self._json(self.workspace.load(self._page(q)))
            if path == "/__editor__/api/check":
                pf = self._page(q)
                data = self.workspace.load(pf)
                return self._json({"results": check_items(pf.read_text(encoding="utf-8"), data["items"])})
            rel = path.lstrip("/")
            if rel == "" or rel.endswith("/"):
                rel += "index.html"
            if rel.endswith(".html"):
                pf = self.workspace.page_path(rel)
                src = pf.read_text(encoding="utf-8")
                preview = (q.get("cme") or [""])[0] == "preview"
                if preview:
                    src, _ = apply_items(src, self.workspace.load(pf)["items"])
                return self._send(inject(src, self.workspace.rel(pf), preview).encode("utf-8"), "text/html; charset=utf-8")
        except ValueError as e:
            return self._json({"error": str(e)}, HTTPStatus.NOT_FOUND)
        return super().do_GET()

    # -- POST
    def do_POST(self) -> None:
        if self.headers.get(API_HEADER) != "1":
            return self._json({"error": "편집 도구에서 보낸 요청이 아니다."}, HTTPStatus.FORBIDDEN)
        url = urlsplit(self.path)
        q = parse_qs(url.query)
        try:
            pf = self._page(q)
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}")
            ws = self.workspace
            if url.path == "/__editor__/api/save":
                data = ws.load(pf)
                it = body.get("item") or {}
                it.setdefault("id", uuid.uuid4().hex[:10])
                it.setdefault("created", datetime.now().astimezone().isoformat(timespec="seconds"))
                it["status"] = "pending"
                keep = ("id", "created", "mode", "find", "replace", "before", "after", "note", "occurrence", "status")
                it = {k: it[k] for k in keep if k in it}
                data["items"] = [x for x in data["items"] if x.get("id") != it["id"]] + [it]
                ws.save(pf, data)
                return self._json({"ok": True, "item": it})
            if url.path == "/__editor__/api/delete":
                data = ws.load(pf)
                data["items"] = [x for x in data["items"] if x.get("id") != body.get("id") or x.get("status") == "published"]
                ws.save(pf, data)
                return self._json({"ok": True})
            if url.path == "/__editor__/api/publish":
                return self._json(ws.publish(pf))
        except (ValueError, json.JSONDecodeError) as e:
            return self._json({"error": str(e)}, HTTPStatus.BAD_REQUEST)
        return self._json({"error": "알 수 없는 요청"}, HTTPStatus.NOT_FOUND)


def main() -> None:
    """편집 서버를 연다."""
    parser = argparse.ArgumentParser(description="자료 쪽 편집과 쪽별 Publish 를 위한 로컬 서버")
    parser.add_argument("--port", type=int, default=8001, help="열 포트 (기본 8001)")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="저장소 위치 (기본: 이 스크립트가 있는 저장소)")
    parser.add_argument("--no-push", action="store_true", help="Publish 때 커밋만 하고 푸시하지 않는다")
    args = parser.parse_args()
    ws = Workspace(args.root, push=not args.no_push)
    if not ws.docs.is_dir():
        sys.exit(f"docs 폴더가 없다: {ws.docs}")
    handler = partial(type("BoundHandler", (Handler,), {"workspace": ws}), directory=str(ws.docs))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"편집 서버: http://127.0.0.1:{args.port}  (docs: {ws.docs}, 편집 파일: {ws.edits})")
    print("Publish 하면 그 쪽의 HTML 과 편집 파일을 main 에 커밋" + ("하고 푸시한다." if ws.push else "한다(푸시 안 함)."))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n편집 서버를 닫는다.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
