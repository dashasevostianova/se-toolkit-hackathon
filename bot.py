"""
DailyEnglish Telegram Bot
Ежедневный бот для изучения английских слов.
"""

import json
import logging
import os
import random
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from vocabulary import VOCABULARY

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USERS_FILE = "users.json"

users_data: dict = {}
registered_users: set = set()


def load_users():
    global users_data, registered_users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            users_data = data.get("users", {})
            registered_users = set(data.get("registered", []))
        logger.info(f"Загружено {len(registered_users)} пользователей: {list(registered_users)}")
    else:
        logger.info("Файл users.json не найден, начинаем с нуля")


def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "users": users_data,
            "registered": list(registered_users),
        }, f, ensure_ascii=False, indent=2)


def get_word_for_user(user_id: int) -> dict:
    uid = str(user_id)
    if uid not in users_data:
        users_data[uid] = {"seen_words": [], "last_word": None, "date": None}

    user = users_data[uid]
    today = datetime.now().strftime("%Y-%m-%d")

    if user["date"] == today and user["last_word"]:
        return next(w for w in VOCABULARY if w["word"] == user["last_word"])

    seen = set(user["seen_words"])
    available = [w for w in VOCABULARY if w["word"] not in seen]
    if not available:
        user["seen_words"] = []
        available = VOCABULARY[:]

    word = random.choice(available)
    user["last_word"] = word["word"]
    user["date"] = today
    user["seen_words"].append(word["word"])
    save_users()
    return word


def format_word_message(word: dict) -> str:
    return (
        f"{word['emoji']} <b>{word['word']}</b>\n\n"
        f"🇷🇺 <b>Перевод:</b> {word['translation']}\n\n"
        f"📝 <b>Пример:</b>\n"
        f"<i>{word['example']}</i>\n\n"
        f"📅 <code>{datetime.now().strftime('%d.%m.%Y')}</code>"
    )


def get_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔄 Next word", callback_data="next_word")
    ]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    registered_users.add(user_id)
    save_users()
    logger.info(f"Пользователь {user_id} зарегистрирован")

    word = get_word_for_user(user_id)
    msg = format_word_message(word)

    await update.message.reply_html(
        text=(
            f"Привет, {user.mention_html()}! 👋\n\n"
            f"Добро пожаловать в <b>DailyEnglish</b>!\n\n"
            f"Каждый день — новое слово с переводом и примером.\n"
            f"Хочешь больше — жми кнопку 👇\n\n"
            f"{msg}"
        ),
        reply_markup=get_keyboard(),
    )


async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    registered_users.add(user_id)
    save_users()

    word = get_word_for_user(user_id)
    msg = format_word_message(word)

    await update.message.reply_html(
        text=f"📖 <b>Слово:</b>\n\n{msg}",
        reply_markup=get_keyboard(),
    )


async def next_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    registered_users.add(user_id)
    save_users()

    uid = str(user_id)
    if uid not in users_data:
        users_data[uid] = {"seen_words": [], "last_word": None, "date": None}

    user = users_data[uid]
    seen = set(user["seen_words"])
    available = [w for w in VOCABULARY if w["word"] not in seen]
    if not available:
        user["seen_words"] = []
        available = VOCABULARY[:]

    word = random.choice(available)
    user["last_word"] = word["word"]
    user["date"] = datetime.now().strftime("%Y-%m-%d")
    user["seen_words"].append(word["word"])
    save_users()

    msg = format_word_message(word)
    await update.message.reply_html(
        text=f"🆕 <b>Новое слово:</b>\n\n{msg}",
        reply_markup=get_keyboard(),
    )


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    uid = str(user_id)
    seen_count = len(users_data.get(uid, {}).get("seen_words", []))
    total = len(VOCABULARY)

    await update.message.reply_text(
        f"📊 <b>Статистика:</b>\n\n"
        f"Изучено: {seen_count}/{total}\n"
        f"Осталось: {total - seen_count}\n\n"
        f"{'🎉 Все слова изучены!' if seen_count >= total else 'Продолжай! 💪'}",
        parse_mode="HTML",
    )


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        "<b>Команды:</b>\n\n"
        "/start — Начать\n"
        "/word — Сегодняшнее слово\n"
        "/next — Следующее слово\n"
        "/stats — Статистика\n"
        "/help — Справка"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    registered_users.add(user_id)
    save_users()

    uid = str(user_id)
    if uid not in users_data:
        users_data[uid] = {"seen_words": [], "last_word": None, "date": None}

    user = users_data[uid]
    seen = set(user["seen_words"])
    available = [w for w in VOCABULARY if w["word"] not in seen]
    if not available:
        user["seen_words"] = []
        available = VOCABULARY[:]

    word = random.choice(available)
    user["last_word"] = word["word"]
    user["date"] = datetime.now().strftime("%Y-%m-%d")
    user["seen_words"].append(word["word"])
    save_users()

    msg = format_word_message(word)
    await query.edit_message_text(
        text=f"🆕 <b>Новое слово:</b>\n\n{msg}",
        parse_mode="HTML",
        reply_markup=get_keyboard(),
    )


async def send_words_to_all(context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"[JOB] Запуск рассылки. Пользователей: {len(registered_users)}")
    if not registered_users:
        logger.warning("[JOB] Нет пользователей!")
        return

    for user_id in registered_users:
        try:
            word = get_word_for_user(user_id)
            msg = format_word_message(word)
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📚 <b>Новое слово!</b>\n\n{msg}",
                parse_mode="HTML",
                reply_markup=get_keyboard(),
            )
            logger.info(f"[JOB] Отправлено {user_id}: {word['word']}")
        except Exception as e:
            logger.error(f"[JOB] Ошибка для {user_id}: {e}")


def main() -> None:
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        return

    load_users()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("word", show_word))
    application.add_handler(CommandHandler("next", next_cmd))
    application.add_handler(CommandHandler("stats", show_stats))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(lambda update, ctx: logger.error("Error: %s", ctx.error))

    # Рассылка через встроенный JobQueue
    application.job_queue.run_repeating(
        send_words_to_all,
        interval=180,
        first=60,
        name="daily_word",
    )

    logger.info("Бот запущен!")
    logger.info(f"Пользователей: {len(registered_users)} -> {list(registered_users)}")
    logger.info("⏰ ТЕСТ: рассылка каждые 3 минуты (первый запуск через 60 сек)")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
