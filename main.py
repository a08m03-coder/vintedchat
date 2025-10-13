import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# Legge i token dalle environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# Lista dei link di ricerca Vinted da monitorare
VINTED_LINKS = [
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=1",
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=2"
]

# Headers realistici per evitare il 403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9",
    "Accept": "application/json",
}

# Memorizza gli ID già inviati per evitare duplicati
seen_items = set()

def fetch_vinted(link):
    try:
        response = requests.get(link, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        print(f"[ERROR] Errore HTTP fetch: {e} su {link}")
        return None
    except Exception as e:
        print(f"[ERROR] Errore generico fetch: {e} su {link}")
        return None

def process_items(data):
    if not data or "items" not in data:
        return []

    new_items = []
    for item in data["items"]:
        item_id = item.get("id")
        if item_id in seen_items:
            continue
        seen_items.add(item_id)

        title = item.get("title", "Senza titolo")
        price = item.get("price", {}).get("amount", "N/A")
        currency = item.get("price", {}).get("currency", "€")
        url = f"https://www.vinted.it/item/{item_id}"
        image = item.get("photos", [{}])[0].get("url", "")

        new_items.append({
            "title": title,
            "price": f"{price} {currency}",
            "url": url,
            "image": image
        })
    return new_items

def send_telegram(items):
    for item in items:
        message = f"{item['title']}\nPrezzo: {item['price']}\nLink: {item['url']}"
        if item["image"]:
            bot.send_photo(chat_id=CHAT_ID, photo=item["image"], caption=message)
        else:
            bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    print("🔄 Avvio monitoraggio Vinted...")
    while True:
        for link in VINTED_LINKS:
            print(f"Controllo {link}")
            data = fetch_vinted(link)
            new_items = process_items(data)
            if new_items:
                send_telegram(new_items)
                print(f"[INFO] Inviati {len(new_items)} nuovi articoli")
            else:
                print(f"[WARNING] Nessun articolo trovato su {link}")
        print("[INFO] Attesa 5 minuti prima del prossimo controllo...")
        time.sleep(300)  # 5 minuti

if __name__ == "__main__":
    # Test rapido bot
    try:
        bot.send_message(chat_id=CHAT_ID, text="Test bot funzionante ✅")
    except Exception as e:
        print(f"[ERROR] Errore invio test Telegram: {e}")
    main()
