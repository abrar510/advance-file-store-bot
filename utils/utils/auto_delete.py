import asyncio

from config import AUTO_DELETE_TIME

async def auto_delete(
    client,
    chat_id,
    message_ids
):

    await asyncio.sleep(
        AUTO_DELETE_TIME
    )

    try:

        await client.delete_messages(
            chat_id,
            message_ids
        )

    except:
        pass
