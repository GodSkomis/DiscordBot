from discord.ext import commands


def is_guild_owner(ctx: commands.Context):
    if ctx.author.id == ctx.guild.owner_id:
        return True
    return False
    