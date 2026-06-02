# Visual Learner

Visual Learner is an AI-assisted STEM learning website that converts theory, notes, and uploaded learning material into visual lesson previews. The goal is to support learners with learning disabilities by turning text-heavy STEM content into clearer visual explanations, storyboards, transcripts, and preview videos.

## Current Status

This project currently includes:

- FastAPI backend.
- MongoDB integration using Motor and Beanie.
- Static HTML/CSS/JavaScript frontend.
- File/text upload flow.
- Dynamic storyboard and preview generation.
- MP4 preview video generation using OpenCV and FFmpeg.
- Transcript and preview HTML generation.
- Tests for schemas, services, MongoDB health, AI provider wrapper, and video preview generation.

Important limitation: the current MP4 is an MVP preview video. Full production-quality Manim animation, real AI narration, TTS audio, and final video assembly are planned next-stage pipeline features.

## Technology Stack

- Backend: Python, FastAPI, Pydantic
- Database: MongoDB
- ODM: Beanie
- MongoDB driver: Motor
- Frontend: HTML, CSS, JavaScript
- Video preview: OpenCV, FFmpeg
- OCR/extraction support: PyMuPDF, pdfplumber, pytesseract, Pillow
- AI services: OpenAI-ready
- Background jobs: Celery + Redis-ready
- Testing: pytest, ruff

## Project Structure

```text
visual-learner/
├── app/
│   ├── api/                 # FastAPI routes
│   ├── core/                # Config and database setup
│   ├── models/              # MongoDB Beanie document models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # AI, OCR, rendering, TTS, video services
│   ├── utils/               # Shared file/path helpers
│   ├── workers/             # Celery app and task stubs
│   └── main.py              # FastAPI app entry point
├── assets/
│   ├── audio/               # Generated audio
│   ├── images/              # Generated images
│   ├── temp/                # Uploaded/temp files
│   └── videos/              # Generated preview videos and HTML pages
├── docs/                    # Architecture notes and class diagrams
├── frontend/
│   ├── css/                 # Website styling
│   ├── js/                  # Frontend JavaScript and page controllers
│   └── pages/               # Website pages
├── tests/                   # Automated backend/service tests
├── docker-compose.yml       # MongoDB and Redis containers
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Ruff/test config
├── .env.example             # Example environment file
└── README.md
```

## Requirements

Install these before running the project:

- Python 3.13
- MongoDB, either local install or Docker container
- FFmpeg
- Tesseract OCR, optional but useful for image/PDF OCR
- Docker Desktop, optional if you want Docker MongoDB/Redis

## Environment Setup

From the project folder:

```powershell
cd "C:\Users\ARUVINTEN RAMANATAHN\Dropbox\visual-learner"
```

Create and activate the Python virtual environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Environment Variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Recommended local values:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=visual_learner
OPENAI_API_KEY=your_real_openai_key_here
OPENAI_MODEL=gpt-4.1-mini
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
```

Do not put your OpenAI API key in frontend JavaScript. Keep it in `.env` only.

## Start MongoDB

Option 1: Use Docker Desktop:

```powershell
cd "C:\Users\ARUVINTEN RAMANATAHN\Dropbox\visual-learner"
docker compose up -d mongodb
```

Optional Redis:

```powershell
docker compose up -d redis
```

Check containers:

```powershell
docker ps
```

Option 2: Use a locally installed MongoDB service. Make sure MongoDB is listening on:

```text
localhost:27017
```

Redis is not required for the current preview flow. It is mainly for future background render jobs.

## Run The Website

Use two PowerShell windows.

### Terminal 1: Backend

```powershell
cd "C:\Users\ARUVINTEN RAMANATAHN\Dropbox\visual-learner"
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Keep this terminal open.

Backend URLs:

```text
http://127.0.0.1:8001/health
http://127.0.0.1:8001/health/mongodb
```

Open those URLs in the browser, or test from PowerShell:

```powershell
Invoke-WebRequest http://127.0.0.1:8001/health
Invoke-WebRequest http://127.0.0.1:8001/health/mongodb
```

### Terminal 2: Frontend

```powershell
cd "C:\Users\ARUVINTEN RAMANATAHN\Dropbox\visual-learner"
python -m http.server 5500
```

Keep this terminal open.

Open the website:

```text
http://127.0.0.1:5500/frontend/pages/index.html
```

## How To Generate A Preview Video

1. Open the website.
2. Go to `New video`.
3. Paste STEM notes or upload a text/PDF/image file.
4. Select the subject.
5. Click `Generate preview`.
6. Use `Open lesson preview` to view the generated lesson page.

Generated files are saved in:

```text
assets/videos/
```

The generated output usually includes:

```text
example-topic-xxxxxxx.mp4
example-topic-xxxxxxx.html
example-topic-xxxxxxx-transcript.txt
```

Open the `.html` file first because it embeds the generated MP4 inside a lesson preview page. Opening the raw `.mp4` directly shows the browser's plain black video-player page.

## Clear Old Website Data

If you still see old demo data such as Newton, Quadratic, Photosynthesis, or old Chemistry files, clear browser localStorage.

Open browser Console and run:

```js
localStorage.removeItem("visualLearnerState");
location.reload();
```

Then generate a new preview again.

Old generated videos do not update automatically. If you open an old file name, you will still see the old video. Generate a new preview and open the new `.html` preview page.

## Test The Project

Activate the virtual environment first:

```powershell
cd "C:\Users\ARUVINTEN RAMANATAHN\Dropbox\visual-learner"
.\.venv\Scripts\Activate.ps1
```

Run all tests:

```powershell
python -m pytest
```

Run tests quietly:

```powershell
python -m pytest -q
```

Run Ruff:

```powershell
python -m ruff check app tests
```

Check frontend JavaScript syntax:

```powershell
Get-ChildItem -Path ".\frontend\js" -Recurse -Filter *.js | ForEach-Object { node --check $_.FullName }
```

Expected result:

```text
25 passed
All checks passed!
```

## Live API Smoke Test

With the backend running on port `8001`, you can test video preview generation from PowerShell:

```powershell
$samplePath = "assets\temp\sample-notes.txt"
Set-Content -Path $samplePath -Value "Chemistry studies matter, atoms, molecules, and chemical reactions."

curl.exe -X POST "http://127.0.0.1:8001/videos/preview" `
  -F "title=Chemistry matter and reactions" `
  -F "subject=Chemistry" `
  -F "input_type=text" `
  -F "notes=" `
  -F "file=@$samplePath;type=text/plain"
```

The response should include:

```json
"status": "preview_created"
```

It should also return paths for:

```text
video_path
preview_path
transcript_path
```

## Important Local URLs

```text
Frontend:
http://127.0.0.1:5500/frontend/pages/index.html

Backend health:
http://127.0.0.1:8001/health

MongoDB health:
http://127.0.0.1:8001/health/mongodb
```

## Troubleshooting

### `uvicorn` is not recognized

Use:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### `Unable to connect to the remote server`

The backend is not running. Start it:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### Port `8000` gives `WinError 10013`

Use port `8001`. The frontend config is set to use:

```text
http://127.0.0.1:8001
```

### `no configuration file provided`

You ran Docker from the wrong folder. Run:

```powershell
cd "C:\Users\ARUVINTEN RAMANATAHN\Dropbox\visual-learner"
docker compose up -d mongodb
```

### Docker image pull fails with `EOF`

Docker Desktop is running, but the image download failed. Retry:

```powershell
docker compose pull mongodb
docker compose up -d mongodb
```

If it still fails, restart Docker Desktop or change network/VPN.

### Website shows old data

Run this in the browser Console:

```js
localStorage.removeItem("visualLearnerState");
location.reload();
```

### Video looks old or wrong

You are probably opening an older generated MP4. Generate a new preview and open the new `.html` preview page from `assets/videos/`.

## Notes For Development

- Backend routes are in `app/api/routes.py`.
- MongoDB models are in `app/models/`.
- Schemas are in `app/schemas/`.
- Preview video generation is in `app/services/video/preview_generator.py`.
- Frontend page behavior is in `frontend/js/pages/`.
- Shared frontend state is in `frontend/js/storage.js`.
- API base URL is in `frontend/js/config.js`.

## Next Development Steps

- Add real AI lesson planning from OpenAI.
- Add high-quality Manim scene rendering.
- Add TTS narration audio.
- Add final video assembly with audio and captions.
- Add user accounts and saved project APIs.
- Add frontend upload progress and backend job polling.
