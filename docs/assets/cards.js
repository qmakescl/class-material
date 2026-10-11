/* materials.js의 목록을 카드로 그린다.
   <div class="card-grid" data-subject-list="statistics" data-base="./" data-limit="3">
   - data-base: 이 페이지에서 docs/ 루트로 가는 상대 경로 ("./" 또는 "../")
   - data-limit: 최근 N개만 표시(생략하면 전부). 항상 최신순.
   항목에 parts가 있으면 한 카드 안에 편마다 링크(.card-part)를 나누어 그린다.
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
      // 여러 편을 묶은 자료(parts)는 카드 전체를 링크로 만들지 않고 편마다 링크를 둔다.
      const parts = Array.isArray(item.parts) ? item.parts : [];
      const card = make(parts.length ? "article" : "a", parts.length ? "material-card has-parts" : "material-card");
      if (!parts.length) card.href = base + item.href;

      const body = make("div");
      body.append(
        make("p", "card-label", `${item.label} · ${item.date}`),
        make("h3", "", item.title),
        make("p", "", item.description)
      );
      // 직접 해 보는 실습 절이 있는 자료는 배지로 표시한다(카드 전체가 링크라 별도 링크는 두지 않는다).
      if (item.practice) body.append(make("span", "card-badge", "실습 포함"));

      card.append(make("span", "card-number", item.number), body);
      if (parts.length) {
        const list = make("div", "card-parts");
        parts.forEach((part, i) => {
          const link = make("a", "card-part");
          link.href = base + part.href;
          link.append(
            make("span", "card-part-label", `${i + 1} · ${part.label}`),
            make("span", "card-part-title", part.title),
            make("span", "card-part-go", "바로가기 →")
          );
          list.append(link);
        });
        card.append(list);
      } else {
        card.append(make("span", "card-status", "바로가기 →"));
      }
      grid.append(card);
    });

    grid.hidden = false;
    const empty = grid.parentElement.querySelector(".section-empty");
    if (empty) empty.remove();
    const count = grid.parentElement.querySelector("[data-total]");
    if (count) count.textContent = `전체 ${items.length}개`;
  });
})();
