import requests
import time
import os
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Puoi aggiungere più link di ricerca Vinted qui:
VINTED_LINKS = [
    "https://www.vinted.it/catalog?search_text=nike%20uomo&size_ids[]=208&page=1&time=1760365096&price_to=100&currency=EUR&order=newest_first",
    # aggiungi altri link se vuoi
]

# Per salvare gli ID già visti
SEEN_IDS = set()

def send_telegram_message(text, image_url=None):
    """Invia un messaggio Telegram con testo e immagine."""
    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    photo_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

    if image_url:
        data = {"chat_id": TELEGRAM_CHAT_ID, "caption": text}
        files = {"photo": requests.get(image_url).content}
        requests.post(photo_url, data=data, files=files)
    else:
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
        requests.post(send_url, data=data)

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
        print(f"Errore nel caricamento di {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    items = []
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
    return items

def main():
    print("🔄 Avvio monitoraggio Vinted...")
    while True:
        for url in VINTED_LINKS:
            print(f"Controllo {url}")
            items = get_vinted_items(url)
            for item in items:
                if item["id"] not in SEEN_IDS:
                    SEEN_IDS.add(item["id"])
                    message = f"🧢 *{item['title']}*\n💶 {item['price']}\n🔗 {item['url']}"
                    send_telegram_message(message, item["image"])
        time.sleep(300)  # ogni 5 minuti

if __name__ == "__main__":
    main()
