(function () {
  async function request(path, options = {}) {
    const baseUrl = window.VisualLearnerConfig.apiBaseUrl;
    const isFormData = options.body instanceof FormData;
    const response = await fetch(`${baseUrl}${path}`, {
      headers: isFormData
        ? options.headers || {}
        : {
            "Content-Type": "application/json",
            ...(options.headers || {})
          },
      ...options
    });

    let body = null;
    const text = await response.text();

    if (text) {
      try {
        body = JSON.parse(text);
      } catch {
        body = { message: text };
      }
    }

    if (!response.ok) {
      const message = body?.detail || body?.message || `Request failed with ${response.status}`;
      throw new Error(message);
    }

    return body;
  }

  async function getHealth() {
    return request("/health");
  }

  async function getMongoHealth() {
    return request("/health/mongodb");
  }

  async function createVideoPreview(formData) {
    return request("/videos/preview", {
      method: "POST",
      body: formData
    });
  }

  window.VisualLearnerAPI = {
    createVideoPreview,
    getHealth,
    getMongoHealth,
    request
  };
})();
