import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в .env")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY не задан в .env")
