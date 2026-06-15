from pyrogram.errors import UserNotParticipant
from config import FORCE_CHANNEL

async def is_joined(client, user_id):

    try:
        await client.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )

        return True

    except UserNotParticipant:

        return False

    except:

        return False
