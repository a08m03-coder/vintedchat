import requests
import time
import os
import threading
from bs4 import BeautifulSoup
from flask import Flask

# --- CONFIGURAZIONE ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# LINK DI RICERCA VINTED
VINTED_LINKS = [
    "https://www.vinted.it/catalog?search_text=nike%20uomo&currency=EUR&order=newest_first&size_ids[]=208&page=1",
]

# --- MEMORIA ARTICOLI VISTI ---
SEEN_IDS = set()

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
        print(f"Invio Telegram risposta: {resp.status_code} - {resp.text[:50]}")
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def get_vinted_items(url):
    """Scarica e restituisce gli articoli da una ricerca Vinted."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "it-IT,it;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Errore caricamento {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    items = []

    # 🔹 Stampiamo TUTTI i div per debug
    divs = soup.find_all("div")
    print(f"Numero totale div nella pagina: {len(divs)}")

    # Selettori originali
    for item in soup.select("div[data-testid='item'] a[href^='/items/']"):
        link = "https://www.vinted.it" + item["href"]
        title_tag = item.select_one("h3")
        price_tag = item.select_one("span[data-testid='price']")
        img_tag = item.select_one("img")

        if not title_tag or not price_tag:
            continue

        item_id = link.split("/")[-1]
        title = title_tag.text.strip()
        price = price_tag.text.strip()
        image_url = img_tag["src"] if img_tag else None

        items.append({"id": item_id, "title": title, "price": price, "url": link, "image": image_url})

    print(f"Trovati {len(items)} articoli con il selettore attuale.")
    return items

def main():
    # --- MESSAGGIO DI TEST TELEGRAM ---
    send_telegram_message("✅ Test Telegram: il bot è attivo!")
    print("🔄 Avvio monitoraggio Vinted...")

    while True:
        for url in VINTED_LINKS:
            print(f"Controllo {url}")
            items = get_vinted_items(url)

            for i, item in enumerate(items, start=1):
                if item["id"] not in SEEN_IDS:
                    SEEN_IDS.add(item["id"])
                    message = f"🧢 *{item['title']}*\n💶 {item['price']}\n🔗 {item['url']}"
                    send_telegram_message(message, item["image"])
                    print(f"{i}. Inviato: {item['title']} - {item['price']}")

        time.sleep(300)  # ogni 5 minuti

# --- SERVER FLASK PER RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Vinted Watcher attivo e funzionante"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# --- AVVIO ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    main()
