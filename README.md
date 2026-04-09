# DailyEnglish 🇬🇧

A web application that helps you learn one English word at a time — with translation, examples, and auto-refresh.

## Demo

**Running app:** http://10.93.25.94:5000

### Screenshots

**Main word card:**
- Shows the English word with emoji association
- Russian translation (hidden by default, click to reveal)
- Example sentence in context
- 3-minute countdown timer in the header

```
┌─────────────────────────────────────────┐
│  📚 DailyEnglish              🔴 3:00   │
├─────────────────────────────────────────┤
│                                         │
│   🌿  Resilient                         │
│                                         │
│  ────────────────────────────────       │
│                                         │
│  🇷🇺 Translation     [👁️ Show]          │
│  ████████████████ (blurred)             │
│                                         │
│  📝 Example                             │
│  │ Children are remarkably resilient.   │
│                                         │
│  ────────────────────────────────       │
│  📊 2 / 10           [Next Word →]      │
│                                         │
└─────────────────────────────────────────┘
```

**Settings panel (⚙️):**
- Choose daily limit: 10 words / 20 words / All 90 words
- Session progress bar
- Round counter (cycles through words)

## Product Context

### End Users

- Anyone from Russia who wants to learn and practice English every day
- Students, professionals, or casual learners
- Users who prefer lightweight tools without complex setup

### Problem

People want to learn new words regularly, but:
- Standard apps require manually opening them and searching for content
- They are overloaded with features that distract from learning
- No automatic reminders lead to irregular practice
- Motivation drops quickly without a simple, frictionless experience

### Our Solution

A minimal web app that serves **one new English word every 3 minutes** automatically. The user just opens the page — no login, no setup. Each word comes with a Russian translation (hidden by default for self-testing), an example sentence, and a visual emoji association. A daily word limit (10, 20, or all 90) lets users control their pace.

## Features

### ✅ Implemented

| Feature | Description |
|---------|-------------|
| **Auto-refresh** | New word every 3 minutes automatically |
| **Daily limit** | Choose 10, 20, or all 90 words per session |
| **Hidden translation** | Blurred by default — click "👁️ Show" to reveal |
| **Random order** | Words are shuffled each session, no memorization by order |
| **Reshuffle** | After all words in the pool are viewed, reshuffle automatically |
| **Progress tracking** | Mini progress bar on card + full stats section |
| **90-word dictionary** | Curated words with Russian translations and examples |
| **Responsive design** | Works on desktop and mobile |
| **Dark animated UI** | Modern dark theme with gradient backgrounds |
| **Session persistence** | Progress saved per browser session |

### ❌ Not Yet Implemented

| Feature | Description |
|---------|-------------|
| User accounts | Login, persistent progress across devices |
| Spaced repetition | Smart scheduling based on word difficulty |
| Audio pronunciation | Text-to-speech for each word |
| Word categories | Filter by topic (business, travel, etc.) |
| Quiz mode | Flashcard-style self-testing |
| Dark/light theme toggle | User-selectable theme |

## Usage

1. Open the app in your browser: `http://<server-ip>:5000`
2. A word appears automatically with emoji, translation (hidden), and example
3. Click **👁️ Show** to reveal the Russian translation
4. Click **Next Word** to get the next word manually
5. Click **⚙️** in the header to set your daily limit (10 / 20 / 90 words)
6. A new word appears automatically every 3 minutes
7. After completing your daily pool, words are reshuffled for a new round

## Deployment

### OS Requirements

- **Ubuntu 24.04 LTS** (same as university VMs)
- Works on any Linux distribution with Python 3.8+

### Prerequisites

The following must be installed on the VM:

```bash
# Python 3.8 or higher (Ubuntu 24.04 has Python 3.12 by default)
python3 --version

# pip (Python package manager)
apt install -y python3-pip

# python3-venv (virtual environment support)
apt install -y python3-venv

# git (for cloning the repository)
apt install -y git
```

### Step-by-Step Deployment

#### 1. Clone the repository

```bash
cd ~
git clone https://github.com/dashasevostianova/se-toolkit-hackathon.git DailyEnglish
cd ~/DailyEnglish
```

#### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run the application

```bash
# Foreground (for testing)
python3 app.py

# Background (for production)
nohup python3 app.py > app.log 2>&1 &
```

#### 5. Access the app

Open your browser and navigate to:

```
http://<VM-IP>:5000
```

For example: `http://10.93.25.94:5000`

#### 6. (Optional) Run as a systemd service

For automatic startup and reliability:

```bash
sudo nano /etc/systemd/system/dailyenglish.service
```

Paste the following:

```ini
[Unit]
Description=DailyEnglish Web App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/DailyEnglish
ExecStart=/root/DailyEnglish/venv/bin/python3 app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dailyenglish
sudo systemctl start dailyenglish

# Check status
sudo systemctl status dailyenglish

# View logs
sudo journalctl -u dailyenglish -f
```

### Firewall Configuration

If `ufw` is enabled, allow port 5000:

```bash
sudo ufw allow 5000/tcp
```

### Verify Deployment

```bash
curl -s http://localhost:5000 | head -5
```

You should see HTML output starting with `<!DOCTYPE html>`.

## Project Structure

```
DailyEnglish/
├── app.py                 # Flask backend (API + routing)
├── vocabulary.py          # 90-word dictionary with translations
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Frontend HTML
├── static/
│   ├── style.css          # Dark theme styles
│   └── script.js          # Timer + word fetching logic
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose deployment
└── README.md              # This file
```

## Tech Stack

- **Backend:** Python 3.12 + Flask 3.0
- **Frontend:** HTML5 + CSS3 + Vanilla JavaScript
- **Deployment:** systemd / Docker
