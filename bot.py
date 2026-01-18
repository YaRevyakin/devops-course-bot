# bot.py
import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from database import get_topic_by_code, register_user, mark_completed, CONTENT_DIR, get_db_connection

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

BOT_TOKEN = "8226360790:AAH7DPXxvUinXEKnQBub7zExNb9uNkzaC78"

# Основное меню: выбор модуля
MAIN_MENU = [
    ["Модуль 0", "Модуль 1", "Модуль 2"],
    ["Модуль 3", "Модуль 4", "Модуль 5"],
    ["Модуль 6", "Модуль 7", "Модуль 8"],
    ["Модуль 9", "Модуль 10", "Модуль 12"],
    ["Модуль 13", "Модуль 14", "Проекты"],
    ["/help"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.full_name)
    reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        f"Привет, {user.full_name}! 👋\nВыбери модуль:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Нажми на модуль → выбери тему.")

# Отправка темы по коду
async def send_topic_by_code(update, code):
    topic = get_topic_by_code(code)
    if not topic:
        await update.message.reply_text(f"Тема `{code}` не найдена.")
        return

    filepath = os.path.join(CONTENT_DIR, topic['filepath'])
    if not os.path.exists(filepath):
        await update.message.reply_text("Файл не найден.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    if len(content) > 4096:
        parts = [content[i:i+4096] for i in range(0, len(content), 4096)]
        for i, part in enumerate(parts, 1):
            await update.message.reply_text(f"Часть {i}/{len(parts)}:\n\n{part}")
    else:
        await update.message.reply_text(content)

    user = update.effective_user
    register_user(user.id, user.full_name)
    mark_completed(user.id, code)

# Получить темы модуля и сформировать клавиатуру
def get_module_keyboard(module_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if module_id == 99:  # Проекты
        cur.execute("""
            SELECT code, title FROM topics 
            WHERE code IN ('final_project', 'roadmap')
            ORDER BY code
        """)
    else:
        cur.execute("""
            SELECT code, title FROM topics 
            WHERE module = %s 
            ORDER BY 
                CASE type 
                    WHEN 'topic' THEN 1
                    WHEN 'practice' THEN 2
                    WHEN 'keypoints' THEN 3
                    WHEN 'test' THEN 4
                END,
                code
        """, (module_id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return [["Назад"]]

    # Группируем по 2 кнопки в строке
    buttons = []
    row = []
    for code, title in rows:
        label = f"{code}: {title[:20]}..." if len(title) > 20 else f"{code}: {title}"
        row.append(label)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append(["Назад"])
    return buttons

# Обработка всех текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Команда "Назад"
    if text == "Назад":
        reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        await update.message.reply_text("Выбери модуль:", reply_markup=reply_markup)
        return

    # Если это модуль
    module_map = {
        "Модуль 0": 0, "Модуль 1": 1, "Модуль 2": 2, "Модуль 3": 3,
        "Модуль 4": 4, "Модуль 5": 5, "Модуль 6": 6, "Модуль 7": 7,
        "Модуль 8": 8, "Модуль 9": 9, "Модуль 10": 10, "Модуль 12": 12,
        "Модуль 13": 13, "Модуль 14": 14, "Проекты": 99
    }

    if text in module_map:
        module_id = module_map[text]
        keyboard = get_module_keyboard(module_id)
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(f"📚 {text} — выбери тему:", reply_markup=reply_markup)
        return

    # Если это тема (в формате "m0t1: Название" или просто "m0t1")
    if ':' in text:
        code = text.split(':')[0].strip()
    else:
        code = text

    # Проверяем, существует ли такая тема
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM topics WHERE code = %s", (code,))
    exists = cur.fetchone()
    conn.close()

    if exists:
        await send_topic_by_code(update, code)
    else:
        await update.message.reply_text("Неизвестная команда. Используй меню.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен с reply-кнопками...")
    app.run_polling()

if __name__ == "__main__":
    main()