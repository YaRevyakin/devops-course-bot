# database.py
import os
import psycopg2
import logging
from psycopg2.extras import RealDictCursor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к БД через переменные окружения (для Render)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'devops_course'),
    'user': os.getenv('DB_USER', 'devops'),
    'password': os.getenv('DB_PASSWORD', 'securepass123')
}

# Путь к папке с чистым контентом
CONTENT_DIR = os.path.join(os.path.dirname(__file__), 'content_clean')

def get_db_connection():
    """Создаёт подключение к PostgreSQL"""
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
        INSERT INTO progress (tg_id, topic_code, completed, completed_at)
        VALUES (%s, %s, TRUE, NOW())
        ON CONFLICT (tg_id, topic_code) 
        DO UPDATE SET completed = TRUE, completed_at = NOW();
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
    cur.close()
    conn.close()

    if not rows:
        return [["Назад"]]

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