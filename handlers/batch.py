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
