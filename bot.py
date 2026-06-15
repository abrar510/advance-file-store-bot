# bot.py

import os
import asyncio
import secrets

from pyrogram import Client, filters
from pyrogram.types import (
InlineKeyboardMarkup,
InlineKeyboardButton
)
from pyrogram.errors import UserNotParticipant
from motor.motor_asyncio import AsyncIOMotorClient

# =========================

# CONFIG

# =========================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = int(os.getenv("OWNER_ID"))

STORE_CHANNEL = int(os.getenv("STORE_CHANNEL"))
FORCE_CHANNEL = int(os.getenv("FORCE_CHANNEL"))

MONGO_URI = os.getenv("MONGO_URI")

CHANNEL_LINK = os.getenv(
"CHANNEL_LINK",
"https://t.me/your_channel"
)

AUTO_DELETE_TIME = 600  # 10 minutes

# =========================

# DATABASE

# =========================

mongo = AsyncIOMotorClient(MONGO_URI)

db = mongo["batch_bot"]

batches = db["batches"]

# =========================

# BOT

# =========================

app = Client(
"batch_bot",
api_id=API_ID,
api_hash=API_HASH,
bot_token=BOT_TOKEN
)

# =========================

# MEMORY

# =========================

active_batches = {}

# =========================

# FORCE JOIN CHECK

# =========================

async def check_join(user_id):

try:
    member = await app.get_chat_member(
        FORCE_CHANNEL,
        user_id
    )

    if member.status in [
        "left",
        "kicked"
    ]:
        return False

    return True

except UserNotParticipant:
    return False

except Exception:
    return False

# =========================

# AUTO DELETE

# =========================

async def auto_delete(
chat_id,
message_ids
):

await asyncio.sleep(
    AUTO_DELETE_TIME
)

try:
    await app.delete_messages(
        chat_id,
        message_ids
    )

except Exception as e:
    print(
        "Delete Error:",
        e
    )

# =========================

# SEND BATCH

# =========================

async def send_batch(
message,
batch_id
):

data = await batches.find_one(
    {
        "batch_id": batch_id
    }
)

if not data:

    return await message.reply(
        "❌ Invalid or expired link."
    )

sent_messages = []

for msg_id in data["files"]:

    try:

        sent = await app.copy_message(
            chat_id=message.chat.id,
            from_chat_id=STORE_CHANNEL,
            message_id=msg_id
        )

        sent_messages.append(
            sent.id
        )

    except Exception as e:

        print(
            "Copy Error:",
            e
        )

if not sent_messages:

    return await message.reply(
        "❌ Failed to send files."
    )

await message.reply(
    "📂 Files Sent Successfully!\n\n"
    "⏳ Auto Delete In 10 Minutes.\n"
    "⚠️ Forward To Saved Messages."
)

asyncio.create_task(
    auto_delete(
        message.chat.id,
        sent_messages
    )
)

# =========================

# START

# =========================

@app.on_message(
filters.command("start")
)
async def start(
client,
message
):

if len(message.command) == 1:

    return await message.reply(
        "🤖 Bot Is Alive!"
    )

batch_id = message.command[1]

joined = await check_join(
    message.from_user.id
)

if not joined:

    return await message.reply(
        "⚠️ You have to join our channel first.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 Join Channel",
                        url=CHANNEL_LINK
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ Try Again",
                        callback_data=f"check_{batch_id}"
                    )
                ]
            ]
        )
    )

await send_batch(
    message,
    batch_id
)

# =========================

# TRY AGAIN

# =========================

@app.on_callback_query(
filters.regex("^check_")
)
async def try_again(
client,
query
):

batch_id = query.data.split(
    "_",
    1
)[1]

joined = await check_join(
    query.from_user.id
)

if not joined:

    return await query.answer(
        "❌ Please join channel first.",
        show_alert=True
    )

await query.message.delete()

await send_batch(
    query.message,
    batch_id
)

await query.answer(
    "✅ Access Granted"
)

# =========================

# CREATE BATCH

# =========================

@app.on_message(
filters.command("batch")
& filters.user(OWNER_ID)
)
async def batch(
client,
message
):

active_batches[
    message.from_user.id
] = []

await message.reply(
    "📥 Send your files now..."
)

# =========================

# COLLECT FILES

# =========================

@app.on_message(
filters.private
& (
filters.document
| filters.video
| filters.audio
| filters.photo
)
)
async def collect(
client,
message
):

uid = message.from_user.id

if uid not in active_batches:
    return

active_batches[uid].append(
    message
)

await message.reply(
    "✅ File Added"
)

# =========================

# DONE

# =========================

@app.on_message(
filters.command("done")
& filters.user(OWNER_ID)
)
async def done(
client,
message
):

uid = message.from_user.id

if uid not in active_batches:

    return await message.reply(
        "❌ No Active Batch."
    )

files = active_batches[uid]

if not files:

    return await message.reply(
        "❌ No Files Found."
    )

await message.reply(
    "⏳ Creating Batch..."
)

msg_ids = []

for file in files:

    try:

        stored = await file.copy(
            STORE_CHANNEL
        )

        msg_ids.append(
            stored.id
        )

    except Exception as e:

        print(
            "Store Error:",
            e
        )

if not msg_ids:

    return await message.reply(
        "❌ Upload Failed."
    )

batch_id = secrets.token_urlsafe(
    8
)

await batches.insert_one(
    {
        "batch_id": batch_id,
        "files": msg_ids
    }
)

del active_batches[uid]

me = await app.get_me()

link = (
    f"https://t.me/"
    f"{me.username}"
    f"?start={batch_id}"
)

await message.reply(
    "✅ Batch Created Successfully!\n\n"
    f"🔗 {link}"
)

# =========================

# RUN

# =========================

print("Bot Started...")

app.run()
