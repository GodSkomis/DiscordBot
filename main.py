import asyncio

import logs

from utils.s3 import S3Client
from core.bot import SkomisBot
from core.sql import init_models, DatabaseSessionManager


async def get_token():
    client = S3Client()
    return await client.get_bot_token()


BOT = SkomisBot()

DatabaseSessionManager.setup()


if __name__ == '__main__':
    asyncio.run(init_models())
    BOT.run(asyncio.run(get_token()))
