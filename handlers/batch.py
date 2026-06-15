import secrets

from pyrogram import filters

from bot import app
from config import ADMINS
from database import batches

active_batches = {}

# ---------------------
# START BATCH
# ---------------------

@app.on_message(
    filters.command("batch")
    & filters.user(ADMINS)
)
async def batch_start(
    client,
    message
):

    active_batches[
        message.from_user.id
    ] = []

    await message.reply(
        "Send all files now.\n\n"
        "When finished send /done"
    )
# --------------------
# SEND FILES
# --------------------

async def send_batch_files(
    client,
    chat_id,
    batch_id
):

    batch = await batches.find_one(
        {
            "_id": batch_id
        }
    )

    if not batch:

        return await client.send_message(
            chat_id,
            "Batch not found."
        )

    sent_messages = []

    for file in batch["files"]:

        try:

            msg = await client.send_cached_media(
                chat_id,
                file["file_id"]
            )

            sent_messages.append(
                msg.id
            )

        except:
            pass

    note = await client.send_message(
        chat_id,
        "Your files will be deleted within 10 minutes so forward it to saved messages."
    )

    sent_messages.append(
        note.id
    )

    asyncio.create_task(
        auto_delete(
            client,
            chat_id,
            sent_messages
        )
    )

# ---------------------
# COLLECT FILES
# ---------------------

@app.on_message(
    filters.private
    & filters.user(ADMINS)
)
async def collect_files(
    client,
    message
):

    uid = message.from_user.id

    if uid not in active_batches:
        return

    file_id = None

    if message.document:

        file_id = (
            message.document.file_id
        )

    elif message.video:

        file_id = (
            message.video.file_id
        )

    elif message.audio:

        file_id = (
            message.audio.file_id
        )

    elif message.photo:

        file_id = (
            message.photo.file_id
        )

    if not file_id:
        return

    active_batches[uid].append(
        {
            "file_id": file_id
        }
    )

    await message.reply(
        "File Added"
    )

# ---------------------
# DONE
# ---------------------

@app.on_message(
    filters.command("done")
    & filters.user(ADMINS)
)
async def batch_done(
    client,
    message
):

    uid = message.from_user.id

    if uid not in active_batches:

        return await message.reply(
            "No active batch."
        )

    files = active_batches[uid]

    if len(files) == 0:

        return await message.reply(
            "No files received."
        )

    code = secrets.token_urlsafe(8)

    await batches.insert_one(
        {
            "_id": code,
            "files": files
        }
    )

    del active_batches[uid]

    me = await client.get_me()

    link = (
        f"https://t.me/"
        f"{me.username}"
        f"?start=batch_{code}"
    )

    await message.reply(
        f"Batch Created\n\n{link}"
    )
import asyncio

from database import batches
from utils.auto_delete import auto_delete


async def send_batch_files(
    client,
    chat_id,
    batch_id
):

    batch = await batches.find_one(
        {"_id": batch_id}
    )

    if not batch:
        return await client.send_message(
            chat_id,
            "Batch not found."
        )

    sent_messages = []

    for file in batch["files"]:

        try:
            msg = await client.send_cached_media(
                chat_id,
                file["file_id"]
            )

            sent_messages.append(
                msg.id
            )

        except Exception:
            pass

    note = await client.send_message(
        chat_id,
        "Your files will be deleted within 10 minutes so forward it to saved messages."
    )

    sent_messages.append(note.id)

    asyncio.create_task(
        auto_delete(
            client,
            chat_id,
            sent_messages
        )
    )
