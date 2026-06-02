(function () {
  let selectedSubject = "All";

  function subjectClass(subject) {
    if (subject === "Mathematics") return "math";
    if (subject === "Biology") return "biology";
    if (subject === "Computer Science") return "code";
    return "physics";
  }

  function assetUrl(path) {
    return path ? new URL(`/${path.replace(/^\/+/, "")}`, window.location.origin).href : "";
  }

  function renderLibrary() {
    const state = window.VisualLearnerStore.loadState();
    const grid = document.querySelector(".asset-grid");

    if (!grid) {
      return;
    }

    const videos = selectedSubject === "All"
      ? state.library
      : state.library.filter((video) => video.subject === selectedSubject);

    grid.innerHTML = videos.length
      ? videos
          .map(
            (video) => `
          <article class="asset-card" data-subject="${video.subject}">
            <div class="asset-thumb ${subjectClass(video.subject)}">${video.label}</div>
            <div>
              <strong>${video.title}</strong>
              <p>${video.subject} - ${video.description}</p>
              ${
                video.previewPath
                  ? `<a class="primary-link" href="${assetUrl(video.previewPath)}" target="_blank" rel="noreferrer">Open lesson preview</a>`
                  : ""
              }
              ${
                video.videoPath
                  ? `<a class="secondary-link" href="${assetUrl(video.videoPath)}" target="_blank" rel="noreferrer">Direct MP4</a>`
                  : ""
              }
            </div>
          </article>
        `
          )
          .join("")
      : '<div class="empty-state">No preview videos in the library yet.</div>';
  }

  function bindFilters() {
    const filterButton = Array.from(document.querySelectorAll("button")).find(
      (button) => button.textContent.trim() === "Filter"
    );
    const subjects = ["All", "Physics", "Mathematics", "Biology", "Computer Science"];
    let index = 0;

    filterButton?.addEventListener("click", () => {
      index = (index + 1) % subjects.length;
      selectedSubject = subjects[index];
      filterButton.textContent = `Filter: ${selectedSubject}`;
      renderLibrary();
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    renderLibrary();
    bindFilters();
  });
})();
