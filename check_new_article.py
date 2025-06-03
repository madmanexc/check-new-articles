import requests
from bs4 import BeautifulSoup
import os

BASE_URL = "https://feedback.minecraft.net"
SECTIONS = {
    "release": "https://feedback.minecraft.net/hc/en-us/sections/360001186971-Release-Changelogs",
    "preview": "https://feedback.minecraft.net/hc/en-us/sections/360001185332-Beta-and-Preview-Information-and-Changelogs",
}

CHAT_ID = os.environ["CHAT_ID"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print("❌ Ошибка при отправке в Telegram:", r.text)

def get_latest_article(section_key, url):
    print(f"🔍 Проверка раздела {section_key}: {url}")
    try:
        html = requests.get(url, timeout=15).text
    except Exception as e:
        print(f"❌ Ошибка при загрузке: {e}")
        return None
    
    # Сохраняем HTML-ответ для отладки
    with open(f"debug_{section_key}.html", "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    first_item = soup.select_one("ul.article-list li.article-list-item a.article-list-link")
    if not first_item:
        print(f"❌ Не удалось найти статью в разделе {section_key}")
        return None
    title = first_item.get_text(strip=True)
    link = BASE_URL + first_item["href"]
    print(f"✅ Найдена статья: {title} → {link}")
    return title, link

def load_last_ids():
    try:
        with open("latest.txt", "r", encoding="utf-8") as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        return set()

def save_ids(ids):
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(ids))

# Основная логика
previous_ids = load_last_ids()
current_ids = set()
new_articles = []

for key, section_url in SECTIONS.items():
    result = get_latest_article(key, section_url)
    if result:
        title, link = result
        current_ids.add(link)
        if link not in previous_ids:
            new_articles.append((title, link))

if new_articles:
    for title, link in new_articles:
        send_telegram(f"🆕 <b>{title}</b>\n{link}")
    save_ids(current_ids)
else:
    print("✅ Новых статей нет")
