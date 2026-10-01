import time
from motor.motor_asyncio import AsyncIOMotorClient
import config


class Database:
    def __init__(self, uri, name):
        self.client = AsyncIOMotorClient(uri)
        d = self.client[name]
        self.users = d.users
        self.admins = d.admins
        self.banned = d.banned
        self.fsub = d.fsub
        self.requests = d.join_requests
        self.deletes = d.pending_deletes
        self.settings = d.settings

    async def setup(self):
        await self.requests.create_index([("chat_id", 1), ("user_id", 1)], unique=True)
        await self.deletes.create_index("delete_at")

    # ---------- users ----------
    async def add_user(self, uid):
        await self.users.update_one({"_id": uid}, {"$setOnInsert": {"_id": uid}}, upsert=True)

    async def all_users(self):
        return [u["_id"] async for u in self.users.find({})]

    async def count_users(self):
        return await self.users.count_documents({})

    async def del_user(self, uid):
        await self.users.delete_one({"_id": uid})

    # ---------- ban ----------
    async def ban(self, uid):
        await self.banned.update_one({"_id": uid}, {"$set": {"_id": uid}}, upsert=True)

    async def unban(self, uid):
        await self.banned.delete_one({"_id": uid})

    async def is_banned(self, uid):
        return await self.banned.find_one({"_id": uid}) is not None

    async def banned_list(self):
        return [u["_id"] async for u in self.banned.find({})]

    # ---------- admins ----------
    async def add_admin(self, uid):
        await self.admins.update_one({"_id": uid}, {"$set": {"_id": uid}}, upsert=True)

    async def del_admin(self, uid):
        await self.admins.delete_one({"_id": uid})

    async def admin_list(self):
        ids = {config.OWNER_ID, *config.ADMINS}
        ids.update([a["_id"] async for a in self.admins.find({})])
        return sorted(i for i in ids if i)

    async def is_admin(self, uid):
        return uid in await self.admin_list()

    # ---------- force sub ----------
    async def add_fsub(self, cid, title, mode="normal"):
        await self.fsub.update_one(
            {"_id": cid}, {"$set": {"_id": cid, "title": title, "mode": mode, "link": None}}, upsert=True
        )

    async def del_fsub(self, cid):
        await self.fsub.delete_one({"_id": cid})
        await self.requests.delete_many({"chat_id": cid})

    async def get_fsub(self, cid):
        return await self.fsub.find_one({"_id": cid})

    async def get_fsubs(self):
        return [c async for c in self.fsub.find({})]

    async def set_fsub_mode(self, cid, mode):
        await self.fsub.update_one({"_id": cid}, {"$set": {"mode": mode, "link": None}})

    async def set_fsub_link(self, cid, link):
        await self.fsub.update_one({"_id": cid}, {"$set": {"link": link}})

    # ---------- join requests ----------
    async def add_request(self, cid, uid):
        await self.requests.update_one(
            {"chat_id": cid, "user_id": uid}, {"$set": {"chat_id": cid, "user_id": uid}}, upsert=True
        )

    async def has_request(self, cid, uid):
        return await self.requests.find_one({"chat_id": cid, "user_id": uid}) is not None

    # ---------- auto delete queue ----------
    async def add_delete(self, chat_id, ids, delete_at, payload=None):
        await self.deletes.insert_one(
            {"chat_id": chat_id, "ids": ids, "delete_at": delete_at, "payload": payload}
        )

    async def due_deletes(self):
        return [d async for d in self.deletes.find({"delete_at": {"$lte": time.time()}}).limit(50)]

    async def remove_delete(self, _id):
        await self.deletes.delete_one({"_id": _id})

 # ---------- shortener tokens / verification ----------
    async def create_token(self, user_id, payload):
        token = secrets.token_hex(8)
        now = time.time()
        await self.tokens.delete_many({"created": {"$lt": now - 3600}})  # cleanup
        await self.tokens.insert_one(
            {"_id": token, "user_id": user_id, "payload": payload, "created": now}
        )
        return token

    async def get_token(self, token):
        return await self.tokens.find_one({"_id": token})

    async def del_token(self, token):
        await self.tokens.delete_one({"_id": token})

    async def set_verified(self, uid, until):
        await self.verified.update_one({"_id": uid}, {"$set": {"until": until}}, upsert=True)

    async def is_verified(self, uid):
        doc = await self.verified.find_one({"_id": uid})
        return bool(doc) and doc["until"] > time.time()   
    
    # ---------- settings ----------
    async def get_setting(self, key, default=None):
        doc = await self.settings.find_one({"_id": "main"}) or {}
        return doc.get(key, default)

    async def set_setting(self, key, value):
        await self.settings.update_one({"_id": "main"}, {"$set": {key: value}}, upsert=True)


db = Database(config.DB_URI, config.DB_NAME)
