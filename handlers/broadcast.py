import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait

from bot import app

from config import ADMINS

from database import users


broadcast_state = {}


@app.on_message(
    filters.command("broadcast")
    & filters.user(ADMINS)
)
async def start_broadcast(
    client,
    message
):

    broadcast_state[
        message.from_user.id
    ] = True

    await message.reply(
        "Send any message to broadcast."
    )


@app.on_message(
    filters.private
    & filters.user(ADMINS)
)
async def broadcast_handler(
    client,
    message
):

    admin_id = message.from_user.id

    if admin_id not in broadcast_state:
        return

    if (
        message.text
        and
        message.text.startswith("/")
    ):
        return

    del broadcast_state[admin_id]

    progress = await message.reply(
        "Broadcast Started..."
    )

    success = 0
    failed = 0

    async for user in users.find():

        user_id = user["_id"]

        try:

            await message.copy(
                user_id
            )

            success += 1

            await asyncio.sleep(
                0.1
            )

        except FloodWait as e:

            await asyncio.sleep(
                e.value
            )

            try:

                await message.copy(
                    user_id
                )

                success += 1

            except:

                failed += 1

        except:

            failed += 1

    await progress.edit_text(
        f"Broadcast Completed\n\n"
        f"Success : {success}\n"
        f"Failed : {failed}"
    )
