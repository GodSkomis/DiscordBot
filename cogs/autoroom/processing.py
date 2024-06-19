import asyncio
import logging
import discord

from pprint import pprint
from typing import Optional
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from core.sql import DatabaseSessionManager

from .models import Autooroom, AutoroomMetrics


class AbstractProcessing(ABC):

    @abstractmethod
    async def process(self, *args, **kwargs):
        pass


class OnVoiceStateUpdateProcessing(AbstractProcessing):
    member: discord.Member
    before: Optional[discord.VoiceState] = None
    after: Optional[discord.VoiceState] = None

    def __init__(
            self,
            member: discord.Member,
            before: discord.VoiceState,
            after: discord.VoiceState
    ):
        self.member = member
        self.before = before
        self.after = after

    @staticmethod
    def _is_room_empty(channel: discord.VoiceChannel) -> bool:
        return len(channel.members) == 0

    async def _is_channel_in_observable_category(self, session: Session) -> bool:
        return await Autooroom.check_are_exists_category_id(session, self.before.channel.category.id)

    def _create_new_channel_name(self, channel: Autooroom) -> str:
        name = nick if (nick := self.member.nick) else self.member.name
        return f"{name}`s {channel.suffix}"

    async def _create_voice_channel(
            self,
            channel_name: str,
            category: discord.CategoryChannel,
            bitrate: int = None
    ) -> discord.VoiceChannel:
        return await self.member.guild.create_voice_channel(
            channel_name,
            category=category,
            bitrate=bitrate if bitrate else self.member.guild.bitrate_limit
        )

    async def _get_category(self, category_id: int) -> discord.CategoryChannel:
        return await asyncio.to_thread(discord.utils.get, self.member.guild.categories, id=category_id)

    async def _finalize_channel(self, channel: discord.VoiceChannel):
        await channel.edit(reason=None, position=0)
        await self.member.move_to(channel)

    async def _before_processing(self):
        if (not self.before.channel) or (not self._is_room_empty(self.before.channel)):
            return
        
        async with DatabaseSessionManager.session() as session:
            if not await self._is_channel_in_observable_category(session):
                return False
            await self.before.channel.delete()
            await AutoroomMetrics.mark_as_deleted(session, self.before.channel.id)
            await session.commit()
            logging.info(
                f'[Guild: "{self.before.channel.guild.name}"({self.before.channel.guild.id}) | Channel: "{self.before.channel.name}"({self.before.channel.id})] - Have been deleted'
            )

    async def _after_processing(self):
        if (not self.after.channel) or (self.member.bot):
            return
        
        async with DatabaseSessionManager.session() as session:
            autoroom = await Autooroom.get_by_channel_id(session, self.after.channel.id)
            if not autoroom:
                return False
            new_channel_name = self._create_new_channel_name(autoroom)
            category = await self._get_category(autoroom.category_id)
            new_channel = await self._create_voice_channel(new_channel_name, category)
            await self._finalize_channel(new_channel)
            await AutoroomMetrics.mark_as_created(session, autoroom.id, self.member.id, new_channel.id)
            await session.commit()
            logging.info(
                f'[Guild: "{self.after.channel.guild.name}"({self.after.channel.guild.id}) | Channel: "{new_channel.name}"({new_channel.id})] - Have been created'
            )

    async def process(self):
        await self._before_processing()
        await self._after_processing()
