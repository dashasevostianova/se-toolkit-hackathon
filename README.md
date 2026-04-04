# DailyEnglish Telegram Bot 🇬🇧

Telegram-бот для ежедневчного изучения английских слов. Каждый день бот отправляет одно новое слово с переводом на русский язык и примером использования.

## Возможности ✨

- **Ежедневное слово** — каждое утро (в 9:00 UTC) бот автоматически отправляет новое слово
- **Ручной запрос** — команда `/next` или кнопка "Next" для получения дополнительного слова
- **Перевод на русский** — каждое слово содержит перевод и пример предложения
- **Визуальные эмодзи** — каждое слово имеет ассоциативную эмодзи-картинку
- **Статистика** — отслеживание прогресса изучения (`/stats`)
- **90 уникальных слов** — словарь с разнообразной лексикой

## Команды бота 📋

| Команда      | Описание                              |
|-------------|---------------------------------------|
| `/start`    | Начать изучение, получить первое слово |
| `/word`     | Получить сегодняшнее слово             |
| `/next`     | Следующее случайное слово              |
| `/stats`    | Показать статистику изучения           |
| `/help`     | Справка по командам                    |

## Установка и запуск 🚀

### Шаг 1: Создание Telegram бота

1. Откройте Telegram и найдите бота **@BotFather**
2. Отправьте команду `/newbot`
3. Введите имя для вашего бота (например, `DailyEnglish`)
4. Введите username для бота (должен заканчиваться на `bot`, например `daily_english_study_bot`)
5. **Скопируйте полученный токен** (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Шаг 2: Подготовка сервера (VM)

Подключитесь к вашей виртуальной машине:

```bash
ssh user@your-vm-ip
```

### Шаг 3: Клонирование/загрузка проекта

Если проект в Git репозитории:

```bash
git clone <ваш-repo-url>
cd project
```

Или скопируйте файлы вручную на VM:

```bash
# Структура проекта:
project/
├── bot.py              # Основной файл бота
├── vocabulary.py       # Словарь из 90 слов
├── requirements.txt    # Зависимости Python
└── README.md           # Этот файл
```

### Шаг 4: Установка Python зависимостей

```bash
# Убедитесь, что Python 3.8+ установлен
python3 --version

# Создаём виртуальное окружение (рекомендуется)
python3 -m venv venv

# Активируем виртуальное окружение
# Для Linux/Mac:
source venv/bin/activate
# Для Windows:
# venv\Scripts\activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### Шаг 5: Установка токена бота

**Вариант A: Через переменную окружения (рекомендуется)**

```bash
export TELEGRAM_BOT_TOKEN="ваш_токен_от_BotFather"
```

**Вариант B: Создать файл .env**

```bash
echo 'TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather' > .env
```

И добавьте в начало `bot.py` загрузку из .env:

```python
from dotenv import load_dotenv
load_dotenv()
```

И добавьте `python-dotenv==1.0.0` в `requirements.txt`.

### Шаг 6: Запуск бота

```bash
python3 bot.py
```

Вы должны увидеть:

```
Бот запущен! Ожидание сообщений...
Ежедневная рассылка настроена на 9:00 UTC
```

### Шаг 7: Запуск в фоновом режиме (production)

**Вариант A: Использование `nohup`**

```bash
nohup python3 bot.py > bot.log 2>&1 &
```

**Вариант B: Использование `screen`**

```bash
# Установите screen если не установлен
sudo apt install screen  # Ubuntu/Debian

# Создаём сессию
screen -S dailyenglish

# Запускаем бота
python3 bot.py

# Отсоединяемся: Ctrl+A, затем D
```

**Вариант C: Создание systemd сервиса (рекомендуется для production)**

Создайте файл сервиса:

```bash
sudo nano /etc/systemd/system/dailyenglish.service
```

Вставьте содержимое:

```ini
[Unit]
Description=DailyEnglish Telegram Bot
After=network.target

[Service]
Type=simple
User=ваш_пользователь
WorkingDirectory=/путь/к/project
Environment="TELEGRAM_BOT_TOKEN=ваш_токен"
ExecStart=/путь/к/project/venv/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируйте и запустите:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dailyenglish
sudo systemctl start dailyenglish

# Проверка статуса
sudo systemctl status dailyenglish

# Просмотр логов
sudo journalctl -u dailyenglish -f
```

## Проверка работы ✅

1. Найдите вашего бота в Telegram по username
2. Нажмите **Start** или отправьте `/start`
3. Бот должен ответить приветственным сообщением со словом
4. Протестируйте команды: `/word`, `/next`, `/stats`, `/help`

## Настройка времени рассылки ⏰

По умолчанию бот отправляет слова в **9:00 UTC**. Чтобы изменить:

Откройте `bot.py` и найдите строку:

```python
scheduler.add_job(
    daily_word_job,
    "cron",
    hour=9,      # Измените час
    minute=0,    # Измените минуту
    ...
)
```

Для московского времени (UTC+3) установите `hour=6` (6:00 UTC = 9:00 МСК).

## Структура проекта 📁

```
project/
├── bot.py              # Основная логика бота
├── vocabulary.py       # Словарь (90 слов с переводом)
├── requirements.txt    # Python зависимости
└── README.md           # Документация
```

## Зависимости 📦

- **python-telegram-bot** — библиотека для работы с Telegram Bot API
- **APScheduler** — планировщик задач для ежедневной рассылки

## Добавление новых слов 📝

Откройте `vocabulary.py` и добавьте новое слово в список `VOCABULARY`:

```python
{
    "word": "YourWord",
    "translation": "Перевод на русский",
    "example": "Example sentence in English.",
    "emoji": "🎯"
},
```

## Решение проблем 🔧

**Бот не запускается:**
- Проверьте, что токен установлен: `echo $TELEGRAM_BOT_TOKEN`
- Проверьте логи: `python3 bot.py` и посмотрите вывод

**Ошибка импорта модулей:**
```bash
pip install -r requirements.txt
```

**Бот не отвечает на сообщения:**
- Убедитесь, что бот запущен
- Проверьте, что вы отправили `/start`
- Посмотрите логи бота

## Лицензия 📄

MIT License — используйте свободно!

## Автор 👤

Создано для ежедневного изучения английского языка 🎓
