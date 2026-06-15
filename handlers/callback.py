from pyrogram import filters

from bot import app

from utils.force_sub import is_joined

from config import CHANNEL_LINK

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from handlers.batch import send_batch_files


@app.on_callback_query(
    filters.regex("^check_")
)
async def check_join_callback(
    client,
    query
):

    batch_id = query.data.replace(
        "check_",
        ""
    )

    joined = await is_joined(
        client,
        query.from_user.id
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

        return await query.message.edit_text(
            "You have to join our channel first.",
            reply_markup=buttons
        )

    await query.answer(
        "Verification Successful",
        show_alert=True
    )

    try:
        await query.message.delete()
    except:
        pass

    await send_batch_files(
        client,
        query.message.chat.id,
        batch_id
    )
