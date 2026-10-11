/* 수식 렌더링 (KaTeX, docs/assets/katex/ 에 포함).
   - 인라인 수식: \( ... \)   /   블록 수식: \[ ... \]
   - HTML 본문뿐 아니라 JS가 나중에 넣는 텍스트/innerHTML 도 자동으로 렌더링한다.
   - SVG <text> 안에서는 수식 구분자를 쓰지 않는다(유니코드 글자를 그대로 쓴다). */
(() => {
  const options = {
    delimiters: [
      { left: "\\[", right: "\\]", display: true },
      { left: "\\(", right: "\\)", display: false }
    ],
    ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code", "option", "text", "tspan"],
    throwOnError: false
  };

  const hasMath = (s) => s.includes("\\(") || s.includes("\\[");

  const render = (el) => {
    if (el && el.nodeType === 1 && typeof window.renderMathInElement === "function") {
      window.renderMathInElement(el, options);
    }
  };

  const start = () => {
    render(document.body);

    // JS가 바꾼 부분만 다시 렌더링한다. 렌더 결과에는 구분자가 없어 무한 루프가 생기지 않는다.
    const pending = new Set();
    let scheduled = false;
    const flush = () => {
      scheduled = false;
      const targets = Array.from(pending);
      pending.clear();
      targets.forEach((el) => { if (el.isConnected) render(el); });
    };
    const queue = (node) => {
      const el = node.nodeType === 1 ? node : node.parentElement;
      // 코드 안(ignoredTags)과 형광펜 화면 조각은 건너뛴다. 형광펜(annotate.js)이 코드의 글을 <mark> 로
      // 감싸거나 풀 때도 변화가 생기는데, 그때 코드 속의 \( \) 를 수식으로 읽으면 안 된다.
      if (!el || el.closest(".katex, pre, code, textarea, .anno-ui")) return;
      pending.add(el);
      if (!scheduled) { scheduled = true; requestAnimationFrame(flush); }
    };

    new MutationObserver((mutations) => {
      mutations.forEach((m) => {
        if (m.type === "characterData") {
          if (hasMath(m.target.data)) queue(m.target);
        } else {
          m.addedNodes.forEach((n) => { if (hasMath(n.textContent || "")) queue(n); });
        }
      });
    }).observe(document.body, { childList: true, subtree: true, characterData: true });
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
