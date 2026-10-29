const themeButton = document.querySelector("#theme");
themeButton.addEventListener("click", () => {
  const light = document.documentElement.dataset.theme !== "light";
  document.documentElement.dataset.theme = light ? "light" : "dark";
  themeButton.innerHTML = light ? "☾ <span>Dark</span>" : "☀ <span>Light</span>";
  themeButton.setAttribute("aria-label", `Switch to ${light ? "dark" : "light"} theme`);
});

const dialog = document.querySelector("#browse-dialog");
document.querySelector("#browse")?.addEventListener("click", () => dialog.showModal());
document.querySelector("#close-browse").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});

const search = document.querySelector("#search");
const filters = [...document.querySelectorAll("[data-filter]")];
const cards = [...document.querySelectorAll(".collection-section .content-card")];
let moduleFilter = "all";

function filterCollections() {
  const term = search.value.trim().toLowerCase();
  let visible = 0;
  for (const card of cards) {
    card.hidden = !((moduleFilter === "all" || card.dataset.module === moduleFilter)
      && card.dataset.search.includes(term));
    if (!card.hidden) visible++;
  }
  document.querySelector("#result-count").textContent = `${visible} collection${visible === 1 ? "" : "s"} to explore`;
  document.querySelector("#empty").hidden = visible !== 0;
}

if (search) {
  search.addEventListener("input", filterCollections);
  for (const filter of filters) {
    filter.addEventListener("click", () => {
      moduleFilter = filter.dataset.filter;
      for (const button of filters) {
        const selected = button === filter;
        button.classList.toggle("active", selected);
        button.setAttribute("aria-pressed", String(selected));
      }
      filterCollections();
    });
  }
}
