from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

mongo = AsyncIOMotorClient(MONGO_URI)

db = mongo["FileStoreBot"]

users = db.users
batches = db.batches

async def add_user(user_id):
user = await users.find_one(
{"_id": user_id}
)

```
if not user:
    await users.insert_one(
        {"_id": user_id}
    )
```

async def total_users():
return await users.count_documents({})

async def create_batch(batch_id, file_ids):
await batches.insert_one(
{
"_id": batch_id,
"files": file_ids
}
)

async def get_batch(batch_id):
return await batches.find_one(
{"_id": batch_id}
)
