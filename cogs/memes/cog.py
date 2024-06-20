import discord

from discord.ext import commands

from .services import MemeService
from .exceptions import MemeServiceException


class MemeCog(commands.Cog):
    _bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.hybrid_command(name='meme')
    async def autoroom_create(self, ctx: commands.Context):
        """Get a meme"""

        await ctx.interaction.response.defer()
        try:
            meme = await MemeService.get_meme(ctx)
            await ctx.interaction.followup.send(meme.title, file=discord.File(meme.bytes, meme.file_name))
        except MemeServiceException as ex:
            await ctx.interaction.followup.send(ex)
        except Exception as ex:
            await ctx.interaction.followup.send('Sorry, failed to load memes')
            raise ex