(function () {
  function statusClass(status) {
    return ["Complete", "Rendering", "Preview"].includes(status) ? "status-pill ready" : "status-pill";
  }

  function renderProjects() {
    const state = window.VisualLearnerStore.loadState();
    const list = document.querySelector(".table-list");
    const statCards = document.querySelectorAll(".stat-card strong");

    if (!list) {
      return;
    }

    list.innerHTML = state.projects.length
      ? state.projects
          .map(
            (project) => `
          <article class="table-row">
            <div>
              <strong>${project.title}</strong>
              <p>${project.subject} - ${project.source} - ${project.scenes} scenes</p>
            </div>
            <span class="${statusClass(project.status)}">${project.status}</span>
          </article>
        `
          )
          .join("")
      : '<div class="empty-state">No projects yet. Create a preview from the New video page.</div>';

    if (statCards.length >= 4) {
      statCards[0].textContent = state.projects.filter((project) => project.status !== "Complete").length;
      statCards[1].textContent = state.projects.filter((project) => project.status === "Review").length;
      statCards[2].textContent = state.projects.filter((project) => project.status === "Complete").length;
      statCards[3].textContent = new Set(state.projects.map((project) => project.subject)).size;
    }
  }

  document.addEventListener("DOMContentLoaded", renderProjects);
})();
