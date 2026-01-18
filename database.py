import os
import psycopg2
import logging
from psycopg2.extras import RealDictCursor
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к БД через переменную окружения
DATABASE_URL = os.getenv("postgresql://postgres:GZfOrvNUQOAgebHShyHbnOutUsvJCZsL@postgres.railway.internal:5432/railway")

def get_db_connection():
    """Создаёт подключение к PostgreSQL через DATABASE_URL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("✅ Подключение к БД успешно")
        return conn
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к БД: {e}")
        raise

def create_tables_if_not_exists():
    """Создаёт таблицы, если их нет"""
    conn = get_db_connection()
    cur = conn.cursor()

    # Таблица пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            tg_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Таблица прогресса
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            tg_id INTEGER,
            topic_code TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (tg_id, topic_code),
            FOREIGN KEY (tg_id) REFERENCES users(tg_id) ON DELETE CASCADE
        );
    """)

    # Таблица тем
    cur.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id SERIAL PRIMARY KEY,
            module_id INTEGER NOT NULL,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            filepath TEXT NOT NULL,
            topic_order INTEGER DEFAULT 0
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

def populate_topics_from_structure():
    """Заполняет таблицу topics из DevOps Структура.md"""
    if not os.path.exists("DevOps Структура.md"):
        logger.warning("⚠️ Файл 'DevOps Структура.md' не найден")
        return

    with open("DevOps Структура.md", "r", encoding="utf-8") as f:
        lines = f.readlines()

    topics = []
    for line in lines:
        line = line.strip()
        if line.startswith("[[") and line.endswith("]]"):
            topic = line[2:-2]
            # Тема: m0t1_Что_такое_DevOps
            if topic.startswith("m") and "t" in topic:
                match = re.match(r"m(\d+)t(\d+)", topic)
                if match:
                    module_id = int(match.group(1))
                    topic_num = int(match.group(2))
                    title = topic.split("_", 1)[1].replace("_", " ").title()
                    filepath = f"module_{module_id}/{topic}.md"
                    topics.append((module_id, topic, title, filepath, topic_num))
            # Ключевые моменты: km0_Ключевые_моменты
            elif topic.startswith("km"):
                match = re.match(r"km(\d+)", topic)
                if match:
                    module_id = int(match.group(1))
                    title = topic.split("_", 1)[1].replace("_", " ").title()
                    filepath = f"module_{module_id}/{topic}.md"
                    topics.append((module_id, topic, title, filepath, 100))
            # Тест: testm0_Тестирование
            elif topic.startswith("testm"):
                match = re.match(r"testm(\d+)", topic)
                if match:
                    module_id = int(match.group(1))
                    title = topic.split("_", 1)[1].replace("_", " ").title()
                    filepath = f"module_{module_id}/{topic}.md"
                    topics.append((module_id, topic, title, filepath, 101))
            # Проекты: p0_Название
            elif topic.startswith("p"):
                match = re.match(r"p(\d+)", topic)
                if match:
                    module_id = int(match.group(1))
                    title = topic.split("_", 1)[1].replace("_", " ").title()
                    filepath = f"projects/{topic}.md"
                    topics.append((module_id, topic, title, filepath, 200))

    conn = get_db_connection()
    cur = conn.cursor()

    for t in topics:
        cur.execute("""
            INSERT INTO topics (module_id, code, title, filepath, topic_order)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (code) DO NOTHING;
        """, t)

    conn.commit()
    cur.close()
    conn.close()

def initialize_database():
    """Инициализирует БД: создаёт таблицы и заполняет темы"""
    create_tables_if_not_exists()
    populate_topics_from_structure()
    logger.info("✅ База данных инициализирована")

def register_user(tg_id: int, full_name: str):
    """Регистрирует или обновляет пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (tg_id, full_name)
        VALUES (%s, %s)
        ON CONFLICT (tg_id) DO UPDATE SET full_name = EXCLUDED.full_name;
    """, (tg_id, full_name))
    conn.commit()
    cur.close()
    conn.close()

def mark_completed(tg_id: int, topic_code: str):
    """Отмечает тему как пройденную"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO progress (tg_id, topic_code, completed_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (tg_id, topic_code)
        DO UPDATE SET completed_at = NOW();
    """, (tg_id, topic_code))
    conn.commit()
    cur.close()
    conn.close()

def get_topic_by_code(code: str):
    """Получает тему по коду"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM topics WHERE code = %s;", (code,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None

def get_module_keyboard(module_id: int):
    """Возвращает клавиатуру с темами модуля"""
    conn = get_db_connection()
    cur = conn.cursor()

    if module_id == 99:  # Проекты
        cur.execute("""
            SELECT title, code FROM topics
            WHERE module_id = 99
            ORDER BY topic_order;
        """)
    else:
        cur.execute("""
            SELECT title, code FROM topics
            WHERE module_id = %s
            ORDER BY topic_order;
        """, (module_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    buttons = []
    for i in range(0, len(rows), 2):  # По 2 кнопки в строке
        row = [f"{rows[i]['code']}: {rows[i]['title']}"]
        if i + 1 < len(rows):
            row.append(f"{rows[i+1]['code']}: {rows[i+1]['title']}")
        buttons.append(row)

    buttons.append(["Назад"])  # Кнопка "Назад"
    return buttons