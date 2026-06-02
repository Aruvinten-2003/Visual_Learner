# Visual Learner Frontend

This frontend is a static HTML, CSS, and JavaScript interface.

## Structure

```text
frontend/
├── pages/
│   ├── index.html
│   ├── projects.html
│   ├── storyboards.html
│   ├── render-jobs.html
│   └── library.html
├── css/
│   └── styles.css
└── js/
    ├── config.js
    ├── api.js
    ├── storage.js
    ├── ui.js
    └── pages/
        ├── new-video.js
        ├── projects.js
        ├── storyboards.js
        ├── render-jobs.js
        └── library.js
```

## Run Locally

Open `frontend/pages/index.html` directly, or run a simple local server from the project root:

```powershell
python -m http.server 5500
```

Then open:

```text
http://127.0.0.1:5500/frontend/pages/index.html
```

The JavaScript checks the FastAPI backend at:

```text
http://127.0.0.1:8001
```
