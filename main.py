import requests
import time
from telegram import Bot

# --- CONFIGURA QUI ---
TELEGRAM_TOKEN = "8495082488:AAEOuLGh7x3Nxi9vRj7wPgq7NUU6GJ_rj74"
CHAT_ID = "365474662"

# Link JSON Vinted già pronti (prime 3 pagine "nike uomo")
VINTED_LINKS = [
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=1",
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=2",
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=3"
]

bot = Bot(token=TELEGRAM_TOKEN)
seen_ids = set()

def fetch_items(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("items", [])
    except Exception as e:
        print(f"Errore fetch: {e}")
        return []

def send_telegram(item):
    title = item.get("title")
    price = f"{item.get('price')} {item.get('currency')}"
    link = "https://www.vinted.it" + item.get("url")
    image = item.get("image_url")

    message = f"{title}\nPrezzo: {price}\nLink: {link}"
    try:
        bot.send_photo(chat_id=CHAT_ID, photo=image, caption=message)
        print(f"Inviato: {title}")
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

if __name__ == "__main__":
    print("🔄 Avvio monitoraggio Vinted...")
    while True:
        for url in VINTED_LINKS:
            items = fetch_items(url)
            for item in items:
                item_id = item.get("id")
                if item_id not in seen_ids:
                    send_telegram(item)
                    seen_ids.add(item_id)
        time.sleep(300)  # controlla ogni 5 minuti
