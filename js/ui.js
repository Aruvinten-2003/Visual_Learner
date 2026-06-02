(function () {
  function showToast(message, type = "info") {
    let toast = document.querySelector("[data-toast]");

    if (!toast) {
      toast = document.createElement("div");
      toast.dataset.toast = "";
      toast.className = "toast";
      document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.dataset.type = type;
    toast.classList.add("visible");

    window.clearTimeout(showToast.hideTimer);
    showToast.hideTimer = window.setTimeout(() => {
      toast.classList.remove("visible");
    }, 3200);
  }

  function setActiveNavigation() {
    const currentPage = window.location.pathname.split("/").pop() || "index.html";

    document.querySelectorAll(".nav-item").forEach((item) => {
      const itemPage = item.getAttribute("href");
      item.classList.toggle("active", itemPage === currentPage);
    });
  }

  function updateSidebarJob() {
    const job = window.VisualLearnerStore.getCurrentJob();
    const panel = document.querySelector(".sidebar-panel");

    if (!panel) {
      return;
    }

    const title = panel.querySelector("h2");
    const meter = panel.querySelector(".mini-meter span");
    const status = panel.querySelector(".muted");

    if (!job) {
      if (title) title.textContent = "No active preview";
      if (meter) meter.style.width = "0%";
      if (status) status.textContent = "Upload notes and generate a preview.";
      return;
    }

    if (title) title.textContent = job.title;
    if (meter) meter.style.width = `${job.progress}%`;
    if (status) status.textContent = job.step;
  }

  async function updateApiStatus() {
    const topbarActions = document.querySelector(".topbar-actions");

    if (!topbarActions) {
      return;
    }

    let status = document.querySelector("[data-api-status]");

    if (!status) {
      status = document.createElement("button");
      status.type = "button";
      status.className = "api-status";
      status.dataset.apiStatus = "";
      status.textContent = "API checking";
      topbarActions.prepend(status);
    }

    try {
      const [apiHealth, mongoHealth] = await Promise.all([
        window.VisualLearnerAPI.getHealth(),
        window.VisualLearnerAPI.getMongoHealth()
      ]);

      const mongoReady = Boolean(mongoHealth.ready);
      status.textContent = mongoReady ? "API + MongoDB online" : "API online";
      status.dataset.state = mongoReady ? "online" : "warning";
      status.title = mongoReady ? "MongoDB is connected" : apiHealth.mongodb?.error || "MongoDB is not ready";
    } catch (error) {
      status.textContent = "API offline";
      status.dataset.state = "offline";
      status.title = error.message;
    }
  }

  function bindGlobalButtons() {
    document.querySelectorAll(".secondary-button, .primary-button, .primary-link").forEach((button) => {
      if (button.dataset.boundGlobal) {
        return;
      }

      button.dataset.boundGlobal = "true";

      if (button.tagName === "A") {
        return;
      }

      button.addEventListener("click", () => {
        if (!button.dataset.silent) {
          showToast(`${button.textContent.trim()} selected`);
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    setActiveNavigation();
    updateSidebarJob();
    updateApiStatus();
    bindGlobalButtons();
  });

  window.VisualLearnerUI = {
    showToast,
    updateApiStatus,
    updateSidebarJob
  };
})();
