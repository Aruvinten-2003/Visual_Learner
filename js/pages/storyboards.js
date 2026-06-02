(function () {
  function renderStoryboards() {
    const state = window.VisualLearnerStore.loadState();
    const storyboard = state.storyboards[0];
    const list = document.querySelector(".review-list");
    const sceneRow = document.querySelector(".scene-row");
    const heading = document.querySelector("#storyboard-title");
    const confidence = document.querySelector(".confidence");
    const previewCanvas = document.querySelector(".preview-canvas");

    if (!storyboard) {
      if (heading) heading.textContent = "No storyboard yet";
      if (confidence) confidence.textContent = "0%";
      if (list) list.innerHTML = '<div class="empty-state">Generate a preview to create storyboard scenes.</div>';
      if (sceneRow) sceneRow.innerHTML = "";
      if (previewCanvas) {
        previewCanvas.innerHTML = `
          <div class="preview-video-card empty">
            <p class="eyebrow">Waiting for preview</p>
            <strong>No scenes created yet</strong>
            <span>Generate a preview from uploaded notes to fill this storyboard.</span>
          </div>
        `;
      }
      return;
    }

    if (heading) heading.textContent = storyboard.lessonTitle;
    if (confidence) confidence.textContent = `${storyboard.confidence}%`;

    if (list) {
      list.innerHTML = storyboard.scenes
        .map(
          (scene, index) => `
            <article class="review-item ${index < 2 ? "approved" : "warning"}">
              <span class="dot"></span>
              <div>
                <strong>${scene.sceneId} ${scene.title}</strong>
                <p>${scene.narration}</p>
              </div>
            </article>
          `
        )
        .join("");
    }

    if (sceneRow) {
      sceneRow.innerHTML = storyboard.scenes
        .map(
          (scene, index) => `
            <article class="scene-card ${index === 0 ? "active" : ""}">
              <span>${scene.sceneId}</span>
              <strong>${scene.sceneType}</strong>
            </article>
          `
        )
        .join("");
    }

    if (previewCanvas) {
      previewCanvas.innerHTML = `
        <div class="preview-video-card">
          <p class="eyebrow">${storyboard.subject}</p>
          <strong>${storyboard.lessonTitle}</strong>
          <span>${storyboard.scenes.length} scenes ready for preview review.</span>
        </div>
      `;
    }
  }

  document.addEventListener("DOMContentLoaded", renderStoryboards);
})();
