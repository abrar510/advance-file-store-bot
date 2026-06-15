# utils/auto_delete.py

import asyncio

async def auto_delete(
    client,
    chat_id,
    message_ids,
    delay=600
):
    await asyncio.sleep(delay)

    try:
        await client.delete_messages(
            chat_id,
            message_ids
        )
    except:
        pass
