from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, sessionmaker

from fish.core.entities import Channel
from fish.infrastructure.database.connection import AsyncSessionFactory
from fish.core.interfaces.channel_repository_abs import ChannelRepositoryAbstract

class ChannelRepository(ChannelRepositoryAbstract):
    def __init__(self, session_factory: sessionmaker = AsyncSessionFactory):
        self.session_factory = session_factory

    async def get_channel(self, channel_id: str) -> Channel:
        async with self.session_factory() as session:
            stmt = select(Channel).where(Channel.twitch_id == channel_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def create_channel(self, channel: Channel) -> Channel:
        async with self.session_factory() as session:
            async with session.begin():
                session.add(channel)
            await session.refresh(channel) 
            return channel

    async def update_channel(self, channel: Channel) -> Channel:
        async with self.session_factory() as session:
            async with session.begin():
                stmt = select(Channel).where(Channel.twitch_id == channel.twitch_id)
                result = await session.execute(stmt)
                existing_channel = result.scalar_one_or_none()
                if existing_channel:
                    existing_channel.name = channel.name
                    existing_channel.se_id = channel.se_id
                
            return existing_channel

    async def delete_channel(self, channel_id: str) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                stmt = select(Channel).where(Channel.twitch_id == channel_id)
                result = await session.execute(stmt)
                channel_to_delete = result.scalar_one_or_none()
                if channel_to_delete:
                    await session.delete(channel_to_delete)

