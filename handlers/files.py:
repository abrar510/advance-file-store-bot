from pyrogram import filters

from bot import app
from config import STORE_CHANNEL

@app.on_message(
filters.private &
(
filters.document |
filters.video |
filters.audio |
filters.photo
)
)
async def store_file(client, message):

```
stored = await message.copy(
    STORE_CHANNEL
)

me = await client.get_me()

link = (
    f"https://t.me/"
    f"{me.username}"
    f"?start={stored.id}"
)

await message.reply_text(
    f"✅ File Stored\n\n{link}"
)
```
