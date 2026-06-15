import asyncio

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from bot import app

from database import (
    users,
    batches
)

from config import (
    CHANNEL_LINK
)

from utils.force_sub import (
    is_joined
)

from utils.auto_delete import (
    auto_delete
)


# --------------------
# START
# --------------------

@app.on_message(filters.command("start"))
async def start_handler(
    client,
    message
):

    user_id = message.from_user.id

    # Save User
    await users.update_one(
        {
            "_id": user_id
        },
        {
            "$set": {
                "_id": user_id
            }
        },
        upsert=True
    )

    # Normal Start
    if len(message.command) == 1:

        return await message.reply(
            "Welcome To File Store Bot"
        )

    data = message.command[1]

    # Not Batch Link
    if not data.startswith(
        "batch_"
    ):
        return

    batch_id = data.replace(
        "batch_",
        ""
    )

    # Check Join
    joined = await is_joined(
        client,
        user_id
    )

    if not joined:

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Join Channel",
                        url=CHANNEL_LINK
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Try Again",
                        callback_data=f"check_{batch_id}"
                    )
                ]
            ]
        )

        return await message.reply(
            "You have to join our channel first.",
            reply_markup=buttons
        )

    await send_batch_files(
        client,
        message.chat.id,
        batch_id
    )
