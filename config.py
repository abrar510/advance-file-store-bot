import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

MONGO_URI = os.getenv("MONGO_URI")

ADMIN_ID = int(os.getenv("ADMIN_ID"))

FORCE_CHANNEL = int(os.getenv("FORCE_CHANNEL"))
STORE_CHANNEL = int(os.getenv("STORE_CHANNEL"))

CHANNEL_LINK = os.getenv("CHANNEL_LINK")

AUTO_DELETE_TIME = 600
