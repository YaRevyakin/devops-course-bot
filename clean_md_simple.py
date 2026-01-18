# clean_md_simple.py
import os
import re

INPUT_DIR = r"D:\work\TG_DevOps\content"
OUTPUT_DIR = r"D:\work\TG_DevOps\content_clean"

os.makedirs(OUTPUT_DIR, exist_ok=True)

md_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.md')]

for filename in md_files:
    with open(os.path.join(INPUT_DIR, filename), 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Удаляем YAML frontmatter
    text = re.sub(r'^---[\s\S]*?---\s*', '', text, flags=re.MULTILINE)

    # 2. Удаляем заголовки: # Заголовок → Заголовок
    text = re.sub(r'^#{1,6}\s*(.*)', r'\1', text, flags=re.MULTILINE)

    # 3. Удаляем жирный/курсив
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)

    # 4. Удаляем inline code
    text = re.sub(r'`([^`\n]+)`', r'\1', text)

    # 5. Удаляем блоки кода (включая ```bash)
    text = re.sub(r'```[\s\S]*?```', '', text)

    # 6. Удаляем цитаты
    text = re.sub(r'^>\s*(.*)', r'\1', text, flags=re.MULTILINE)

    # 7. Удаляем горизонтальные линии
    text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)

    # 8. Удаляем ссылки и изображения
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)      # [текст](ссылка)
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)          # ![alt](img)

    # 9. 🔥 УДАЛЯЕМ ТАБЛИЦЫ: любые строки, содержащие символ |
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Пропускаем строку, если она содержит | и состоит в основном из таблицы
        if '|' in line and not (stripped.startswith('|') and stripped.endswith('|')):
            continue
        if stripped.count('|') >= 2:  # даже если начинается с |, но это явно таблица
            continue
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)

    # 10. Чистим лишние пустые строки
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    # Сохраняем
    with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(text)

print(f"✅ Очищено {len(md_files)} файлов → {OUTPUT_DIR}")