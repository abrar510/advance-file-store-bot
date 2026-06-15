from pyrogram import filters

from bot import app
from config import ADMINS
from database import users, batches


@app.on_message(filters.command("ping") & filters.user(ADMINS))
async def ping_cmd(client, message):

    await message.reply(
        "Pong!"
    )


@app.on_message(filters.command("users") & filters.user(ADMINS))
async def users_cmd(client, message):

    total = await users.count_documents({})

    await message.reply(
        f"Total Users: {total}"
    )


@app.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_cmd(client, message):

    total_users = await users.count_documents({})

    total_batches = await batches.count_documents({})

    text = (
        f"Users: {total_users}\n"
        f"Batches: {total_batches}"
    )

    await message.reply(text)


@app.on_message(filters.command("deletebatch") & filters.user(ADMINS))
async def delete_batch(client, message):

    if len(message.command) < 2:

        return await message.reply(
            "/deletebatch batch_id"
        )

    batch_id = message.command[1]

    result = await batches.delete_one(
        {
            "_id": batch_id
        }
    )

    if result.deleted_count:

        await message.reply(
            "Batch Deleted"
        )

    else:

        await message.reply(
            "Batch Not Found"
        )


@app.on_message(filters.command("batchinfo") & filters.user(ADMINS))
async def batch_info(client, message):

    if len(message.command) < 2:

        return

    batch_id = message.command[1]

    batch = await batches.find_one(
        {
            "_id": batch_id
        }
    )

    if not batch:

        return await message.reply(
            "Batch Not Found"
        )

    await message.reply(
        f"Files: {len(batch['files'])}"
    )


@app.on_message(filters.command("admin") & filters.user(ADMINS))
async def admin_help(client, message):

    text = """
Admin Commands

/batch
/done

/broadcast

/stats

/users

/ping

/deletebatch batch_id

/batchinfo batch_id
"""

    await message.reply(text)
