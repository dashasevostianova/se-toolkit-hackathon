// ===== CONFIG =====
const REFRESH_INTERVAL = 180; // 3 minutes in seconds

// ===== STATE =====
let timer = REFRESH_INTERVAL;
let timerInterval = null;
let isFetching = false;
let hasError = false;

// ===== DOM ELEMENTS =====
const loading = document.getElementById("loading");
const wordContent = document.getElementById("wordContent");
const wordEmoji = document.getElementById("wordEmoji");
const wordText = document.getElementById("wordText");
const wordTranslation = document.getElementById("wordTranslation");
const wordExample = document.getElementById("wordExample");
const wordDate = document.getElementById("wordDate");
const timerEl = document.getElementById("timer");
const timerBadge = document.getElementById("timerBadge");
const timerDot = document.getElementById("timerDot");
const statSeen = document.getElementById("statSeen");
const statPercent = document.getElementById("statPercent");
const progressFill = document.getElementById("progressFill");
const cycleInfo = document.getElementById("cycleInfo");
const allLearnedBanner = document.getElementById("allLearnedBanner");
const nextBtn = document.getElementById("nextBtn");

// ===== FUNCTIONS =====

function updateTimerDisplay() {
    // Clamp timer to 0 minimum
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
    // Clear existing timer
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

function displayWord(data) {
    wordEmoji.textContent = data.emoji;
    wordText.textContent = data.word;
    wordTranslation.textContent = data.translation;
    wordExample.textContent = `"${data.example}"`;

    const now = new Date();
    wordDate.textContent = now.toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });

    // Show/hide "all learned" banner
    if (data.all_learned) {
        allLearnedBanner.classList.remove("hidden");
    } else {
        allLearnedBanner.classList.add("hidden");
    }

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
        await fetchStats();
        startTimer();
    } catch (err) {
        console.error("Error fetching word:", err);
        hasError = true;
        // Restart timer after 10 seconds on error
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

async function fetchStats() {
    try {
        const res = await fetch("/api/stats");
        if (!res.ok) return;

        const stats = await res.json();

        // Cap percent at 100
        const pct = Math.min(stats.percent, 100);
        statSeen.textContent = stats.seen;
        statPercent.textContent = `${pct}%`;
        progressFill.style.width = `${pct}%`;

        // Show cycle info
        if (stats.reset_count > 0) {
            cycleInfo.textContent = `Cycle #${stats.reset_count + 1}`;
        } else {
            cycleInfo.textContent = "";
        }
    } catch (err) {
        console.error("Error fetching stats:", err);
    }
}

// ===== INIT =====
document.addEventListener("DOMContentLoaded", () => {
    fetchNextWord();
});

// Re-fetch when tab becomes visible again
document.addEventListener("visibilitychange", () => {
    if (!document.hidden && hasError) {
        fetchNextWord();
    }
});
