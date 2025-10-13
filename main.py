import os
from telegram import Bot

bot = Bot(token=os.environ.get("TELEGRAM_BOT_TOKEN"))
bot.send_message(chat_id=os.environ.get("TELEGRAM_CHAT_ID"), text="Test bot funzionante ✅")
