import os
import requests
import time
import logging
import json
from telegram import Bot

# --- Configurazione logging dettagliato ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Variabili d'ambiente Telegram ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not CHAT_ID:
    logging.error("Devi impostare TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID su Render")
    raise ValueError("Variabili d'ambiente mancanti")

bot = Bot(token=TELEGRAM_TOKEN)

# --- Link JSON Vinted ---
VINTED_LINKS = [
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=1",
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=2",
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=3"
]

# --- File dove salvare gli ID già inviati ---
SEEN_FILE = "seen_ids.json"

# --- Carica gli ID già inviati ---
if os.path.exists(SEEN_FILE):
    try:
        with open(SEEN_FILE, "r") as f:
            seen_ids = set(json.load(f))
        logging.info(f"Caricati {len(seen_ids)} ID già inviati dal file")
    except Exception as e:
        logging.error(f"Errore caricamento seen_ids: {e}")
        seen_ids = set()
else:
    seen_ids = set()

def save_seen_ids():
    try:
        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen_ids), f)
        logging.info(f"Salvati {len(seen_ids)} ID inviati")
    except Exception as e:
        logging.error(f"Errore salvataggio seen_ids: {e}")

def fetch_items(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        items = data.get("items", [])
        logging.info(f"Fetch completato: {len(items)} articoli trovati su {url}")
        return items
    except requests.RequestException as e:
        logging.error(f"Errore HTTP fetch: {e} su {url}")
        return []
    except ValueError as e:
        logging.error(f"Errore parsing JSON: {e} su {url}")
        return []

def send_telegram(item):
    try:
        item_id = item.get("id")
        if not item_id:
            logging.warning("Articolo senza ID, salto")
            return

        title = item.get("title") or "Nessun titolo"
        price = f"{item.get('price', '0')} {item.get('currency', '')}"
        link_path = item.get("url")
        image = item.get("image_url")

        if not link_path:
            logging.warning(f"Articolo {item_id} senza URL, salto")
            return
        if not image:
            logging.warning(f"Articolo {item_id} senza immagine, salto")
            return

        link = "https://www.vinted.it" + link_path
        message = f"{title}\nPrezzo: {price}\nLink: {link}"

        bot.send_photo(chat_id=CHAT_ID, photo=image, caption=message)
        logging.info(f"Inviato articolo {item_id}: {title}")
    except Exception as e:
        logging.error(f"Errore invio Telegram: {e}")

if __name__ == "__main__":
    logging.info("🔄 Avvio monitoraggio Vinted...")
    while True:
        for url in VINTED_LINKS:
            items = fetch_items(url)
            if not items:
                logging.warning(f"Nessun articolo trovato su {url}")
            for item in items:
                item_id = item.get("id")
                if item_id and item_id not in seen_ids:
                    send_telegram(item)
                    seen_ids.add(item_id)
                    save_seen_ids()  # salva subito dopo invio
        logging.info("Attesa 5 minuti prima del prossimo controllo...")
        time.sleep(300)  # 5 minuti
