(function () {
  function renderJobs(jobs = window.VisualLearnerStore.loadState().renderJobs) {
    const list = document.querySelector(".job-list");
    const queueStatus = document.querySelector(".page-panel .status-pill");

    if (!list) {
      return;
    }

    if (queueStatus) {
      const runningCount = jobs.filter((job) => job.status === "running").length;
      queueStatus.textContent = `${runningCount} running`;
      queueStatus.classList.toggle("ready", runningCount > 0);
    }

    list.innerHTML = jobs.length
      ? jobs
          .map(
            (job) => `
          <article class="job-card">
            <div class="job-header">
              <div>
                <strong>${job.title}</strong>
                <p>${job.step}</p>
              </div>
              <span>${job.progress}%</span>
            </div>
            <div class="mini-meter"><span style="width: ${job.progress}%"></span></div>
          </article>
        `
          )
          .join("")
      : '<div class="empty-state">No render jobs yet. Generate a preview first.</div>';
  }

  function bindRefresh() {
    const refreshButton = Array.from(document.querySelectorAll("button")).find(
      (button) => button.textContent.trim() === "Refresh status"
    );

    refreshButton?.addEventListener("click", () => {
      const jobs = window.VisualLearnerStore.advanceRenderJobs();
      renderJobs(jobs);
      window.VisualLearnerUI.updateSidebarJob();
      window.VisualLearnerUI.showToast("Render job progress updated", "success");
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    renderJobs();
    bindRefresh();
  });
})();
