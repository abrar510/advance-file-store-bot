from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
"FileStoreBot",
api_id=API_ID,
api_hash=API_HASH,
bot_token=BOT_TOKEN
)

import handlers.start
import handlers.files
import handlers.batch
import handlers.broadcast
import handlers.admin

print("Bot Started...")

app.run()
