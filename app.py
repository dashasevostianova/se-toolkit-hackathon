"""
DailyEnglish Web App
Flask backend with word API.
"""

import random
from datetime import datetime
from flask import Flask, render_template, jsonify, session

from vocabulary import VOCABULARY

app = Flask(__name__)
app.secret_key = "dailyenglish_secret_key_2024"

# Session storage: session_id -> dict
# Each session: {"seen_words": [...], "reset_count": int}
sessions: dict = {}

TOTAL_WORDS = len(VOCABULARY)


def get_session_id():
    if "user_id" not in session:
        session["user_id"] = f"user_{random.randint(10000, 99999)}"
    return session["user_id"]


def get_session_data(sid):
    if sid not in sessions:
        sessions[sid] = {"seen_words": [], "reset_count": 0}
    return sessions[sid]


@app.route("/")
def index():
    return render_template("index.html", total_words=TOTAL_WORDS)


@app.route("/api/word", methods=["GET"])
def get_word():
    sid = get_session_id()
    data = get_session_data(sid)
    seen = set(data["seen_words"])

    available = [w for w in VOCABULARY if w["word"] not in seen]
    all_learned = False

    if not available:
        all_learned = True
        data["seen_words"] = []
        data["reset_count"] += 1
        available = VOCABULARY[:]

    word = random.choice(available)
    data["seen_words"].append(word["word"])

    return jsonify({
        "word": word["word"],
        "translation": word["translation"],
        "example": word["example"],
        "emoji": word["emoji"],
        "all_learned": all_learned,
        "reset_count": data["reset_count"],
    })


@app.route("/api/stats", methods=["GET"])
def get_stats():
    sid = get_session_id()
    data = get_session_data(sid)
    seen_count = len(data["seen_words"])

    return jsonify({
        "seen": seen_count,
        "total": TOTAL_WORDS,
        "remaining": TOTAL_WORDS - seen_count,
        "percent": round(seen_count / TOTAL_WORDS * 100, 1),
        "reset_count": data.get("reset_count", 0),
    })


@app.route("/api/reset", methods=["POST"])
def reset_progress():
    sid = get_session_id()
    if sid in sessions:
        sessions[sid] = {"seen_words": [], "reset_count": sessions[sid].get("reset_count", 0)}
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
