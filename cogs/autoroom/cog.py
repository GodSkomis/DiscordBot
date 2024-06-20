import discord

from discord.ext import commands

from core.checks import is_guild_owner

from .commands import AddCommand, ListCommand, StatsCommand
from .processing import OnVoiceStateUpdateProcessing


class AutoroomCog(commands.Cog):
    _bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
            self,
            member: discord.Member,
            before: discord.VoiceState,
            after: discord.VoiceState
    ):
        processor = OnVoiceStateUpdateProcessing(member, before, after)
        await processor.process()

    @commands.hybrid_group(name='autoroom')
    async def autoroom(self, ctx: commands.Context):
        # await ctx.send_message('Choose a subcommand')
        # await ctx.send()
        pass
    
    @autoroom.command(name='add')
    @commands.check(is_guild_owner)
    async def autoroom_create(
        self,
        ctx: commands.Context,
        channel_id: str,
        category_id: str,
        suffix: str = None
    ):
        command = AddCommand(ctx, int(channel_id), int(category_id), suffix)
        await ctx.interaction.response.defer()
        await command.process()
        
    @autoroom.command(name='list')
    @commands.check(is_guild_owner)
    async def autoroom_list(self, ctx: commands.Context):
        command = ListCommand(ctx)
        await command.process()
    
    @autoroom.command(name='stats')
    async def autoroom_list(self, ctx: commands.Context):
        await ctx.interaction.response.defer()
        command = StatsCommand(ctx)
        await command.process()

    @autoroom.command(name='remove')
    @commands.check(is_guild_owner)
    async def autoroom_remove(self, ctx: commands.Context):
        await ctx.interaction.response.defer()

    @autoroom.command(name='update')
    @commands.check(is_guild_owner)
    async def autoroom_update(self, ctx: commands.Context):
        await ctx.interaction.response.defer()
    