import asyncio
import discord

import settings

from discord.ext import commands
from sqlalchemy.orm import Session

from core.sql import DatabaseSessionManager

from .models import Autooroom
from .processing import AbstractProcessing


class AddCommand(AbstractProcessing):
    ctx: commands.Context
    channel_id: int
    category_id: int
    suffix: str | None

    def __init__(
            self,
            ctx: commands.Context,
            channel_id: int,
            category_id: int,
            suffix: str = None
    ):
        self.ctx = ctx
        self.channel_id = channel_id
        self.category_id = category_id
        self.suffix = suffix

    async def _check_channel(self) -> bool:
        return bool(await asyncio.to_thread(discord.utils.get, self.ctx.guild.voice_channels, id=self.channel_id))

    async def _check_category(self) -> bool:
        return bool(await asyncio.to_thread(discord.utils.get, self.ctx.guild.categories, id=self.category_id))

    async def _create_record(self, session: Session):
        autoroom = Autooroom()
        autoroom.guild_id = self.ctx.guild.id
        autoroom.channel_id = self.channel_id
        autoroom.category_id = self.category_id
        if self.suffix:
            autoroom.suffix = self.suffix
        await autoroom.save(session)

    async def process(self) -> bool:
        if not await self._check_channel():
            # await self.ctx.channel.send(f'Channel with given id "{self.channel_id}" not found')
            await self.ctx.interaction.followup.send(content=f'Channel with given id "{self.channel_id}" not found')
            return False

        if not await self._check_category():
            # await self.ctx.channel.send(f'Category with given id "{self.category_id}" not found')
            await self.ctx.interaction.followup.send(content=f'Category with given id "{self.category_id}" not found')
            return False

        try:
            async with DatabaseSessionManager.session() as session:
                await self._create_record(session)
                await session.commit()
        except Exception as ex:
            # await self.ctx.channel.send('Something go wrong, please try again')
            await self.ctx.interaction.followup.send(content='Something go wrong, please try again')
            raise(ex)

        await self.ctx.interaction.followup.send(content="New entry created")
        return True


class ListCommand(AbstractProcessing):
    _ctx: commands.Context

    def __init__(self, ctx: commands.Context):
        self._ctx = ctx

    async def process(self):
        records = await Autooroom.get_guild_records(self._ctx.guild.id)
        response_data = []
        for record in records:
            channel = await asyncio.to_thread(discord.utils.get, self._ctx.guild.voice_channels, id=record.channel_id)
            if channel is None:
                response_data.append(f'ERROR!: "Channel with id: {record.channel_id} not found, please update record"')
                continue
            category = await asyncio.to_thread(discord.utils.get, self._ctx.guild.categories, id=record.category_id)

            if category is None:
                response_data.append(f'ERROR!: "Category with id: {record.category_id} not found, please update record"')
                continue

            response_data.append(f"'{channel.name}' => '{category.name}' with suffix: '{record.suffix}'")

        response = '\n'.join(response_data)
        # await self._ctx.channel.send(response if response else settings.AUTOROOM_EMPTY_LIST_RESPONSE)
        await self._ctx.interaction.response.send_message(response if response else settings.AUTOROOM_EMPTY_LIST_RESPONSE)
