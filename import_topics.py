# import_topics.py (упрощённая версия)
import re
import psycopg2

STRUCTURE_FILE = r"D:\work\TG_DevOps\DevOps Структура.md"

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'devops_course',
    'user': 'devops',
    'password': 'securepass123'
}

def get_type(code):
    if code.startswith('m') and 't' in code:
        return 'topic'
    elif code.startswith('p'):
        return 'practice'
    elif code.startswith('km'):
        return 'keypoints'
    elif code.startswith('test'):
        return 'test'
    elif code == 'final_project':
        return 'practice'
    elif code == 'roadmap':
        return 'topic'
    else:
        return 'topic'

def get_module(code):
    if code.startswith('m') and 't' in code:
        try:
            return int(code[1:code.index('t')])
        except:
            return 99
    elif code.startswith(('p', 'km', 'test')):
        nums = re.findall(r'\d+', code)
        return int(nums[0]) if nums else 99
    elif code == 'final_project':
        return 11
    else:
        return 99

def main():
    with open(STRUCTURE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    links = re.findall(r'\[\[(.*?)\]\]', content)
    seen = set()
    unique_links = []
    for link in links:
        clean = link.rstrip('.md')
        if clean not in seen:
            seen.add(clean)
            unique_links.append(clean)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("DELETE FROM progress")
    cur.execute("DELETE FROM topics")

    for filename in unique_links:
        parts = filename.split('_', 1)
        if len(parts) < 2:
            print(f"Пропускаю: {filename}")
            continue

        code = parts[0]
        title = parts[1]
        topic_type = get_type(code)
        module = get_module(code)
        filepath = f"{filename}.md"

        try:
            cur.execute("""
                INSERT INTO topics (code, title, module, type, filepath)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (code) DO NOTHING
            """, (code, title, module, topic_type, filepath))
        except Exception as e:
            print(f"Ошибка при {code}: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Готово! Вставлено {len(unique_links)} записей.")

if __name__ == "__main__":
    main()