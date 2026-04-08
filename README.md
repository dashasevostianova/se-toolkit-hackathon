# DailyEnglish 🇬🇧

A web application for learning one English word at a time, every 3 minutes.

## Features ✨

- **Auto-refresh** — new word every 3 minutes automatically
- **90 unique words** — with Russian translations and example sentences
- **Progress tracking** — visual progress bar with cycle counter
- **Beautiful dark UI** — animated gradients, responsive design
- **No repeats** — cycles through all words before repeating

## Quick Start 🚀

### Option 1: Docker (recommended)

```bash
# Build and run
docker compose up -d --build

# Open in browser
open http://localhost:5000

# Stop
docker compose down
```

### Option 2: Python

```bash
pip install -r requirements.txt
python app.py
```

## Deploy on VM

```bash
# Clone repo
git clone https://github.com/dashasevostianova/se-toolkit-hackathon.git
cd se-toolkit-hackathon

# Docker (recommended for production)
docker compose up -d --build

# Or Python
pip install -r requirements.txt
python app.py
```

## Project Structure 📁

```
├── app.py                 # Flask backend
├── vocabulary.py          # 90 words dictionary
├── templates/
│   └── index.html         # Frontend
├── static/
│   ├── style.css          # Dark theme styles
│   └── script.js          # Timer + auto-refresh logic
├── Dockerfile             # Docker image
├── docker-compose.yml     # Docker deployment
└── requirements.txt       # Dependencies
```

## Tech Stack 🛠️

- **Backend:** Flask (Python)
- **Frontend:** HTML/CSS/JS (no frameworks)
- **Deployment:** Docker + Docker Compose
