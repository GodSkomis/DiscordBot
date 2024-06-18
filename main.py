import os
import asyncio
import discord
import settings

from discord.ext import commands

# import logs

from utils.s3 import S3Client


async def get_token():
    client = S3Client()
    return await client.get_bot_token()


INTENTS = discord.Intents.all()
BOT = commands.Bot(command_prefix='/', intents=INTENTS, description=settings.BOT_DESCRIPTION)



if __name__ == '__main__':
    BOT.run(asyncio.run(get_token()))
