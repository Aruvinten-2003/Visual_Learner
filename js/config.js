(function () {
  const defaultApiBaseUrl = "http://127.0.0.1:8001";
  const savedApiBaseUrl = localStorage.getItem("visualLearnerApiBaseUrl");

  function normalizeApiBaseUrl(value) {
    if (!value) {
      return defaultApiBaseUrl;
    }

    const trimmedValue = value.trim().replace(/\/+$/, "");

    try {
      const url = new URL(trimmedValue);
      const isLegacyLocalPort =
        (url.hostname === "127.0.0.1" || url.hostname === "localhost") &&
        url.port === "8000";

      if (isLegacyLocalPort) {
        return defaultApiBaseUrl;
      }

      return url.origin;
    } catch {
      return defaultApiBaseUrl;
    }
  }

  const apiBaseUrl = normalizeApiBaseUrl(savedApiBaseUrl);

  if (savedApiBaseUrl !== apiBaseUrl) {
    localStorage.setItem("visualLearnerApiBaseUrl", apiBaseUrl);
  }

  window.VisualLearnerConfig = {
    apiBaseUrl,
    storageKey: "visualLearnerState"
  };
})();
