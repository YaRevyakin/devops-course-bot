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