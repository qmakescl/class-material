/* 로컬 편집 도구 (src/python/edit_server.py 가 쪽을 내보낼 때만 끼워 넣는다. 배포본에는 없다)
   - "편집" 단추로 편집 모드를 켜고 끈다. 켜면 글을 드래그해 고칠 내용을 적는다.
   - 항목은 서버가 edits/<쪽 경로>.json 에 저장한다.
   - "검사"는 항목마다 원문에서 찾았는지와 바뀌는 부분을 보여 준다.
   - "편집본 보기"는 대기 항목을 적용한 쪽을 새 탭에 연다.
   - "Publish"는 이 쪽만 반영하고 main 에 커밋·푸시한다. */
(() => {
  const CFG = window.CME_CONFIG || {};
  const PAGE = CFG.page;
  if (!PAGE) return;
  const API = "/__editor__/api/";
  const q = "?page=" + encodeURIComponent(PAGE);
  let data = { items: [] }, checks = {}, on = false, editing = null, armed = false;

  const el = (tag, attrs = {}, ...kids) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "text") e.textContent = v; else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v);
    }
    kids.flat().forEach(k => e.append(k));
    return e;
  };
  const post = (path, body) => fetch(API + path + q, {
    method: "POST", headers: { "Content-Type": "application/json", "X-CME": "1" }, body: JSON.stringify(body || {})
  }).then(r => r.json());
  const get = path => fetch(API + path + q, { cache: "no-store" }).then(r => r.json());

  /* ---------- 화면 ---------- */
  const fab = el("button", { type: "button", class: "cme-fab", "aria-expanded": "false", text: CFG.preview ? "편집본 미리보기" : "편집" });
  const status = el("p", { class: "cme-status", role: "status" });
  const list = el("ol", { class: "cme-list" });
  const btnCheck = el("button", { type: "button", text: "검사" });
  const btnPreview = el("button", { type: "button", text: "편집본 보기" });
  const btnPublish = el("button", { type: "button", class: "cme-primary", text: "Publish" });
  const panel = el("section", { class: "cme-panel", hidden: "", "aria-label": "편집 도구" },
    el("header", {}, el("b", { text: "편집" }), el("span", { class: "cme-page", text: PAGE })),
    el("p", { class: "cme-help", text: "편집 모드에서 고칠 글을 드래그하면 입력 칸이 열린다. 수식이나 그림 속 글처럼 찾지 못하는 곳은 'HTML 원문에서 그대로 찾기'를 켜고 원문을 적는다." }),
    list, el("div", { class: "cme-actions" }, btnCheck, btnPreview, btnPublish), status);

  const fFind = el("textarea", { rows: "2", "aria-label": "원래 글" });
  const fRep = el("textarea", { rows: "2", "aria-label": "바꿀 글" });
  const fNote = el("input", { type: "text", "aria-label": "메모", placeholder: "메모(선택)" });
  const fMode = el("input", { type: "checkbox", id: "cme-mode" });
  const fOcc = el("input", { type: "number", min: "1", placeholder: "몇 번째", "aria-label": "같은 글 가운데 몇 번째" });
  const form = el("form", { class: "cme-form", hidden: "" },
    el("label", { text: "원래 글" }), fFind,
    el("div", { class: "cme-row" }, fMode, el("label", { for: "cme-mode", text: "HTML 원문에서 그대로 찾기" }), fOcc),
    el("label", { text: "바꿀 글" }), fRep, fNote,
    el("div", { class: "cme-actions" },
      el("button", { type: "submit", class: "cme-primary", text: "저장" }),
      el("button", { type: "button", text: "취소", onclick: () => closeForm() })));
  const ui = el("div", { class: "cme-ui" }, fab, panel, form);
  document.body.append(ui);

  const setStatus = (t, bad) => { status.textContent = t; status.classList.toggle("cme-bad", !!bad); };
  const LABEL = { ok: "반영 가능", notfound: "찾지 못함", ambiguous: "여러 곳", tags: "태그를 걸침", overlap: "다른 항목과 겹침", empty: "비어 있음" };

  function render() {
    list.replaceChildren();
    const items = data.items.slice().reverse();
    if (!items.length) list.append(el("li", { class: "cme-empty", text: "아직 항목이 없다." }));
    for (const it of items) {
      const c = checks[it.id];
      const badge = it.status === "published" ? ["반영됨", "done"] : c ? [LABEL[c.status] + (c.count > 1 && c.status !== "ok" ? ` (${c.count})` : ""), c.status] : ["대기", "wait"];
      const li = el("li", { class: "cme-item" },
        el("span", { class: "cme-badge cme-" + badge[1], text: badge[0] }),
        el("div", { class: "cme-diff" },
          el("del", { text: it.find }), el("span", { text: " → " }), el("ins", { text: it.replace || "(지움)" }),
          it.mode === "source" ? el("small", { text: " · HTML 원문" }) : "",
          it.note ? el("small", { text: " · " + it.note }) : "",
          c && c.line ? el("small", { text: ` · ${c.line}줄` }) : ""));
      if (it.status !== "published") {
        li.append(el("div", { class: "cme-item-actions" },
          el("button", { type: "button", text: "고치기", onclick: () => openForm(it) }),
          el("button", { type: "button", text: "지우기", onclick: () => del(it.id) })));
      }
      list.append(li);
    }
    const pending = data.items.filter(i => i.status !== "published").length;
    fab.textContent = (CFG.preview ? "편집본 미리보기" : "편집") + (pending ? ` · ${pending}` : "");
    markPage();
  }

  /* 화면 속 대기 항목에 표시를 단다(한 글자 노드 안에서 찾은 것만) */
  function markPage() {
    document.querySelectorAll("mark.cme-mark").forEach(m => m.replaceWith(...m.childNodes));
    if (CFG.preview) return;
    const root = document.querySelector("main") || document.body;
    for (const it of data.items) {
      if (it.status === "published" || it.mode === "source" || !it.find) continue;
      const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
        acceptNode: n => n.parentElement.closest(".cme-ui,script,style") ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT
      });
      let n;
      while ((n = w.nextNode())) {
        const k = n.nodeValue.indexOf(it.find);
        if (k < 0) continue;
        const r = document.createRange();
        r.setStart(n, k); r.setEnd(n, k + it.find.length);
        const m = el("mark", { class: "cme-mark", title: "→ " + (it.replace || "(지움)") });
        r.surroundContents(m);
        break;
      }
    }
  }

  async function load() {
    try { data = await get("edits"); render(); }
    catch (e) { setStatus("편집 파일을 읽지 못했다: " + e, true); }
  }

  /* ---------- 입력 칸 ---------- */
  function openForm(it, at) {
    editing = it || null;
    fFind.value = it ? it.find : ""; fRep.value = it ? (it.replace || "") : ""; fNote.value = it ? (it.note || "") : "";
    fMode.checked = !!(it && it.mode === "source"); fOcc.value = it && it.occurrence ? it.occurrence : "";
    form.hidden = false;
    const x = at ? Math.min(at.x, innerWidth - 380) : innerWidth - 400, y = at ? Math.min(at.y + 12, innerHeight - 320) : 80;
    form.style.left = Math.max(8, x) + "px"; form.style.top = Math.max(8, y) + "px";
    (it ? fRep : fRep).focus();
  }
  function closeForm() { form.hidden = true; editing = null; }

  form.addEventListener("submit", async ev => {
    ev.preventDefault();
    const item = Object.assign({}, editing || {}, {
      find: fFind.value, replace: fRep.value, note: fNote.value.trim(),
      mode: fMode.checked ? "source" : "text"
    });
    const occ = parseInt(fOcc.value, 10); if (occ > 0) item.occurrence = occ; else delete item.occurrence;
    if (!item.find.trim()) { setStatus("원래 글이 비어 있다.", true); return; }
    const r = await post("save", { item });
    if (r.error) { setStatus(r.error, true); return; }
    closeForm(); checks = {}; await load(); setStatus("저장했다. 검사를 눌러 반영할 수 있는지 확인한다.");
  });

  /* 편집 모드에서 글을 드래그하면 입력 칸을 연다. 앞뒤 문맥을 함께 저장해 같은 글이 여러 번 나와도 자리를 고른다 */
  document.addEventListener("mouseup", ev => {
    if (!on || ev.target.closest(".cme-ui")) return;
    const sel = getSelection();
    if (!sel || sel.isCollapsed) return;
    const text = sel.toString();
    if (!text.trim()) return;
    const range = sel.getRangeAt(0), root = document.querySelector("main") || document.body;
    const pre = document.createRange(); pre.setStart(root, 0); pre.setEnd(range.startContainer, range.startOffset);
    const post_ = document.createRange(); post_.setStart(range.endContainer, range.endOffset); post_.setEnd(root, root.childNodes.length);
    openForm(null, { x: ev.clientX, y: ev.clientY });
    fFind.value = text;
    editing = { before: pre.toString().slice(-80), after: post_.toString().slice(0, 80) };
  }, true);

  async function del(id) { await post("delete", { id }); checks = {}; await load(); setStatus("지웠다."); }

  btnCheck.addEventListener("click", async () => {
    const r = await get("check");
    checks = {}; (r.results || []).forEach(x => { checks[x.id] = x; });
    const n = Object.values(checks), ok = n.filter(x => x.status === "ok").length;
    render();
    setStatus(n.length ? `대기 ${n.length}건 가운데 ${ok}건을 반영할 수 있다.` + (ok < n.length ? " 나머지는 원래 글을 고치거나 'HTML 원문에서 그대로 찾기'를 쓴다." : "") : "대기 항목이 없다.", ok < n.length);
  });
  btnPreview.addEventListener("click", () => window.open(location.pathname + "?cme=preview", "_blank"));
  btnPublish.addEventListener("click", async () => {
    if (!armed) { armed = true; btnPublish.textContent = "이 쪽을 반영하고 main 에 올릴까? 한 번 더 누른다"; setTimeout(() => { armed = false; btnPublish.textContent = "Publish"; }, 6000); return; }
    armed = false; btnPublish.textContent = "Publish"; btnPublish.disabled = true; setStatus("반영하는 중…");
    try {
      const r = await post("publish");
      if (r.ok) setStatus(`${r.message} · 커밋 ${r.commit}` + (r.pushed ? " · 푸시함" : "") + (r.left ? ` · 남은 항목 ${r.left}건` : "") + " · 새로고침하면 반영된 쪽이 보인다.");
      else setStatus(r.message || r.error, true);
      checks = {}; (r.results || []).forEach(x => { if (x.status !== "ok") checks[x.id] = x; });
      await load();
    } finally { btnPublish.disabled = false; }
  });

  fab.addEventListener("click", () => {
    on = !on;
    panel.hidden = !on; form.hidden = true;
    fab.setAttribute("aria-expanded", String(on));
    document.body.classList.toggle("cme-on", on);
    if (on && !CFG.preview) setStatus("편집 모드: 고칠 글을 드래그한다.");
  });
  if (CFG.preview) { btnCheck.disabled = btnPublish.disabled = true; setStatus("대기 항목을 적용한 미리보기다. 여기서는 편집하지 않는다."); }

  window.CME = { load, data: () => data, check: () => btnCheck.click() };
  load();
})();
