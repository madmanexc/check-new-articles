import os
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SECTIONS = {
    "release": "https://feedback.minecraft.net/hc/en-us/sections/360001186971-Release-Changelogs",
    "preview": "https://feedback.minecraft.net/hc/en-us/sections/360001185332-Beta-and-Preview-Information-and-Changelogs",
}
BASE_URL = "https://feedback.minecraft.net"

def send_telegram(message):
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print("❌ Ошибка Telegram:", r.text)

def load_last_ids():
    try:
        with open("latest.txt", "r", encoding="utf-8") as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        return set()

def save_ids(ids):
    with open("latest.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(ids))

def run():
    previous_ids = load_last_ids()
    current_ids = set()
    new_articles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for name, url in SECTIONS.items():
            print(f"🌐 Открываю {name}: {url}")
            try:
                page.goto(url, timeout=20000)
                page.wait_for_selector("ul.article-list", timeout=15000)
                link = page.query_selector("ul.article-list li.article-list-item a.article-list-link")
                if link:
                    title = link.inner_text().strip()
                    href = BASE_URL + link.get_attribute("href")
                    print(f"✅ Найдена статья: {title}")
                    current_ids.add(href)
                    if href not in previous_ids:
                        new_articles.append((title, href))
                else:
                    print(f"❌ Не найден элемент a.article-list-link в разделе {name}")
            except Exception as e:
                print(f"❌ Ошибка при загрузке {name}: {e}")

        browser.close()

    if new_articles:
        for title, link in new_articles:
            send_telegram(f"🆕 <b>{title}</b>\n{link}")
        save_ids(current_ids)
    else:
        print("✅ Новых статей нет")

if __name__ == "__main__":
    run()
