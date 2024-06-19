import discord

import settings

from discord.ext import commands
from discord.app_commands import CommandTree

from cogs.autoroom.cog import AutoroomCog


class SkomisBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="/", intents=intents, description=settings.BOT_DESCRIPTION)

    async def setup_hook(self):
        # await self.load_extension("cogs.admin")
        await self.add_cog(AutoroomCog(self))
        await self.tree.sync()
        for guild in self.guilds:
            await self.tree.sync(guild)
            
