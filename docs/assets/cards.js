/* materials.js의 목록을 카드로 그린다.
   <div class="card-grid" data-subject-list="statistics" data-base="./" data-limit="3">
   - data-base: 이 페이지에서 docs/ 루트로 가는 상대 경로 ("./" 또는 "../")
   - data-limit: 최근 N개만 표시(생략하면 전부). 항상 최신순.
   자료가 하나도 없으면 grid는 숨겨 두고 옆의 .section-empty 안내를 그대로 둔다. */
(() => {
  const all = window.MATERIALS || [];

  document.querySelectorAll("[data-subject-list]").forEach((grid) => {
    const subject = grid.dataset.subjectList;
    const base = grid.dataset.base || "./";
    const limit = Number(grid.dataset.limit) || Infinity;

    // 발행 순서(오래된 것 = 01)를 번호로 쓰고, 표시는 최신순으로 뒤집는다.
    const items = all
      .map((item, index) => ({ ...item, index }))
      .filter((item) => item.subject === subject)
      .sort((a, b) => a.date.localeCompare(b.date) || a.index - b.index)
      .map((item, order) => ({ ...item, number: String(order + 1).padStart(2, "0") }))
      .reverse();

    if (!items.length) return;

    const make = (tag, className, text) => {
      const el = document.createElement(tag);
      if (className) el.className = className;
      if (text !== undefined) el.textContent = text;
      return el;
    };

    items.slice(0, limit).forEach((item) => {
      const card = make("a", "material-card");
      card.href = base + item.href;

      const body = make("div");
      body.append(
        make("p", "card-label", `${item.label} · ${item.date}`),
        make("h3", "", item.title),
        make("p", "", item.description)
      );

      card.append(make("span", "card-number", item.number), body, make("span", "card-status", "바로가기 →"));
      grid.append(card);
    });

    grid.hidden = false;
    const empty = grid.parentElement.querySelector(".section-empty");
    if (empty) empty.remove();
    const count = grid.parentElement.querySelector("[data-total]");
    if (count) count.textContent = `전체 ${items.length}개`;
  });
})();
