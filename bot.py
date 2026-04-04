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
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from vocabulary import VOCABULARY

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Получаем токен из переменной окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Файл для хранения данных пользователей
USERS_FILE = "users.json"

# Глобальное хранилище
users_data: dict = {}  # {user_id: {"seen_words": [...], "last_word": "..."}}
registered_users: set = set()  # set(user_id) — все, кто нажал /start


def load_users():
    """Загружает данные пользователей из файла."""
    global users_data, registered_users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            users_data = data.get("users", {})
            registered_users = set(data.get("registered", []))
        logger.info(f"Загружено {len(registered_users)} пользователей")
    else:
        logger.info("Файл users.json не найден, начинаем с нуля")


def save_users():
    """Сохраняет данные пользователей в файл."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "users": users_data,
            "registered": list(registered_users),
        }, f, ensure_ascii=False, indent=2)


def get_word_of_the_day(user_id: int) -> dict:
    """Получить слово для пользователя (новое или то же самое за 'день')."""
    uid = str(user_id)
    if uid not in users_data:
        users_data[uid] = {"seen_words": [], "last_word": None, "date": None}

    user = users_data[uid]
    today = datetime.now().strftime("%Y-%m-%d")

    # Если сегодня уже получал слово — вернуть его
    if user["date"] == today and user["last_word"]:
        return next(w for w in VOCABULARY if w["word"] == user["last_word"])

    # Выбираем новое слово
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


def get_next_word(user_id: int) -> dict:
    """Получить следующее случайное слово (для кнопки Next)."""
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
    return word


def format_word_message(word: dict) -> str:
    """Форматирует сообщение со словом."""
    message = (
        f"{word['emoji']} <b>{word['word']}</b>\n\n"
        f"🇷🇺 <b>Перевод:</b> {word['translation']}\n\n"
        f"📝 <b>Пример:</b>\n"
        f"<i>{word['example']}</i>\n\n"
        f"📅 <code>{datetime.now().strftime('%d.%m.%Y')}</code>"
    )
    return message


def get_next_keyboard() -> InlineKeyboardMarkup:
    """Создаёт inline-кнопку 'Next'."""
    keyboard = [[InlineKeyboardButton("🔄 Next word", callback_data="next_word")]]
    return InlineKeyboardMarkup(keyboard)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок."""
    logger.error("Exception while handling an update:", exc_info=context.error)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    user_id = user.id

    # Регистрируем пользователя
    registered_users.add(user_id)
    save_users()

    word = get_word_of_the_day(user_id)
    message = format_word_message(word)

    await update.message.reply_html(
        text=(
            f"Привет, {user.mention_html()}! 👋\n\n"
            f"Добро пожаловать в <b>DailyEnglish</b> — бот для изучения английских слов!\n\n"
            f"Каждый день я буду отправлять тебе новое слово с переводом и примером.\n"
            f"А если хочешь учиться быстрее — жми кнопку ниже 👇\n\n"
            f"{message}"
        ),
        reply_markup=get_next_keyboard(),
    )


async def word_of_the_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /word — получить сегодняшнее слово."""
    user_id = update.effective_user.id

    # Регистрируем если ещё нет
    registered_users.add(user_id)
    save_users()

    word = get_word_of_the_day(user_id)
    message = format_word_message(word)

    await update.message.reply_html(
        text=f"📖 <b>Слово дня:</b>\n\n{message}",
        reply_markup=get_next_keyboard(),
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /stats — показать статистику."""
    user_id = update.effective_user.id
    uid = str(user_id)
    seen_count = len(users_data.get(uid, {}).get("seen_words", []))
    total_count = len(VOCABULARY)

    await update.message.reply_text(
        f"📊 <b>Статистика:</b>\n\n"
        f"Изучено слов: {seen_count}/{total_count}\n"
        f"Осталось: {total_count - seen_count}\n\n"
        f"{'🎉 Отлично! Ты изучил все слова!' if seen_count >= total_count else 'Продолжай в том же духе! 💪'}",
        parse_mode="HTML",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    await update.message.reply_html(
        "<b>Доступные команды:</b>\n\n"
        "/start — Начать изучение\n"
        "/word — Получить сегодняшнее слово\n"
        "/next — Следующее слово\n"
        "/stats — Статистика изучения\n"
        "/help — Эта справка\n\n"
        "💡 <i>Новое слово приходит каждый день автоматически!</i>"
    )


async def next_word_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /next."""
    user_id = update.effective_user.id

    registered_users.add(user_id)
    save_users()

    word = get_next_word(user_id)
    message = format_word_message(word)

    await update.message.reply_html(
        text=f"🆕 <b>Новое слово:</b>\n\n{message}",
        reply_markup=get_next_keyboard(),
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатия inline-кнопки."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    registered_users.add(user_id)
    save_users()

    word = get_next_word(user_id)
    message = format_word_message(word)

    await query.edit_message_text(
        text=f"🆕 <b>Новое слово:</b>\n\n{message}",
        parse_mode="HTML",
        reply_markup=get_next_keyboard(),
    )


async def scheduled_word_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка нового слова всем зарегистрированным пользователям."""
    if not registered_users:
        logger.info("Нет зарегистрированных пользователей, пропускаю")
        return

    logger.info(f"Отправляю слово {len(registered_users)} пользователям")

    for user_id in registered_users:
        try:
            word = get_word_of_the_day(user_id)
            message = format_word_message(word)

            await context.bot.send_message(
                chat_id=user_id,
                text=f"📚 <b>Новое слово!</b>\n\n{message}",
                parse_mode="HTML",
                reply_markup=get_next_keyboard(),
            )
            logger.info(f"Отправлено пользователю {user_id}: {word['word']}")
        except Exception as e:
            logger.error(f"Ошибка отправки пользователю {user_id}: {e}")


def main() -> None:
    """Запуск бота."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        return

    # Загружаем сохранённых пользователей
    load_users()

    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчик ошибок
    application.add_error_handler(error_handler)

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("word", word_of_the_day))
    application.add_handler(CommandHandler("next", next_word_handler))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("help", help_command))

    # Регистрируем обработчик inline-кнопок
    application.add_handler(CallbackQueryHandler(button_callback))

    # Настраиваем рассылку каждые 3 минуты (для тестирования)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_word_job,
        "interval",
        minutes=3,
        replace_existing=True,
    )
    scheduler.start()

    logger.info("Бот запущен! Ожидание сообщений...")
    logger.info(f"Зарегистрировано пользователей: {len(registered_users)}")
    logger.info("⏰ ТЕСТОВЫЙ РЕЖИМ: рассылка каждые 3 минуты")

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
