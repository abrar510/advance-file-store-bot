import os
import asyncio
import secrets
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient

# ======================
# CONFIG
# ======================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = int(os.getenv("OWNER_ID"))
STORE_CHANNEL = int(os.getenv("STORE_CHANNEL"))

MONGO_URL = os.getenv("MONGO_URI")

# ======================
# DATABASE
# ======================

mongo = AsyncIOMotorClient(MONGO_URL)
db = mongo["batch_bot"]
batches = db["batches"]

# ======================
# APP
# ======================

app = Client(
    "batch-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Active memory
active_batches = {}

# ======================
# START
# ======================

@app.on_message(filters.command("start"))
async def start(_, message):

    if len(message.command) == 1:
        return await message.reply("🤖 Bot is alive!")

    batch_id = message.command[1]

    data = await batches.find_one({"batch_id": batch_id})

    if not data:
        return await message.reply("❌ Invalid or expired link")

    sent_msgs = []

    for msg_id in data["files"]:
        try:
            msg = await app.copy_message(
                chat_id=message.chat.id,
                from_chat_id=STORE_CHANNEL,
                message_id=msg_id
            )
            sent_msgs.append(msg.id)
        except Exception as e:
            print("Send error:", e)

    if not sent_msgs:
        return await message.reply("❌ Failed to send files")

    await message.reply("📂 Files sent!\n⏳ Auto delete in 10 minutes. Please forward it to Saved Messages.")

    asyncio.create_task(auto_delete(message.chat.id, sent_msgs))


# ======================
# BATCH START
# ======================

@app.on_message(filters.command("batch") & filters.user(OWNER_ID))
async def batch(_, message):

    active_batches[message.from_user.id] = []

    await message.reply("📥 Send your files now...")


# ======================
# COLLECT FILES
# ======================

@app.on_message(
    filters.private &
    (filters.document | filters.video | filters.audio | filters.photo)
)
async def collect(_, message):

    uid = message.from_user.id

    if uid not in active_batches:
        return

    active_batches[uid].append(message)

    await message.reply("✅ File added")


# ======================
# DONE + GENERATE LINK
# ======================

@app.on_message(filters.command("done") & filters.user(OWNER_ID))
async def done(_, message):

    uid = message.from_user.id

    if uid not in active_batches:
        return await message.reply("❌ No active batch")

    files = active_batches[uid]

    if not files:
        return await message.reply("❌ No files found")

    await message.reply("⏳ Creating batch...")

    msg_ids = []

    for file in files:
        try:
            sent = await file.copy(STORE_CHANNEL)
            if sent:
                msg_ids.append(sent.id)
        except Exception as e:
            print("Copy error:", e)

    if not msg_ids:
        return await message.reply("❌ Upload failed to store channel")

    batch_id = secrets.token_urlsafe(8)

    await batches.insert_one({
        "batch_id": batch_id,
        "files": msg_ids
    })

    del active_batches[uid]

    me = await app.get_me()

    if not me.username:
        return await message.reply("❌ Bot username not set in BotFather")

    link = f"https://t.me/{me.username}?start={batch_id}"

    await message.reply(
        f"✅ Batch Created Successfully!\n\n🔗 {link}"
    )


# ======================
# AUTO DELETE SYSTEM
# ======================

async def auto_delete(chat_id, msg_ids):

    await asyncio.sleep(600)  # 10 minutes

    for mid in msg_ids:
        try:
            await app.delete_messages(chat_id, mid)
        except Exception as e:
            print("Delete error:", e)


# ======================
# RUN BOT
# ======================

app.run()
