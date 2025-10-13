import os
import time
import requests
import telegram

# Lista dei link JSON di Vinted
VINTED_LINKS = [
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=1",
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=2",
]

# Telegram bot
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = telegram.Bot(token=BOT_TOKEN)

# Memorizza gli ID già inviati
seen_ids = set()

def fetch_items(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("items", [])
    except Exception as e:
        print(f"Errore fetch: {e}")
        return []

def send_telegram(item):
    text = f"{item['title']}\nPrezzo: {item['price']} {item['currency']}\nLink: {item['url']}"
    bot.send_photo(chat_id=CHAT_ID, photo=item['image_url'], caption=text)

while True:
    print("🔄 Controllo nuovi articoli...")
    for link in VINTED_LINKS:
        items = fetch_items(link)
        for item in items:
            if item['id'] not in seen_ids:
                try:
                    send_telegram(item)
                    seen_ids.add(item['id'])
                    print(f"Inviato: {item['title']}")
                except Exception as e:
                    print(f"Errore invio Telegram: {e}")
    time.sleep(300)  # 5 minuti
