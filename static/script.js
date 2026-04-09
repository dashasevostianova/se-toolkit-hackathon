// ===== CONFIG =====
const REFRESH_INTERVAL = 180; // 3 minutes in seconds

// ===== STATE =====
let timer = REFRESH_INTERVAL;
let timerInterval = null;
let isFetching = false;
let hasError = false;
let translationRevealed = false;
let lastPoolProgress = 0;
let currentDailyLimit = 10;

// ===== DOM ELEMENTS =====
const loading = document.getElementById("loading");
const wordContent = document.getElementById("wordContent");
const wordEmoji = document.getElementById("wordEmoji");
const wordText = document.getElementById("wordText");
const wordTranslation = document.getElementById("wordTranslation");
const wordExample = document.getElementById("wordExample");
const timerEl = document.getElementById("timer");
const timerBadge = document.getElementById("timerBadge");
const timerDot = document.getElementById("timerDot");
const statSeenToday = document.getElementById("statSeenToday");
const statDailyLimit = document.getElementById("statDailyLimit");
const statCycle = document.getElementById("statCycle");
const progressFill = document.getElementById("progressFill");
const revealBtn = document.getElementById("revealBtn");
const poolProgressText = document.getElementById("poolProgressText");
const poolProgressFill = document.getElementById("poolProgressFill");
const reshuffleBanner = document.getElementById("reshuffleBanner");
const settingsPanel = document.getElementById("settingsPanel");
const nextBtn = document.getElementById("nextBtn");
const currentLimitEl = document.getElementById("currentLimit");

// ===== TIMER =====

function updateTimerDisplay() {
    if (timer < 0) timer = 0;
    const minutes = Math.floor(timer / 60);
    const seconds = timer % 60;
    timerEl.textContent = `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function setTimerState(active) {
    if (active) {
        timerBadge.classList.remove("paused");
        timerDot.style.background = "var(--success)";
    } else {
        timerBadge.classList.add("paused");
        timerDot.style.background = "var(--warning)";
    }
}

function startTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    timer = REFRESH_INTERVAL;
    updateTimerDisplay();
    setTimerState(true);

    timerInterval = setInterval(() => {
        timer--;
        updateTimerDisplay();

        if (timer <= 0) {
            clearInterval(timerInterval);
            timerInterval = null;
            setTimerState(false);
            fetchNextWord();
        }
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    setTimerState(false);
}

// ===== TRANSLATION REVEAL =====

function toggleTranslation() {
    if (translationRevealed) {
        wordTranslation.classList.remove("revealed");
        wordTranslation.classList.add("blur-text");
        revealBtn.innerHTML = "👁️ Show";
        translationRevealed = false;
    } else {
        wordTranslation.classList.add("revealed");
        wordTranslation.classList.remove("blur-text");
        revealBtn.innerHTML = "🙈 Hide";
        translationRevealed = true;
    }
}

// ===== SETTINGS =====

function toggleSettings() {
    settingsPanel.classList.toggle("hidden");
}

function setLimit(limit) {
    // Update active button
    document.querySelectorAll(".limit-btn").forEach(btn => {
        btn.classList.toggle("active", parseInt(btn.dataset.limit) === limit);
    });

    // Send to backend
    fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ daily_limit: limit }),
    })
    .then(res => res.json())
    .then(data => {
        currentDailyLimit = data.daily_limit;
        currentLimitEl.textContent = currentDailyLimit;
        statDailyLimit.textContent = currentDailyLimit;
    })
    .catch(err => console.error("Error updating settings:", err));
}

async function loadSettings() {
    try {
        const res = await fetch("/api/settings");
        const data = await res.json();
        currentDailyLimit = data.daily_limit;
        currentLimitEl.textContent = currentDailyLimit;
        statDailyLimit.textContent = currentDailyLimit;

        // Highlight active button
        document.querySelectorAll(".limit-btn").forEach(btn => {
            btn.classList.toggle("active", parseInt(btn.dataset.limit) === currentDailyLimit);
        });
    } catch (err) {
        console.error("Error loading settings:", err);
    }
}

// ===== WORD FETCHING =====

function resetTranslation() {
    translationRevealed = false;
    wordTranslation.classList.remove("revealed");
    wordTranslation.classList.add("blur-text");
    revealBtn.innerHTML = "👁️ Show";
}

function displayWord(data) {
    resetTranslation();

    wordEmoji.textContent = data.emoji;
    wordText.textContent = data.word;
    wordTranslation.textContent = data.translation;
    wordExample.textContent = `"${data.example}"`;

    // Pool progress
    poolProgressText.textContent = `${data.pool_progress} / ${data.pool_size}`;
    const pct = (data.pool_progress / data.pool_size) * 100;
    poolProgressFill.style.width = `${Math.min(pct, 100)}%`;

    // Show reshuffle banner if pool was exhausted and restarted
    if (data.cycle > 1 && data.pool_progress <= 1) {
        reshuffleBanner.classList.remove("hidden");
        setTimeout(() => {
            reshuffleBanner.classList.add("hidden");
        }, 4000);
    } else {
        reshuffleBanner.classList.add("hidden");
    }

    // Stats
    statSeenToday.textContent = data.pool_progress;
    statCycle.textContent = data.cycle;

    // Progress bar
    const progressPct = (data.pool_progress / data.pool_size) * 100;
    progressFill.style.width = `${Math.min(progressPct, 100)}%`;

    // Show content
    loading.classList.add("hidden");
    wordContent.classList.remove("hidden");

    // Animation
    wordContent.parentElement.classList.add("animate-in");
    setTimeout(() => {
        wordContent.parentElement.classList.remove("animate-in");
    }, 500);
}

async function fetchNextWord() {
    if (isFetching) return;
    isFetching = true;
    hasError = false;
    nextBtn.disabled = true;

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        const res = await fetch("/api/word", { signal: controller.signal });
        clearTimeout(timeoutId);

        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        displayWord(data);
        startTimer();
    } catch (err) {
        console.error("Error fetching word:", err);
        hasError = true;
        stopTimer();
        timer = 10;
        updateTimerDisplay();
        timerInterval = setInterval(() => {
            timer--;
            updateTimerDisplay();
            if (timer <= 0) {
                clearInterval(timerInterval);
                timerInterval = null;
                fetchNextWord();
            }
        }, 1000);
    } finally {
        isFetching = false;
        nextBtn.disabled = false;
    }
}

// ===== INIT =====
document.addEventListener("DOMContentLoaded", () => {
    loadSettings();
    fetchNextWord();
});

// Re-fetch when tab becomes visible again
document.addEventListener("visibilitychange", () => {
    if (!document.hidden && hasError) {
        fetchNextWord();
    }
});
