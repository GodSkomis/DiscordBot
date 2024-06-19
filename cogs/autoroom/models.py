import datetime
import logging

import settings

from typing import Dict, List, TYPE_CHECKING, Optional, Self, Tuple
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from sqlalchemy import ForeignKey, Column, Table, Index, desc, exists, func, null, select, update

from core.sql import Base


class Autooroom(Base):
    __tablename__ = "bot_autoroom"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(nullable=False)
    channel_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    category_id: Mapped[int] = mapped_column(nullable=False)
    suffix: Mapped[str] = mapped_column(default=settings.AUTOROOM_DEFAULT_SUFFIX, nullable=False)

    metrics: Mapped[List['AutoroomMetrics']] = relationship(back_populates='autoroom')

    # __table_args__ = (
    #     Index('idx_channel_id_guild_id', 'first_name', 'last_name'),
    # )
    
    async def save(self, session: Session) -> None:
        session.add(self)

    @classmethod
    async def check_are_exists_category_id(self, session: Session, category_id: int) -> bool:
        query = select(exists().where(Autooroom.category_id == category_id))
        return await session.scalar(query)
        
    @classmethod
    async def get_by_channel_id(self, session: Session, channel_id: int) -> Optional[Self]:
        query = select(Autooroom).where(Autooroom.channel_id == channel_id)
        return await session.scalar(query)

    @classmethod
    async def get_guild_records(self, session: Session, guild_id: int) -> List[Self]:
        query = select(Autooroom).where(Autooroom.guild_id == guild_id)
        return await session.scalars(query)
        
        
class AutoroomMetrics(Base):
    __tablename__ = "bot_autoroom_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    autoroom_id: Mapped[int] = mapped_column(ForeignKey(Autooroom.id), nullable=False)
    autoroom: Mapped[Autooroom] = relationship(back_populates='metrics')
    created_at: Mapped[datetime.datetime] = mapped_column(default=settings.GET_TIME_LAMBDA)
    destroyed_at: Mapped[datetime.datetime] = mapped_column(nullable=True)
    channel_owner_id: Mapped[int] = mapped_column(nullable=False)
    channel_id: Mapped[int] = mapped_column(nullable=False)

    @classmethod
    async def mark_as_created(cls, session: Session, autoroom_id: int, member_id: int, channel_id: int) -> Self:
        metric = cls()
        metric.autoroom_id = autoroom_id
        metric.channel_owner_id = member_id
        metric.channel_id = channel_id
        session.add(metric)
            
    @classmethod
    async def mark_as_deleted(cls, session: Session, channel_id: int) -> Self:
        get_datetime = settings.GET_TIME_LAMBDA
        query = update(AutoroomMetrics) \
                    .where(
                        AutoroomMetrics.channel_id == channel_id,
                        AutoroomMetrics.destroyed_at == null()
                    ) \
                        .values(destroyed_at=get_datetime())
        await session.execute(query)

    @classmethod
    async def get_user_metrics(cls, session: Session, member_id: int) -> Tuple[int, Self]:
        count_query = select(func.count()).where(AutoroomMetrics.channel_owner_id == member_id)
        last_metric_query = select(AutoroomMetrics).where(AutoroomMetrics.destroyed_at.isnot(None)).order_by(desc(AutoroomMetrics.destroyed_at)).limit(1)
        return (await session.scalar(count_query), await session.scalar(last_metric_query))
