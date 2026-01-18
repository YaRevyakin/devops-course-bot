# database.py
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'devops_course',
    'user': 'devops',
    'password': 'securepass123'
}

CONTENT_DIR = r"D:\work\TG_DevOps\content_clean"

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_topic_by_code(code: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM topics WHERE code = %s", (code,))
    topic = cur.fetchone()
    cur.close()
    conn.close()
    return topic

def register_user(tg_id: int, full_name: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (tg_id, full_name) 
        VALUES (%s, %s) 
        ON CONFLICT (tg_id) DO NOTHING
    """, (tg_id, full_name))
    conn.commit()
    cur.close()
    conn.close()

def mark_completed(tg_id: int, topic_code: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO progress (tg_id, topic_code, completed, completed_at)
        VALUES (%s, %s, TRUE, NOW())
        ON CONFLICT (tg_id, topic_code) 
        DO UPDATE SET completed = TRUE, completed_at = NOW()
    """, (tg_id, topic_code))
    conn.commit()
    cur.close()
    conn.close()

# database.py — добавь эту функцию
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