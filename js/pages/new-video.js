(function () {
  let selectedFile = null;

  function getActiveInputType() {
    return document.querySelector(".source-tabs .tab.active")?.textContent.trim().toLowerCase() || "text";
  }

  function getPreviewUrl(path) {
    return new URL(`/${path.replace(/^\/+/, "")}`, window.location.origin).href;
  }

  function setFlowProgress(activeIndex) {
    document.querySelectorAll(".flow-step").forEach((step, index) => {
      step.classList.toggle("complete", index < activeIndex);
      step.classList.toggle("active", index === activeIndex);
    });
  }

  function updateReviewFromNotes() {
    const notes = document.querySelector("#notes");
    const subject = document.querySelector("#subject");
    const reviewItems = document.querySelectorAll(".review-item p");
    const confidence = document.querySelector(".confidence");

    if (!notes || !subject || reviewItems.length < 3) {
      return;
    }

    const text = notes.value.trim();
    const words = text.split(/\s+/).filter(Boolean);
    const formulaMatch = text.match(/[A-Za-z]\s*=\s*[^.]+/);
    const hasFile = Boolean(selectedFile);

    reviewItems[0].textContent =
      words.length > 8
        ? `${subject.value} notes detected with ${words.length} words.`
        : hasFile
          ? `${selectedFile.name} is ready to send to the backend.`
          : "Add notes or upload a file to generate a preview.";
    reviewItems[1].textContent = formulaMatch ? formulaMatch[0].trim() : "No formula detected yet.";
    reviewItems[2].textContent = "Generate preview to create storyboard scenes and a preview package.";

    if (confidence) {
      confidence.textContent = words.length > 0 || hasFile ? `${Math.min(98, Math.max(55, words.length * 3))}%` : "0%";
    }
  }

  function updateReviewFromPreview(payload) {
    const reviewItems = document.querySelectorAll(".review-item");
    const confidence = document.querySelector(".confidence");
    const scriptCard = document.querySelector(".script-card");
    const formulas = payload.lesson.formulas.length ? payload.lesson.formulas.join(", ") : "No formula detected.";

    if (reviewItems.length >= 3) {
      reviewItems[0].querySelector("p").textContent = payload.lesson.key_concepts.join(", ");
      reviewItems[1].querySelector("p").textContent = formulas;
      reviewItems[2].querySelector("p").textContent = `${payload.storyboard.scenes.length} storyboard scenes created.`;
    }

    if (confidence) {
      confidence.textContent = `${payload.lesson.confidence}%`;
    }

    if (scriptCard) {
      scriptCard.querySelector("p:last-child").textContent = payload.lesson.summary;
    }
  }

  function updateVisualPreview(payload) {
    const statusPill = document.querySelector(".visual-panel .status-pill");
    const previewCanvas = document.querySelector(".preview-canvas");
    const sceneRow = document.querySelector(".scene-row");
    const videoUrl = getPreviewUrl(payload.video.video_path);
    const previewUrl = getPreviewUrl(payload.video.preview_path);
    const transcriptUrl = getPreviewUrl(payload.video.transcript_path);

    if (statusPill) {
      statusPill.textContent = "Preview created";
      statusPill.classList.add("ready");
    }

    if (previewCanvas) {
      previewCanvas.innerHTML = `
        <div class="preview-video-card">
          <p class="eyebrow">Generated preview</p>
          <strong>${payload.video.title}</strong>
          <span>${Math.round(payload.video.duration_seconds)} seconds of storyboard narration</span>
          <div class="generated-links">
            <a class="primary-link" href="${previewUrl}" target="_blank" rel="noreferrer">Open lesson preview</a>
            <a class="secondary-link" href="${videoUrl}" target="_blank" rel="noreferrer">Direct MP4</a>
            <a class="secondary-link" href="${transcriptUrl}" target="_blank" rel="noreferrer">Transcript</a>
          </div>
        </div>
      `;
    }

    if (sceneRow) {
      sceneRow.innerHTML = payload.storyboard.scenes
        .map(
          (scene, index) => `
            <article class="scene-card ${index === 0 ? "active" : ""}">
              <span>${scene.scene_id}</span>
              <strong>${scene.title}</strong>
            </article>
          `
        )
        .join("");
    }
  }

  function bindInputTabs() {
    const tabs = document.querySelectorAll(".source-tabs .tab");
    const uploadZone = document.querySelector(".upload-zone");
    const notes = document.querySelector("#notes");

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((item) => item.classList.remove("active"));
        tab.classList.add("active");

        const type = tab.textContent.trim();
        if (uploadZone) {
          uploadZone.querySelector("span").textContent =
            type === "Text" ? "Optional PDF, image, or handwriting sample" : `Select a ${type.toLowerCase()} file`;
        }

        if (notes && type !== "Text") {
          notes.placeholder = `Add context for the ${type.toLowerCase()} upload here.`;
        }
      });
    });
  }

  function bindUploadZone() {
    const uploadZone = document.querySelector(".upload-zone");

    if (!uploadZone) {
      return;
    }

    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".txt,.md,.csv,.pdf,image/*";
    input.hidden = true;
    uploadZone.appendChild(input);

    uploadZone.setAttribute("role", "button");
    uploadZone.setAttribute("tabindex", "0");

    uploadZone.addEventListener("click", () => input.click());
    uploadZone.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        input.click();
      }
    });

    input.addEventListener("change", () => {
      selectedFile = input.files[0] || null;
      if (!selectedFile) return;
      uploadZone.classList.add("has-file");
      uploadZone.querySelector("strong").textContent = selectedFile.name;
      uploadZone.querySelector("span").textContent = `${Math.round(selectedFile.size / 1024)} KB selected`;
      updateReviewFromNotes();
    });
  }

  function collectForm() {
    const notes = document.querySelector("#notes");
    const subject = document.querySelector("#subject");
    const firstSentence = notes?.value.trim().split(/[.!?]/)[0] || "";
    const fileTitle = selectedFile?.name.replace(/\.[^.]+$/, "");
    const shortNoteTitle = firstSentence
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 7)
      .join(" ");

    return {
      title: shortNoteTitle.length > 8 ? shortNoteTitle : fileTitle || `${subject?.value || "STEM"} visual lesson`,
      subject: subject?.value || "Physics",
      inputType: getActiveInputType(),
      notes: notes?.value.trim() || "",
      file: selectedFile,
      fileName: selectedFile?.name || ""
    };
  }

  function buildPreviewFormData(form) {
    const formData = new FormData();
    formData.append("title", form.title);
    formData.append("subject", form.subject);
    formData.append("input_type", form.inputType);
    formData.append("notes", form.notes);

    if (form.file) {
      formData.append("file", form.file);
    }

    return formData;
  }

  function bindDraftActions() {
    const saveButton = Array.from(document.querySelectorAll("button")).find(
      (button) => button.textContent.trim() === "Save draft"
    );
    const generateButton = Array.from(document.querySelectorAll("button")).find(
      (button) => button.textContent.trim() === "Generate preview"
    );

    if (saveButton) {
      saveButton.dataset.silent = "true";
      saveButton.addEventListener("click", () => {
        const form = collectForm();
        window.VisualLearnerStore.createProjectFromForm(form);
        window.VisualLearnerUI.showToast("Draft saved to Projects", "success");
        window.VisualLearnerUI.updateSidebarJob();
      });
    }

    if (generateButton) {
      generateButton.dataset.silent = "true";
      generateButton.addEventListener("click", async () => {
        const form = collectForm();

        if (!form.notes && !form.file) {
          window.VisualLearnerUI.showToast("Add notes or upload a file first", "error");
          return;
        }

        generateButton.disabled = true;
        generateButton.textContent = "Generating...";
        setFlowProgress(2);

        try {
          const payload = await window.VisualLearnerAPI.createVideoPreview(buildPreviewFormData(form));
          window.VisualLearnerStore.createProjectFromPreview(payload);
          updateReviewFromPreview(payload);
          updateVisualPreview(payload);
          setFlowProgress(4);
          window.VisualLearnerUI.showToast("Preview package created", "success");
          window.VisualLearnerUI.updateSidebarJob();
        } catch (error) {
          setFlowProgress(1);
          window.VisualLearnerUI.showToast(error.message, "error");
        } finally {
          generateButton.disabled = false;
          generateButton.textContent = "Generate preview";
        }
      });
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindInputTabs();
    bindUploadZone();
    bindDraftActions();

    const notes = document.querySelector("#notes");
    const subject = document.querySelector("#subject");

    notes?.addEventListener("input", updateReviewFromNotes);
    subject?.addEventListener("change", updateReviewFromNotes);
  });
})();
