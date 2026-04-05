"""
DailyEnglish Web App
Красивый сайт для изучения английских слов.
"""

import random
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session

from vocabulary import VOCABULARY

app = Flask(__name__)
app.secret_key = "dailyenglish_secret_key_2024"

# Хранилище изученных слов: session_id -> list
seen_words: dict = {}

# Общее количество слов
TOTAL_WORDS = len(VOCABULARY)


def get_session_id():
    """Получить или создать ID сессии."""
    if "user_id" not in session:
        session["user_id"] = f"user_{random.randint(10000, 99999)}"
    return session["user_id"]


def get_seen(session_id):
    """Получить список изученных слов для сессии."""
    if session_id not in seen_words:
        seen_words[session_id] = []
    return seen_words[session_id]


@app.route("/")
def index():
    """Главная страница."""
    return render_template("index.html", total_words=TOTAL_WORDS)


@app.route("/api/word", methods=["GET"])
def get_word():
    """Получить случайное слово (не повторяется, пока не пройдёшь все)."""
    sid = get_session_id()
    seen = get_seen(sid)

    available = [w for w in VOCABULARY if w["word"] not in seen]
    if not available:
        seen_words[sid] = []
        available = VOCABULARY[:]

    word = random.choice(available)
    seen.append(word["word"])
    seen_words[sid] = seen

    return jsonify({
        "word": word["word"],
        "translation": word["translation"],
        "example": word["example"],
        "emoji": word["emoji"],
    })


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Получить статистику пользователя."""
    sid = get_session_id()
    seen = get_seen(sid)

    return jsonify({
        "seen": len(seen),
        "total": TOTAL_WORDS,
        "remaining": TOTAL_WORDS - len(seen),
        "percent": round(len(seen) / TOTAL_WORDS * 100, 1),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
