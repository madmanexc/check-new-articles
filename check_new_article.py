import requests
from bs4 import BeautifulSoup
import os

URL = "https://example.com/blog"  # ← Замени на свой сайт
CHAT_ID = os.environ["CHAT_ID"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

def get_latest_title():
    html = requests.get(URL, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select_one("article h2 a")  # ← Подстрой под сайт
    return article.text.strip() if article else None

latest = get_latest_title()
if not latest:
    exit("❌ Не найдена статья")

state_path = "latest.txt"
if os.path.exists(state_path):
    with open(state_path) as f:
        prev = f.read().strip()
    if latest == prev:
        exit("✅ Без изменений")

with open(state_path, "w") as f:
    f.write(latest)

send_telegram(f"🆕 Новая статья: {latest}\n{URL}")
