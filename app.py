"""
DailyEnglish Web App
Flask backend with word API.
"""

import random
from flask import Flask, render_template, jsonify, session

from vocabulary import VOCABULARY

app = Flask(__name__)
app.secret_key = "dailyenglish_secret_key_2024"

TOTAL_WORDS = len(VOCABULARY)

# Session storage
# session_id -> {
#   "daily_limit": int,
#   "daily_pool": [word_indices],
#   "pool_index": int,
#   "cycle": int,
#   "seen_count": int (lifetime),
# }
sessions: dict = {}


def get_session_id():
    if "user_id" not in session:
        session["user_id"] = f"user_{random.randint(10000, 99999)}"
    return session["user_id"]


def get_session_data(sid):
    if sid not in sessions:
        sessions[sid] = {
            "daily_limit": 10,
            "daily_pool": [],
            "pool_index": 0,
            "cycle": 0,
            "seen_count": 0,
        }
    return sessions[sid]


def generate_daily_pool(data):
    """Generate a shuffled pool of words for today."""
    limit = min(data["daily_limit"], TOTAL_WORDS)
    indices = list(range(TOTAL_WORDS))
    random.shuffle(indices)
    data["daily_pool"] = indices[:limit]
    data["pool_index"] = 0
    data["cycle"] += 1


def next_word_from_pool(data):
    """Get next word from the daily pool. Reshuffle if pool exhausted."""
    if data["pool_index"] >= len(data["daily_pool"]):
        # Pool exhausted — reshuffle
        generate_daily_pool(data)

    word_idx = data["daily_pool"][data["pool_index"]]
    data["pool_index"] += 1
    data["seen_count"] += 1
    return VOCABULARY[word_idx]


@app.route("/")
def index():
    return render_template("index.html", total_words=TOTAL_WORDS)


@app.route("/api/settings", methods=["GET"])
def get_settings():
    sid = get_session_id()
    data = get_session_data(sid)
    return jsonify({
        "daily_limit": data["daily_limit"],
        "total_available": TOTAL_WORDS,
    })


@app.route("/api/settings", methods=["POST"])
def update_settings():
    sid = get_session_id()
    data = get_session_data(sid)
    req = get_json_safe()
    if req and "daily_limit" in req:
        new_limit = int(req["daily_limit"])
        if new_limit < 1:
            new_limit = 1
        if new_limit > TOTAL_WORDS:
            new_limit = TOTAL_WORDS
        data["daily_limit"] = new_limit
        # Regenerate pool with new limit
        generate_daily_pool(data)
    return jsonify({
        "daily_limit": data["daily_limit"],
        "pool_size": len(data["daily_pool"]),
    })


def get_json_safe():
    """Safely get JSON body from request."""
    from flask import request
    try:
        return request.get_json(force=True, silent=True)
    except Exception:
        return None


@app.route("/api/word", methods=["GET"])
def get_word():
    sid = get_session_id()
    data = get_session_data(sid)

    # Ensure pool exists
    if not data["daily_pool"]:
        generate_daily_pool(data)

    word = next_word_from_pool(data)

    return jsonify({
        "word": word["word"],
        "translation": word["translation"],
        "example": word["example"],
        "emoji": word["emoji"],
        "pool_progress": data["pool_index"],
        "pool_size": len(data["daily_pool"]),
        "cycle": data["cycle"],
    })


@app.route("/api/stats", methods=["GET"])
def get_stats():
    sid = get_session_id()
    data = get_session_data(sid)

    pool_progress = data["pool_index"]
    pool_size = len(data["daily_pool"]) if data["daily_pool"] else data["daily_limit"]

    return jsonify({
        "seen_today": pool_progress,
        "daily_limit": pool_size,
        "total_seen_lifetime": data["seen_count"],
        "cycle": data["cycle"],
        "percent_today": round(pool_progress / pool_size * 100, 1) if pool_size > 0 else 0,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
