import os
import psycopg2
import logging
from psycopg2.extras import RealDictCursor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к БД через отдельные параметры
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'dpg-d5m55u63jp1c739rt8lg-a.frankfurt-postgres.render.com'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'devops_course_db'),
    'user': os.getenv('DB_USER', 'devops_course_db_user'),
    'password': os.getenv('DB_PASSWORD', 'XxUp5L0WvQOyt415mPf6yBzxpILEl7HX')
}

def get_db_connection():
    """Создаёт подключение к PostgreSQL через параметры"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("✅ Подключение к БД успешно")
        return conn
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к БД: {e}")
        raise

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