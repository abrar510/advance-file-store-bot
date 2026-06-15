from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

MONGO_URI = os.getenv("MONGO_URI")

FORCE_CHANNEL = int(os.getenv("FORCE_CHANNEL"))

CHANNEL_LINK = os.getenv("CHANNEL_LINK")

ADMINS = [int(x) for x in os.getenv("ADMINS").split(",")]

AUTO_DELETE_TIME = 600
