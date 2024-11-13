from os import getenv
from dotenv import load_dotenv

load_dotenv()

DISCORD_API_TOKEN = getenv("DISCORD_API_TOKEN")
ADMIN_CHANNEL_ID = int(getenv("ADMIN_CHANNEL_ID") or 0)

DB_URL = getenv("DB_URL")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_PASS = getenv("DB_PASS")
Gemini_API_Key = getenv("Gemini_API_Key")