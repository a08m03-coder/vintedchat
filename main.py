import requests
import time
import os
import threading
from flask import Flask

# --- CONFIGURAZIONE ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# LINK DI RICERCA VINTED (puoi metterne più di uno)
VINTED_LINKS = [
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=1",
]

SEEN_IDS = set()  # articoli già inviati

# --- FUNZIONI ---
def send_telegram_message(text, image_url=None):
    """Invia un messaggio Telegram con testo e immagine."""
    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    photo_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

    try:
        if image_url:
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": text, "parse_mode": "Markdown"}
            files = {"photo": requests.get(image_url).content}
            resp = requests.post(photo_url, data=data, files=files, timeout=10)
        else:
            data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
            resp = requests.post(send_url, data=data, timeout=10)
        print(f"Invio Telegram: {resp.status_code} - {resp.text[:50]}")
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def get_vinted_items_json(url):
    """Scarica articoli usando l'API JSON interna di Vinted."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "it-IT,it;q=0.9",
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"Errore caricamento {url}: {e}")
        return []

    items = []

    try:
        data = r.json()  # se il link restituisce JSON
        # Vinted spesso invia JSON dentro 'items' o 'search_items'
        search_items = data.get('items') or data.get('search_items') or []
        for item in search_items:
            item_id = str(item.get('id'))
            title = item.get('title') or "Senza titolo"
            price = item.get('price') or "N/A"
            url_link = "https://www.vinted.it" + item.get('url', '/')
            image_url = item.get('photo', {}).get('url') or None
            items.append({"id": item_id, "title": title, "price": price, "url": url_link, "image": image_url})
    except Exception:
        # fallback: se non JSON, ignora e stampa errore
        print("❌ Non è JSON valido o struttura diversa")

    return items

def main():
    # messaggio test all’avvio
    send_telegram_message("✅ Test Telegram: il bot è attivo e pronto a inviare articoli!")
    print("🔄 Avvio monitoraggio Vinted...")

    while True:
        for url in VINTED_LINKS:
            print(f"Controllo {url}")
            items = get_vinted_items_json(url)
            print(f"Trovati {len(items)} articoli JSON su {url}")

            for item in items:
                if item["id"] not in SEEN_IDS:
                    SEEN_IDS.add(item["id"])
                    message = f"🧢 *{item['title']}*\n💶 {item['price']}\n🔗 {item['url']}"
                    send_telegram_message(message, item["image"])
                    print(f"Inviato: {item['title']} - {item['price']}")

        time.sleep(300)  # ogni 5 minuti

# --- SERVER FLASK PER RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Vinted Watcher API JSON attivo"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# --- AVVIO ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    main()
