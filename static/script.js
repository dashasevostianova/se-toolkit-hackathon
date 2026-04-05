// ===== CONFIG =====
const REFRESH_INTERVAL = 180; // 3 минуты в секундах

// ===== STATE =====
let timer = REFRESH_INTERVAL;
let timerInterval = null;

// ===== DOM ELEMENTS =====
const loading = document.getElementById("loading");
const wordContent = document.getElementById("wordContent");
const wordEmoji = document.getElementById("wordEmoji");
const wordText = document.getElementById("wordText");
const wordTranslation = document.getElementById("wordTranslation");
const wordExample = document.getElementById("wordExample");
const wordDate = document.getElementById("wordDate");
const timerEl = document.getElementById("timer");
const statSeen = document.getElementById("statSeen");
const statPercent = document.getElementById("statPercent");
const progressFill = document.getElementById("progressFill");

// ===== FUNCTIONS =====

function updateTimerDisplay() {
    const minutes = Math.floor(timer / 60);
    const seconds = timer % 60;
    timerEl.textContent = `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function startTimer() {
    timer = REFRESH_INTERVAL;
    updateTimerDisplay();

    if (timerInterval) clearInterval(timerInterval);

    timerInterval = setInterval(() => {
        timer--;
        updateTimerDisplay();

        if (timer <= 0) {
            fetchNextWord();
        }
    }, 1000);
}

function displayWord(data) {
    wordEmoji.textContent = data.emoji;
    wordText.textContent = data.word;
    wordTranslation.textContent = data.translation;
    wordExample.textContent = `"${data.example}"`;

    const now = new Date();
    wordDate.textContent = now.toLocaleDateString("ru-RU", {
        day: "numeric",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });

    loading.classList.add("hidden");
    wordContent.classList.remove("hidden");

    // Анимация появления
    wordContent.parentElement.classList.add("animate-in");
    setTimeout(() => {
        wordContent.parentElement.classList.remove("animate-in");
    }, 500);
}

async function fetchNextWord() {
    try {
        const res = await fetch("/api/word");
        const data = await res.json();
        displayWord(data);
        fetchStats();
        startTimer();
    } catch (err) {
        console.error("Ошибка загрузки слова:", err);
    }
}

async function fetchStats() {
    try {
        const res = await fetch("/api/stats");
        const stats = await res.json();

        statSeen.textContent = stats.seen;
        statPercent.textContent = `${stats.percent}%`;
        progressFill.style.width = `${stats.percent}%`;
    } catch (err) {
        console.error("Ошибка загрузки статистики:", err);
    }
}

// ===== INIT =====
document.addEventListener("DOMContentLoaded", () => {
    fetchNextWord();
});
