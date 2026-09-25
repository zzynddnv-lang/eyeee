import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# Bot tokeni
BOT_TOKEN = os.getenv("BOT_TOKEN", "8539604514:AAGz3fFAI1WHOYFkyS0SAk74RMs00bjh1es")

# Render platformasi taqdim etadigan port
PORT = int(os.getenv("PORT", 8080))

# Yuklab olingan fayllar vaqtinchalik saqlanadigan papka
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
