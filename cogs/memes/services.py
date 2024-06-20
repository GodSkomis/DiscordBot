import io
import os
import logging
import aiohttp

import settings

from typing import Dict
from collections import namedtuple

from discord.ext import commands

from .exceptions import MemeServiceException


Meme = namedtuple('Meme', ['bytes', 'file_name', 'title'])


class MemeService:
    
    @classmethod
    async def get_meme(cls, ctx: commands.Context) -> Meme:
        data = await cls._load_memes()
        url = data['url']
        title = data['title']
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=settings.REDDIT_MEME_USER_AGENT, auth=aiohttp.BasicAuth(
                    settings.GET_REDDIT_CLIENT_ID(), settings.GET_REDDIT_CLIENT_SECRET()
                )) as resp:
                img = await resp.read()
                bytes = io.BytesIO(img)
                file_name = os.path.basename(url)
                return Meme(bytes=bytes, file_name=file_name, title=title)
    
    @classmethod
    async def _load_memes(cls) -> Dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.BASE_MEME_ENDPOINT) as response:
                data = await response.json()
                if response.status >= 400:
                    logging.error(f'MemeService Error: {data}')
                    raise MemeServiceException('The meme service is currently unavailable, please try again later')
                return data