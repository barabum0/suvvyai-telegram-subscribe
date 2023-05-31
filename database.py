import motor.motor_asyncio
from os import getenv


def create_db_connection():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        getenv("MONGO_URL")
    )
    client = client["CorpSoft"]
    return client


class Database:
    def __init__(self, db_connection: motor.motor_asyncio.AsyncIOMotorClient):
        self.db = db_connection

    async def add_questions_to_db(self, insert: dict):
        await self.db.questionary.insert_one(insert)

    async def check_questions(self, uid: int):
        return bool(await self.db.questionary.find_one({"uid": uid}))

    async def get_questions(self, uid: int):
        return await self.db.questionary.find_one({"uid": uid}) or {}