# clean_md.py — улучшенная версия
import os
import re
import markdown
from bs4 import BeautifulSoup

INPUT_DIR = r"D:\work\TG_DevOps\content"
OUTPUT_DIR = r"D:\work\TG_DevOps\content_clean"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if not filename.endswith('.md'):
        continue

    with open(os.path.join(INPUT_DIR, filename), 'r', encoding='utf-8') as f:
        md_text = f.read()

    # 1. Удаляем фронтматтер (YAML-блоки)
    md_text = re.sub(r'^---.*?---\s*', '', md_text, flags=re.DOTALL | re.MULTILINE)

    # 2. Удаляем Markdown-разметку вручную (на случай, если markdown не справится)
    # Заголовки: # Заголовок → Заголовок
    md_text = re.sub(r'^#{1,6}\s*(.*)', r'\1', md_text, flags=re.MULTILINE)
    
    # Жирный и курсив: **текст** или __текст__ → текст
    md_text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', md_text)
    
    # Код в строке: `code` → code
    md_text = re.sub(r'`([^`]+)`', r'\1', md_text)
    
    # Горизонтальные линии
    md_text = re.sub(r'^\s*[-*_]{3,}\s*$', '', md_text, flags=re.MULTILINE)

    # 3. Конвертируем остатки через markdown → HTML → текст
    try:
        html = markdown.markdown(md_text)
        soup = BeautifulSoup(html, "html.parser")
        clean_text = soup.get_text(separator="\n", strip=True)
    except Exception:
        # Если markdown сломался — используем как есть
        clean_text = md_text

    # 4. Чистим лишние пустые строки
    clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)
    clean_text = clean_text.strip()

    # Сохраняем
    with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(clean_text)

print(f"✅ Очищено {len([f for f in os.listdir(INPUT_DIR) if f.endswith('.md')])} файлов → {OUTPUT_DIR}")