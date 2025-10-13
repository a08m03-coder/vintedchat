import os
import asyncio
import requests
from telegram import Bot, constants

# Prendi le variabili d'ambiente
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("⚠️ Imposta TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID nelle Environment Variables")
    exit(1)

bot = Bot(token=BOT_TOKEN)

# Lista di link Vinted da monitorare
VINTED_LINKS = [
    "https://www.vinted.it/api/v2/catalog/items?search_text=nike%20uomo&page=1"
]

async def invia_messaggio(testo):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=testo, parse_mode=constants.ParseMode.HTML)
    except Exception as e:
        print(f"Errore invio messaggio: {e}")

async def fetch_articoli(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        dati = r.json()
        articoli = []
        for item in dati.get("items", []):
            titolo = item.get("title")
            prezzo = item.get("price", {}).get("amount")
            link = f"https://www.vinted.it/item/{item.get('id')}"
            articoli.append(f"{titolo} - {prezzo}€\n{link}")
        return articoli
    except requests.exceptions.HTTPError as e:
        print(f"🚫 Errore HTTP fetch: {e} su {url}")
        return []
    except Exception as e:
        print(f"🚫 Errore generico: {e} su {url}")
        return []

async def monitoraggio():
    inviati = set()
    print("🔄 Avvio monitoraggio Vinted...")
    while True:
        for url in VINTED_LINKS:
            articoli = await fetch_articoli(url)
            nuovi = [a for a in articoli if a not in inviati]
            for art in nuovi:
                await invia_messaggio(art)
                inviati.add(art)
        print("⏱ Attesa 5 minuti prima del prossimo controllo...")
        await asyncio.sleep(300)  # 5 minuti

if __name__ == "__main__":
    asyncio.run(monitoraggio())
