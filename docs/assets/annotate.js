/* 형광펜과 메모 (자료 페이지 공통 — docs/{subject}/ 의 자료 쪽이 함께 쓴다)
   - 본문(main)의 글을 드래그하면 형광펜 버튼이 뜬다. 칠한 곳을 누르면 메모를 적거나 색을 바꾸거나 지울 수 있다.
   - 저장: 쪽마다 localStorage 한 칸("cm-anno:v1:" + 경로). 서버로 보내지 않으므로 칠한 그 브라우저에서만 보인다.
   - 위치는 글자 번호가 아니라 "칠한 글 + 앞뒤 32자"로 기억한다. 본문이 조금 바뀌어도 같은 글을 다시 찾아 칠한다.
   - 수식(KaTeX, MathJax)은 쪼개지 않고 통째로 칠한다. 버튼·입력칸·SVG·캔버스 안의 글자는 칠하지 않는다.
   - 스타일은 같은 폴더의 annotate.css 를 이 스크립트가 불러온다.
     쪽에는 <script defer src="../assets/annotate.js"></script> 한 줄만 넣는다. */
(() => {
  "use strict";

  const self = document.currentScript;
  if (self && self.src) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = new URL("annotate.css", self.src).href;
    document.head.appendChild(link);
  }

  const KEY = "cm-anno:v1:" + location.pathname.replace(/\/$/, "/index.html");
  const PEN_KEY = "cm-anno:pen";
  const COLOR_KEY = "cm-anno:color";
  const COLORS = [["y", "노랑"], ["g", "초록"], ["p", "분홍"], ["b", "파랑"]];
  const ATOM = ".katex-display, .katex, mjx-container";
  const SKIP = "script,style,noscript,template,svg,canvas,button,select,option,textarea,input,.anno-ui";
  const FLOW = /^(inline|block|inline-block|list-item|table-cell|table-caption|flow-root)$/;
  const CTX = 32;
  const MAX_QUOTE = 4000;
  const MAX_NOTE = 500;

  let root, ui, pop, card, note, fab, panel, list, empty, clearBtn, penBox;
  let items = [];
  const lost = new Set();   // 저장되어 있지만 본문에서 찾지 못한 것
  let pending = null;       // 드래그해 두고 아직 칠하지 않은 범위
  let openId = null;        // 메모 상자가 열려 있는 형광펜
  let pen = false;          // 드래그하면 바로 칠하기
  let color = "y";
  let touch = false;
  let saveTimer = 0;

  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 저장이 막힌 환경: 이 화면에서만 유지 */ } },
    del(k) { try { localStorage.removeItem(k); } catch (e) { /* 위와 같다 */ } }
  };
  const isColor = (c) => COLORS.some((x) => x[0] === c);
  const within = (t, sel) => (t && t.closest ? t.closest(sel) : null);
  const byId = (id) => items.find((it) => it.id === id);
  const clip = (s, n) => { s = s.replace(/\s+/g, " ").trim(); return s.length > n ? s.slice(0, n - 1) + "…" : s; };
  const el = (tag, attrs, ...kids) => {
    const n = document.createElement(tag);
    Object.keys(attrs || {}).forEach((k) => n.setAttribute(k, attrs[k]));
    n.append(...kids);
    return n;
  };

  function load() {
    try {
      const d = JSON.parse(store.get(KEY) || "null");
      items = (d && Array.isArray(d.items) ? d.items : [])
        .filter((it) => it && /^[a-z0-9]+$/.test(it.id) && typeof it.q === "string" && it.q)
        .map((it) => ({
          id: it.id, q: it.q, pre: String(it.pre || ""), suf: String(it.suf || ""), pos: +it.pos || 0,
          label: String(it.label || ""), c: isColor(it.c) ? it.c : "y", note: String(it.note || "").slice(0, MAX_NOTE), t: +it.t || 0
        }));
    } catch (e) { items = []; }
    pen = store.get(PEN_KEY) === "1";
    const c = store.get(COLOR_KEY);
    if (isColor(c)) color = c;
  }
  function save() {
    clearTimeout(saveTimer);
    if (items.length) store.set(KEY, JSON.stringify({ v: 1, items }));
    else store.del(KEY);
  }
  const saveSoon = () => { clearTimeout(saveTimer); saveTimer = setTimeout(save, 300); };

  /* ── 본문 글자열: 칠할 수 있는 텍스트 노드를 문서 순서대로 이어 붙인 것 ── */
  const atomOf = (p) => { const a = p.closest(ATOM); return a ? a.closest(".katex-display") || a : null; };
  function stream() {
    const nodes = [], parts = [];
    const w = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode: (n) => (n.nodeType === 3 ? NodeFilter.FILTER_ACCEPT : n.matches(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_SKIP)
    });
    let len = 0, n;
    while ((n = w.nextNode())) {
      if (!n.data || !n.parentElement) continue;
      nodes.push({ node: n, start: len, atom: atomOf(n.parentElement) });
      parts.push(n.data);
      len += n.data.length;
    }
    return { nodes, text: parts.join("") };
  }

  /* 목록에 보여 줄 글: 수식은 안의 글자 대신 표시 하나로 줄인다 */
  function labelOf(st, s, e) {
    let out = "", last = null, box = null;
    for (const en of st.nodes) {
      const a = Math.max(s, en.start), b = Math.min(e, en.start + en.node.data.length);
      if (a >= b) { if (en.start >= e) break; continue; }
      // 표의 칸이나 문단이 바뀌면 글이 붙지 않게 한 칸 띄운다
      const here = en.node.parentElement.closest("td,th,p,li,dt,dd,pre,h2,h3,h4,figcaption,summary");
      if (here !== box) { out += " "; box = here; }
      if (en.atom) { if (en.atom !== last) out += " 〔수식〕 "; last = en.atom; }
      else out += en.node.data.slice(a - en.start, b - en.start);
    }
    return clip(out, 120);
  }

  /* 드래그한 범위 → 저장할 정보(칠한 글, 앞뒤 글, 위치). 수식에 걸치면 수식 전체로 넓힌다 */
  function pickFromRange(range) {
    const st = stream(), touched = new Set();
    let s = -1, e = -1;
    for (const en of st.nodes) {
      if (!range.intersectsNode(en.node)) { if (s >= 0) break; continue; }
      const a = en.node === range.startContainer ? range.startOffset : 0;
      const b = en.node === range.endContainer ? range.endOffset : en.node.data.length;
      if (a >= b) continue;
      if (en.atom) touched.add(en.atom);
      if (s < 0) s = en.start + a;
      e = en.start + b;
    }
    if (s < 0) return null;
    if (touched.size) st.nodes.forEach((en) => {
      if (touched.has(en.atom)) { s = Math.min(s, en.start); e = Math.max(e, en.start + en.node.data.length); }
    });
    const t = st.text;
    while (s < e && /\s/.test(t[s])) s++;
    while (e > s && /\s/.test(t[e - 1])) e--;
    if (e <= s || e - s > MAX_QUOTE) return null;
    return { q: t.slice(s, e), pre: t.slice(Math.max(0, s - CTX), s), suf: t.slice(e, e + CTX), pos: s, label: labelOf(st, s, e) };
  }

  /* 저장된 글을 본문에서 다시 찾는다: 같은 글이 여러 번 나오면 앞뒤 글이 가장 많이 맞는 곳, 그다음 원래 위치에 가까운 곳 */
  function locate(it, st) {
    const t = st.text, q = it.q;
    let best = -1, bestScore = -1, i = t.indexOf(q), tries = 0;
    while (i >= 0 && tries++ < 400) {
      let sc = 0;
      for (let k = 1; k <= it.pre.length && t[i - k] === it.pre[it.pre.length - k]; k++) sc++;
      for (let k = 0; k < it.suf.length && t[i + q.length + k] === it.suf[k]; k++) sc++;
      if (sc > bestScore || (sc === bestScore && Math.abs(i - it.pos) < Math.abs(best - it.pos))) { best = i; bestScore = sc; }
      i = t.indexOf(q, i + 1);
    }
    return best;
  }

  const marksOf = (id) => root.querySelectorAll('mark.anno[data-anno="' + id + '"]');
  const atomsOf = (id) => root.querySelectorAll('.anno-atom[data-anno~="' + id + '"]');
  const inlineLike = (n) => !!n && (n.nodeType === 3 || (n.nodeType === 1 && /^inline/.test(getComputedStyle(n).display)));

  /* 텍스트 노드의 [a, b) 를 <mark> 로 감싼다. 레이아웃을 건드리지 않도록 빈칸뿐인 조각과 flex·grid 안의 글은 따로 다룬다 */
  function wrap(node, a, b, it) {
    const p = node.parentElement;
    if (!p) return;
    const flow = FLOW.test(getComputedStyle(p).display);
    if (!/\S/.test(node.data.slice(a, b))) {
      // 블록 사이의 줄바꿈 같은 빈칸을 감싸면 빈 줄이나 표의 빈 칸이 생긴다. 글 사이에 낀 빈칸만 칠한다.
      if (!flow || !inlineLike(node.previousSibling) || !inlineLike(node.nextSibling)) return;
    } else if (!flow) {
      // flex·grid 바로 아래의 글은 쪼개면 칸이 나뉜다. 글 덩어리를 통째로 칠한다.
      a = 0; b = node.data.length;
    }
    let mid = node;
    if (a > 0) mid = node.splitText(a);
    if (b - a < mid.data.length) mid.splitText(b - a);
    const m = document.createElement("mark");
    m.className = "anno";
    m.dataset.anno = it.id;
    mid.parentNode.insertBefore(m, mid);
    m.appendChild(mid);
  }

  /* 색·메모 표시를 칠해진 조각 전체에 맞춘다 */
  function decorate(it) {
    const ms = Array.from(marksOf(it.id));
    ms.forEach((m, i) => {
      m.className = "anno anno-" + it.c + (it.note ? " has-note" : "") + (it.note && i === ms.length - 1 ? " anno-end" : "");
      if (it.note) m.title = it.note; else m.removeAttribute("title");
    });
    atomsOf(it.id).forEach((a) => {
      COLORS.forEach((c) => a.classList.remove("anno-" + c[0]));
      a.classList.add("anno-" + it.c);
      a.classList.toggle("has-note", !!it.note);
    });
  }

  function paint(it) {
    const st = stream(), s = locate(it, st);
    if (s < 0) return false;
    const e = s + it.q.length, todo = [], atoms = new Set();
    for (const en of st.nodes) {
      const a = Math.max(s, en.start) - en.start, b = Math.min(e, en.start + en.node.data.length) - en.start;
      if (a >= b) { if (en.start >= e) break; continue; }
      if (en.atom) atoms.add(en.atom); else todo.push([en.node, a, b]);
    }
    todo.forEach((x) => wrap(x[0], x[1], x[2], it));
    atoms.forEach((a) => {
      const ids = (a.dataset.anno || "").split(" ").filter(Boolean);
      if (!ids.includes(it.id)) ids.push(it.id);
      a.dataset.anno = ids.join(" ");
      a.classList.add("anno-atom");
    });
    it.pos = s;
    decorate(it);
    return true;
  }

  function unpaint(id) {
    marksOf(id).forEach((m) => {
      const p = m.parentNode;
      while (m.firstChild) p.insertBefore(m.firstChild, m);
      p.removeChild(m);
      p.normalize();
    });
    atomsOf(id).forEach((a) => {
      const ids = a.dataset.anno.split(" ").filter((x) => x && x !== id);
      if (ids.length) {
        a.dataset.anno = ids.join(" ");
        const rest = byId(ids[ids.length - 1]);
        if (rest && rest.id !== id) decorate(rest);
      } else {
        delete a.dataset.anno;
        a.classList.remove("anno-atom", "has-note", "anno-flash");
        COLORS.forEach((c) => a.classList.remove("anno-" + c[0]));
      }
    });
  }

  function create(pick, c) {
    const it = {
      id: "a" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
      q: pick.q, pre: pick.pre, suf: pick.suf, pos: pick.pos, label: pick.label, c, note: "", t: Date.now()
    };
    if (!paint(it)) return null;
    items.push(it);
    save();
    refresh();
    return it;
  }

  function remove(id) {
    unpaint(id);
    items = items.filter((it) => it.id !== id);
    lost.delete(id);
    if (openId === id) closeCard();
    save();
    refresh();
  }

  /* ── 화면 조각 ── */
  const swatches = () => COLORS.map((c) => el("button", {
    type: "button", class: "anno-sw anno-" + c[0], "data-c": c[0], "aria-pressed": "false",
    "aria-label": c[1] + " 형광펜", title: c[1] + " 형광펜"
  }));
  const syncSwatches = (box, c) => box.querySelectorAll(".anno-sw").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.c === c)));

  function buildUI() {
    pop = el("div", { class: "anno-pop", role: "toolbar", "aria-label": "형광펜" },
      ...swatches(), el("button", { type: "button", class: "anno-memo", "data-act": "memo" }, "메모"));
    pop.hidden = true;

    note = el("textarea", { rows: "3", maxlength: String(MAX_NOTE), "aria-label": "메모", placeholder: "메모를 적는다. 이 브라우저에만 저장된다." });
    card = el("div", { class: "anno-card", role: "dialog", "aria-label": "형광펜 메모" },
      el("div", { class: "anno-row" }, ...swatches(), el("button", { type: "button", class: "anno-text", "data-act": "del" }, "지우기")),
      note,
      el("div", { class: "anno-row anno-right" }, el("button", { type: "button", class: "anno-text", "data-act": "close" }, "닫기")));
    card.hidden = true;

    fab = el("button", { type: "button", class: "anno-fab", "aria-expanded": "false", "aria-controls": "anno-panel" }, "형광펜", el("b", {}));

    penBox = el("input", { type: "checkbox" });
    list = el("ol", { class: "anno-list" });
    empty = el("p", { class: "anno-empty" }, "아직 칠한 곳이 없다.");
    clearBtn = el("button", { type: "button", class: "anno-text", "data-act": "clear" }, "모두 지우기");
    panel = el("div", { class: "anno-panel", id: "anno-panel", role: "region", "aria-label": "형광펜과 메모" },
      el("div", { class: "anno-row" }, el("strong", {}, "형광펜과 메모"),
        el("button", { type: "button", class: "anno-text", "data-act": "panel-close", "aria-label": "닫기" }, "×")),
      el("p", { class: "anno-help" }, "본문을 드래그하면 형광펜 버튼이 나온다. 칠한 곳을 누르면 메모를 적거나 지울 수 있다. 이 브라우저에만 저장된다."),
      el("label", { class: "anno-pen" }, penBox, "드래그하면 바로 칠하기"),
      list, empty,
      el("div", { class: "anno-row anno-right" }, clearBtn));
    panel.hidden = true;

    ui = el("div", { class: "anno-ui" }, pop, card, fab, panel);
    document.body.appendChild(ui);
  }

  function refresh() {
    const n = items.length;
    fab.querySelector("b").textContent = n ? String(n) : "";
    fab.classList.toggle("is-pen", pen);
    fab.title = pen ? "형광펜과 메모 (드래그하면 바로 칠하기 켜짐)" : "형광펜과 메모";
    penBox.checked = pen;
    empty.hidden = n > 0;
    clearBtn.hidden = n === 0;
    resetClear();
    list.textContent = "";
    items.slice().sort((a, b) => a.pos - b.pos).forEach((it) => {
      const go = el("button", { type: "button", class: "anno-go anno-" + it.c, "data-go": it.id },
        el("span", { class: "anno-q" }, it.label || clip(it.q, 120)));
      if (it.note) go.append(el("span", { class: "anno-n" }, it.note));
      if (lost.has(it.id)) go.append(el("span", { class: "anno-lost" }, "본문에서 이 글을 찾지 못했다"));
      list.append(el("li", {}, go,
        el("button", { type: "button", class: "anno-x", "data-del": it.id, "aria-label": "이 형광펜 지우기", title: "지우기" }, "×")));
    });
  }

  /* 상자를 화면 좌표 (x, first) 에 놓는다. first 자리에 들어가지 않으면 second 를 쓴다 */
  function place(box, x, first, second) {
    const w = box.offsetWidth, h = box.offsetHeight, vw = document.documentElement.clientWidth, vh = window.innerHeight;
    const fits = (t) => t >= 8 && t + h <= vh - 8;
    const top = fits(first) || !fits(second) ? Math.max(8, first) : second;
    box.style.left = Math.max(8, Math.min(x, vw - w - 8)) + window.scrollX + "px";
    box.style.top = top + window.scrollY + "px";
  }

  function hidePop() { pending = null; if (pop) pop.hidden = true; }
  function showPop(range, pt) {
    pop.hidden = false;
    syncSwatches(pop, color);
    const rects = range.getClientRects();
    const r = rects.length ? rects[rects.length - 1] : range.getBoundingClientRect();
    const x = pt ? pt.x : r.right, top = pt ? pt.y - 14 : r.top, bottom = pt ? pt.y + 18 : r.bottom;
    place(pop, x - pop.offsetWidth / 2, top - pop.offsetHeight - 6, bottom + 6);
  }

  function closeCard() {
    if (openId) { clearTimeout(saveTimer); save(); }
    openId = null;
    if (card) card.hidden = true;
  }
  function openCard(id, at, focus) {
    const it = byId(id);
    if (!it) return;
    hidePop();
    openId = id;
    card.hidden = false;
    note.value = it.note;
    syncSwatches(card, it.c);
    place(card, at.x - 24, at.bottom + 8, at.top - card.offsetHeight - 8);
    if (focus) note.focus({ preventScroll: true });
  }
  /* 칠해진 마지막 조각의 자리 */
  function anchorOf(id) {
    const all = [...marksOf(id), ...atomsOf(id)];
    if (!all.length) return null;
    const rects = all[all.length - 1].getClientRects();
    const r = rects.length ? rects[rects.length - 1] : all[all.length - 1].getBoundingClientRect();
    return { x: r.left + 24, top: r.top, bottom: r.bottom };
  }

  function closePanel() { if (panel && !panel.hidden) { panel.hidden = true; fab.setAttribute("aria-expanded", "false"); } }
  function resetClear() { clearBtn.textContent = "모두 지우기"; delete clearBtn.dataset.armed; }

  function go(id) {
    const it = byId(id);
    if (!it) return;
    let first = marksOf(id)[0] || atomsOf(id)[0];
    if (!first) {
      // 위젯이 그 자리를 다시 그렸을 수 있다. 한 번 더 찾아 칠한다.
      unpaint(id);
      if (paint(it)) lost.delete(id); else lost.add(id);
      refresh();
      first = marksOf(id)[0] || atomsOf(id)[0];
    }
    if (!first) return;
    for (let d = first.closest("details"); d; d = d.parentElement && d.parentElement.closest("details")) d.open = true;
    first.scrollIntoView({ block: "center" });
    const all = [...marksOf(id), ...atomsOf(id)];
    all.forEach((x) => { x.classList.remove("anno-flash"); void x.offsetWidth; x.classList.add("anno-flash"); });
    setTimeout(() => all.forEach((x) => x.classList.remove("anno-flash")), 1600);
  }

  /* ── 드래그가 끝났을 때 ── */
  function onSelectEnd(ev) {
    if (ev && within(ev.target, ".anno-ui")) return;
    const pt = ev && ev.type === "pointerup" ? { x: ev.clientX, y: ev.clientY } : null;
    setTimeout(() => {
      const sel = window.getSelection();
      if (!sel || sel.isCollapsed || !sel.rangeCount) { hidePop(); return; }
      const range = sel.getRangeAt(0);
      const pick = pickFromRange(range);
      if (!pick) { hidePop(); return; }
      if (pen && !touch) {
        if (create(pick, color)) sel.removeAllRanges();
        return;
      }
      pending = pick;
      showPop(range, pt);
    }, 0);
  }

  function paintPending(withNote) {
    if (!pending) return;
    const it = create(pending, color);
    hidePop();
    const sel = window.getSelection();
    if (sel) sel.removeAllRanges();
    if (it && withNote) { const at = anchorOf(it.id); if (at) openCard(it.id, at, true); }
  }

  function bind() {
    document.addEventListener("pointerdown", (e) => {
      touch = e.pointerType === "touch" || e.pointerType === "pen";
      if (within(e.target, ".anno-ui")) return;
      hidePop();
      if (!within(e.target, "mark.anno, .anno-atom")) closeCard();
      closePanel();
    }, true);
    document.addEventListener("pointerup", (e) => {
      // 슬라이더·그림·버튼을 만진 것은 드래그로 치지 않는다
      if (within(e.target, SKIP)) return;
      onSelectEnd(e);
    }, true);
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { hidePop(); closeCard(); closePanel(); }
      else if (e.key === "Enter" && (e.metaKey || e.ctrlKey) && e.target === note) closeCard();
    });
    document.addEventListener("keyup", (e) => {
      if (within(e.target, ".anno-ui") || !(e.shiftKey || e.key === "Shift")) return;
      onSelectEnd(null);
    });
    let selTimer = 0;
    document.addEventListener("selectionchange", () => {
      const sel = window.getSelection();
      if (!sel || sel.isCollapsed) { hidePop(); return; }
      // 터치에서는 손을 뗀 뒤에야 선택이 정해진다
      if (touch) { clearTimeout(selTimer); selTimer = setTimeout(() => onSelectEnd(null), 400); }
    });

    // 칠한 곳을 누르면 메모 상자를 연다 (링크·펼침 제목 위에서는 원래 동작을 그대로 둔다)
    document.addEventListener("click", (e) => {
      const m = within(e.target, "mark.anno, .anno-atom");
      if (!m || !root.contains(m) || within(e.target, "a[href], summary")) return;
      const sel = window.getSelection();
      if (sel && !sel.isCollapsed) return;
      const ids = (m.dataset.anno || "").split(" ").filter(Boolean);
      if (ids.length) openCard(ids[ids.length - 1], { x: e.clientX, top: e.clientY - 12, bottom: e.clientY + 12 }, false);
    });

    // 버튼을 눌러도 본문의 선택이 풀리지 않게 한다
    pop.addEventListener("mousedown", (e) => e.preventDefault());

    ui.addEventListener("click", (e) => {
      const b = within(e.target, "button");
      if (!b) return;
      const act = b.dataset.act;
      if (b.dataset.c) {
        color = b.dataset.c;
        store.set(COLOR_KEY, color);
        if (pop.contains(b)) paintPending(false);
        else { const it = byId(openId); if (it) { it.c = color; decorate(it); syncSwatches(card, color); save(); refresh(); } }
      } else if (act === "memo") paintPending(true);
      else if (act === "del") { if (openId) remove(openId); }
      else if (act === "close") closeCard();
      else if (act === "panel-close") { closePanel(); fab.focus(); }
      else if (act === "clear") {
        if (!b.dataset.armed) {
          b.dataset.armed = "1";
          b.textContent = "한 번 더 누르면 모두 지운다";
          setTimeout(resetClear, 4000);
        } else {
          items.slice().forEach((it) => unpaint(it.id));
          items = [];
          lost.clear();
          closeCard();
          save();
          refresh();
        }
      } else if (b.dataset.go) go(b.dataset.go);
      else if (b.dataset.del) remove(b.dataset.del);
      else if (b === fab) {
        panel.hidden = !panel.hidden;
        fab.setAttribute("aria-expanded", String(!panel.hidden));
      }
    });

    note.addEventListener("input", () => {
      const it = byId(openId);
      if (!it) return;
      it.note = note.value.slice(0, MAX_NOTE);
      decorate(it);
      saveSoon();
      refresh();
    });
    penBox.addEventListener("change", () => {
      pen = penBox.checked;
      store.set(PEN_KEY, pen ? "1" : "0");
      refresh();
    });
    // 창 크기가 바뀌면 상자의 자리가 어긋난다. 닫아 둔다(메모는 이미 저장되어 있다).
    window.addEventListener("resize", () => { hidePop(); closeCard(); });
    window.addEventListener("pagehide", () => { if (saveTimer) save(); });
  }

  function init() {
    root = document.querySelector("main");
    if (!root || document.querySelector(".anno-ui")) return;
    load();
    buildUI();
    items.forEach((it) => { if (!paint(it)) lost.add(it.id); });
    refresh();
    bind();
    // 늦게 그려지는 부분(위젯, 수식)에 칠한 것은 한 번 더 찾아본다
    if (lost.size) setTimeout(() => {
      lost.forEach((id) => { const it = byId(id); if (it && paint(it)) lost.delete(id); });
      refresh();
    }, 1500);
  }

  /* 수식이 다 그려진 뒤에 시작한다: KaTeX(math.js)는 DOMContentLoaded 에서, MathJax 는 startup.promise 에서 끝난다 */
  function start() {
    const mj = window.MathJax && window.MathJax.startup && window.MathJax.startup.promise;
    if (mj && typeof mj.then === "function") mj.then(init, init);
    else init();
  }
  if (document.readyState === "complete") start();
  else window.addEventListener("load", start);
})();
