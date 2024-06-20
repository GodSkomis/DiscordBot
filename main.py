import asyncio
import json
import os

import logs
import settings

from utils.s3 import S3Client
from core.bot import SkomisBot
from core.sql import init_models, DatabaseSessionManager


async def get_token():
    client = S3Client()
    return await client.get_bot_token()

async def load_reddit_secrest():
    client = S3Client()
    response = await client.get_file_data(settings.REDDIT_SECRET_FILE)
    data = json.loads(response)
    os.environ['REDDIT_CLIENT_ID'] = data['client_id']
    os.environ['REDDIT_CLIENT_SECRET'] = data['client_secret']

BOT = SkomisBot()

DatabaseSessionManager.setup()


if __name__ == '__main__':
    asyncio.run(init_models())
    asyncio.run(load_reddit_secrest())
    
    BOT.run(asyncio.run(get_token()))
