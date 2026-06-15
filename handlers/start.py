from pyrogram import filters
from pyrogram.types import (
InlineKeyboardMarkup,
InlineKeyboardButton
)

from bot import app
from config import (
FORCE_CHANNEL,
CHANNEL_LINK
)

from database import add_user

async def is_joined(user_id):

```
try:
    member = await app.get_chat_member(
        FORCE_CHANNEL,
        user_id
    )

    return member.status not in [
        "left",
        "kicked"
    ]

except:
    return False
```

@app.on_message(filters.command("start"))
async def start_handler(client, message):

```
await add_user(
    message.from_user.id
)

buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "📢 Join Channel",
                url=CHANNEL_LINK
            )
        ]
    ]
)

if not await is_joined(
    message.from_user.id
):

    await message.reply_text(
        "⚠️ Join our channel first.",
        reply_markup=buttons
    )

    return

await message.reply_text(
    "✅ Welcome!\n\nSend me a file."
)
```
