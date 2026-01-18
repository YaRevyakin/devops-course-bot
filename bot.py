import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from database import register_user, get_topic_by_code, mark_completed, get_module_keyboard, initialize_database
from flask import Flask
from threading import Thread

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

<<<<<<< HEAD
# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "8226360790:AAH7DPXxvUinXEKnQBub7zExNb9uNkzaC78")
=======
# Токен из переменной окружения или напрямую (для Render — лучше через env)
BOT_TOKEN = os.getenv("8226360790:AAH7DPXxvUinXEKnQBub7zExNb9uNkzaC78")
>>>>>>> fd3d9915e5df8198387c4bb6b67df0175f8e61cd

# Основное меню
MAIN_MENU = [
    ["Модуль 0", "Модуль 1", "Модуль 2"],
    ["Модуль 3", "Модуль 4", "Модуль 5"],
    ["Модуль 6", "Модуль 7", "Модуль 8"],
    ["Модуль 9", "Модуль 10", "Модуль 12"],
    ["Модуль 13", "Модуль 14", "Проекты"],
    ["/help"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        if not user:
            await update.message.reply_text("❌ Не удалось определить пользователя.")
            return

        full_name = user.full_name or "Друг"
        register_user(user.id, full_name)

        reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        await update.message.reply_text(
            f"Привет, {full_name}! 👋\nВыбери модуль для изучения:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await update.message.reply_text("⚠️ Внутренняя ошибка. Попробуйте позже.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Нажми на модуль → выбери тему.")

def get_module_id(text: str) -> int | None:
    module_map = {
        "Модуль 0": 0, "Модуль 1": 1, "Модуль 2": 2, "Модуль 3": 3,
        "Модуль 4": 4, "Модуль 5": 5, "Модуль 6": 6, "Модуль 7": 7,
        "Модуль 8": 8, "Модуль 9": 9, "Модуль 10": 10, "Модуль 12": 12,
        "Модуль 13": 13, "Модуль 14": 14, "Проекты": 99
    }
    return module_map.get(text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if text == "Назад":
        reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        await update.message.reply_text("Выбери модуль:", reply_markup=reply_markup)
        return

    # Если это выбор модуля
    module_id = get_module_id(text)
    if module_id is not None:
        keyboard = get_module_keyboard(module_id)
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(f"📚 {text} — выбери тему:", reply_markup=reply_markup)
        return

    # Если это код темы
    code = text.split(':')[0].strip() if ':' in text else text
    topic = get_topic_by_code(code)
    if topic:
        filepath = os.path.join("content", topic['filepath'])
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            if len(content) > 4096:
                parts = [content[i:i+4096] for i in range(0, len(content), 4096)]
                for i, part in enumerate(parts, 1):
                    await update.message.reply_text(f"Часть {i}/{len(parts)}:\n\n{part}")
            else:
                await update.message.reply_text(content)
            register_user(update.effective_user.id, update.effective_user.full_name or "User")
            mark_completed(update.effective_user.id, code)
        else:
            await update.message.reply_text("Файл не найден.")
    else:
        await update.message.reply_text("Неизвестная команда. Используй меню.")

def run_bot():
    """Запуск Telegram-бота"""
    logger.info("🚀 Запуск Telegram-бота...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("✅ Бот готов к работе")
    app.run_polling()

# Flask-сервер для Render/Railway
app = Flask(__name__)

@app.route('/')
def health_check():
    return "DevOps Bot is running!", 200

if __name__ == "__main__":
    # Инициализация БД при запуске
    initialize_database()
    
    # Запуск бота в отдельном потоке
    bot_thread = Thread(target=run_bot)
    bot_thread.start()

    # Запуск веб-сервера
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)