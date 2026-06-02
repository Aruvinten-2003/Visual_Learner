(function () {
  const key = window.VisualLearnerConfig.storageKey;
  const stateVersion = "20260601-preview";

  const emptyState = {
    version: stateVersion,
    projects: [],
    storyboards: [],
    renderJobs: [],
    library: []
  };

  const demoIds = new Set([
    "project-newton",
    "project-quadratic",
    "project-photosynthesis",
    "storyboard-newton",
    "job-newton",
    "job-quadratic",
    "job-photosynthesis",
    "video-newton",
    "video-quadratic",
    "video-photosynthesis",
    "video-binary"
  ]);

  function cloneEmptyState() {
    return structuredClone(emptyState);
  }

  function removeDemoEntries(state) {
    return {
      version: stateVersion,
      projects: state.projects.filter((item) => !demoIds.has(item.id)),
      storyboards: state.storyboards.filter((item) => !demoIds.has(item.id)),
      renderJobs: state.renderJobs.filter((item) => !demoIds.has(item.id)),
      library: state.library.filter((item) => !demoIds.has(item.id))
    };
  }

  function normalizeState(state) {
    const isOldState = state?.version !== stateVersion;
    const normalized = {
      ...cloneEmptyState(),
      ...state
    };

    normalized.projects = Array.isArray(normalized.projects) ? normalized.projects : [];
    normalized.storyboards = Array.isArray(normalized.storyboards) ? normalized.storyboards : [];
    normalized.renderJobs = Array.isArray(normalized.renderJobs) ? normalized.renderJobs : [];
    normalized.library = Array.isArray(normalized.library) ? normalized.library : [];

    const withoutDemo = removeDemoEntries(normalized);

    if (!isOldState) {
      return withoutDemo;
    }

    return {
      version: stateVersion,
      projects: withoutDemo.projects.filter((project) => project.status === "Preview"),
      storyboards: withoutDemo.storyboards.filter((storyboard) => storyboard.status === "Preview"),
      renderJobs: withoutDemo.renderJobs.filter((job) => job.status === "completed"),
      library: withoutDemo.library.filter((video) => video.videoPath || video.previewPath)
    };
  }

  function loadState() {
    const stored = localStorage.getItem(key);

    if (!stored) {
      return cloneEmptyState();
    }

    try {
      const state = normalizeState(JSON.parse(stored));
      saveState(state);
      return state;
    } catch {
      saveState(emptyState);
      return cloneEmptyState();
    }
  }

  function saveState(state) {
    localStorage.setItem(key, JSON.stringify(normalizeState(state)));
  }

  function getCurrentJob() {
    const state = loadState();
    return (
      state.renderJobs.find((job) => job.status === "running") ||
      state.renderJobs[0] ||
      null
    );
  }

  function createProjectFromForm(formData) {
    const state = loadState();
    const now = Date.now();
    const title = formData.title || `${formData.subject} learning video`;
    const projectId = `project-${now}`;
    const storyboardId = `storyboard-${now}`;

    const project = {
      id: projectId,
      title,
      subject: formData.subject,
      inputType: formData.inputType,
      status: "Draft",
      scenes: 0,
      source: formData.fileName || (formData.inputType === "text" ? "typed notes" : `${formData.inputType} upload`),
      updatedAt: "Just now"
    };

    state.projects.unshift(project);
    state.storyboards.unshift({
      id: storyboardId,
      lessonTitle: title,
      subject: formData.subject,
      confidence: 0,
      status: "Draft",
      scenes: []
    });

    saveState(state);
    return project;
  }

  function createProjectFromPreview(payload) {
    const state = loadState();
    const now = Date.now();
    const projectId = payload.ids?.document_id || `project-${now}`;
    const storyboardId = payload.ids?.storyboard_id || `storyboard-${now}`;
    const jobId = payload.ids?.render_job_id || `job-${now}`;
    const videoId = payload.ids?.video_id || `video-${now}`;
    const scenes = payload.storyboard?.scenes || [];

    const project = {
      id: projectId,
      title: payload.project.title,
      subject: payload.project.subject,
      inputType: payload.project.input_type,
      status: "Preview",
      scenes: scenes.length,
      source: payload.project.source,
      updatedAt: "Just now"
    };

    const storyboard = {
      id: storyboardId,
      lessonTitle: payload.storyboard.title,
      subject: payload.project.subject,
      confidence: payload.storyboard.confidence,
      status: "Preview",
      scenes: scenes.map((scene) => ({
        sceneId: scene.scene_id,
        sceneType: scene.scene_type,
        title: scene.title,
        narration: scene.narration_text,
        visualDescription: scene.visual_description
      }))
    };

    const renderJob = {
      id: jobId,
      title: payload.render_job.title,
      step: payload.render_job.step,
      progress: payload.render_job.progress,
      status: payload.render_job.status
    };

    const video = {
      id: videoId,
      title: payload.video.title,
      subject: payload.project.subject,
      label: payload.video.label,
      description: payload.video.description,
      videoPath: payload.video.video_path,
      previewPath: payload.video.preview_path,
      transcriptPath: payload.video.transcript_path
    };

    state.projects = [project, ...state.projects.filter((item) => item.id !== project.id)];
    state.storyboards = [storyboard, ...state.storyboards.filter((item) => item.id !== storyboard.id)];
    state.renderJobs = [renderJob, ...state.renderJobs.filter((item) => item.id !== renderJob.id)];
    state.library = [video, ...state.library.filter((item) => item.id !== video.id)];

    saveState(state);
    return project;
  }

  function advanceRenderJobs() {
    const state = loadState();

    state.renderJobs = state.renderJobs.map((job) => {
      if (job.status !== "running") {
        return job;
      }

      const nextProgress = Math.min(100, job.progress + 9);

      return {
        ...job,
        progress: nextProgress,
        step: nextProgress >= 100 ? "Completed" : job.step,
        status: nextProgress >= 100 ? "completed" : job.status
      };
    });

    saveState(state);
    return state.renderJobs;
  }

  window.VisualLearnerStore = {
    advanceRenderJobs,
    createProjectFromForm,
    createProjectFromPreview,
    getCurrentJob,
    loadState,
    saveState
  };
})();
