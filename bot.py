"""
DailyEnglish Telegram Bot
Ежедневный бот для изучения английских слов.
"""

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
    MessageHandler,
    filters,
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

# Отслеживание отправленных слов каждому пользователю (чтобы не повторяться в один день)
user_daily_words: dict[int, set] = {}
user_total_seen: dict[int, set] = {}  # все слова, которые пользователь уже видел


def get_word_of_the_day(user_id: int) -> dict:
    """
    Получить слово дня для пользователя.
    Если пользователь уже получил слово сегодня, вернуть то же самое.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{user_id}_{today}"

    if key not in user_daily_words:
        # Выбираем случайное слово, которое пользователь ещё не видел
        available = [w for w in VOCABULARY if w["word"] not in user_total_seen.get(user_id, set())]
        if not available:
            # Если все слова изучены, сбрасываем и начинаем заново
            user_total_seen[user_id] = set()
            available = VOCABULARY[:]

        word = random.choice(available)
        user_daily_words[key] = word["word"]
        user_total_seen.setdefault(user_id, set()).add(word["word"])

    # Находим полное слово по названию
    word_str = user_daily_words[key]
    return next(w for w in VOCABULARY if w["word"] == word_str)


def get_next_word(user_id: int) -> dict:
    """Получить следующее случайное слово (для кнопки Next)."""
    available = [w for w in VOCABULARY if w["word"] not in user_total_seen.get(user_id, set())]
    if not available:
        user_total_seen[user_id] = set()
        available = VOCABULARY[:]

    word = random.choice(available)
    user_total_seen.setdefault(user_id, set()).add(word["word"])

    # Обновляем слово дня
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{user_id}_{today}"
    user_daily_words[key] = word["word"]

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    user_id = user.id

    # Инициализируем отслеживание
    if user_id not in user_total_seen:
        user_total_seen[user_id] = set()

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

    if user_id not in user_total_seen:
        user_total_seen[user_id] = set()

    word = get_word_of_the_day(user_id)
    message = format_word_message(word)

    await update.message.reply_html(
        text=f"📖 <b>Слово дня:</b>\n\n{message}",
        reply_markup=get_next_keyboard(),
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /stats — показать статистику."""
    user_id = update.effective_user.id
    seen_count = len(user_total_seen.get(user_id, set()))
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

    if user_id not in user_total_seen:
        user_total_seen[user_id] = set()

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

    if user_id not in user_total_seen:
        user_total_seen[user_id] = set()

    word = get_next_word(user_id)
    message = format_word_message(word)

    await query.edit_message_text(
        text=f"🆕 <b>Новое слово:</b>\n\n{message}",
        parse_mode="HTML",
        reply_markup=get_next_keyboard(),
    )


async def daily_word_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ежедневная отправка слова всем активным пользователям."""
    # Собираем всех пользователей, которые уже взаимодействовали с ботом
    all_users = set(user_total_seen.keys())

    for user_id in all_users:
        try:
            word = get_word_of_the_day(user_id)
            message = format_word_message(word)

            await context.bot.send_message(
                chat_id=user_id,
                text=f"☀️ <b>Доброе утро! Вот твоё слово на сегодня:</b>\n\n{message}",
                parse_mode="HTML",
                reply_markup=get_next_keyboard(),
            )
        except Exception as e:
            logger.error(f"Ошибка отправки слова пользователю {user_id}: {e}")


def main() -> None:
    """Запуск бота."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен! Установите переменную окружения.")
        return

    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("word", word_of_the_day))
    application.add_handler(CommandHandler("next", next_word_handler))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("help", help_command))

    # Регистрируем обработчик inline-кнопок
    application.add_handler(CallbackQueryHandler(button_callback))

    # Настраиваем ежедневную рассылку (9:00 утра по UTC)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        daily_word_job,
        "cron",
        hour=9,
        minute=0,
        args=[application._job_queue],
        replace_existing=True,
    )
    scheduler.start()

    logger.info("Бот запущен! Ожидание сообщений...")
    logger.info("Ежедневная рассылка настроена на 9:00 UTC")

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
