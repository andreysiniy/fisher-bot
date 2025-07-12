from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, sessionmaker

from fish.core.entities import PlayerProfile, User, Channel, SE_Stats
from fish.infrastructure.database.connection import AsyncSessionFactory
from fish.core.interfaces.player_profile_repository_abs import PlayerProfileRepositoryAbstract

class PlayerProfileRepository(PlayerProfileRepositoryAbstract):
    def __init__(self, session_factory: sessionmaker = AsyncSessionFactory):
        self.session_factory = session_factory

    async def get_or_create_profile(self, user_id: str, username: str, channel_info: dict) -> PlayerProfile:
        async with self.session_factory() as session:
            async with session.begin():
                stmt = (
                    select(PlayerProfile)
                    .join(PlayerProfile.user)
                    .join(PlayerProfile.channel)
                    .where(User.twitch_id == user_id, Channel.name == channel_info["name"])
                    .options(
                        selectinload(PlayerProfile.se_stats),
                        selectinload(PlayerProfile.fish_stats),
                        selectinload(PlayerProfile.unlocked_rewards),
                        selectinload(PlayerProfile.user),
                        selectinload(PlayerProfile.channel)
                    )
                )
        
                result = await session.execute(stmt)
                profile = result.scalar_one_or_none()

                if profile:
                    if profile.user.twitch_name != username:
                        profile.user.twitch_name = username
                
                    return profile
                
                user_stmt = select(User).where(User.twitch_id == user_id)
                user = (await session.execute(user_stmt)).scalar_one_or_none()
                if not user:
                    user = User(twitch_id=user_id, twitch_name=username)
                    session.add(user)

                channel_stmt = select(Channel).where(Channel.name == channel_info["name"])
                channel = (await session.execute(channel_stmt)).scalar_one_or_none()

                if not channel:
                    channel = Channel(name=channel_info["name"], twitch_id=channel_info["twitch_id"], se_id=channel_info["se_id"])
                    session.add(channel)

                new_profile = PlayerProfile(user=user, channel=channel)
                new_profile.se_stats = SE_Stats()

                session.add(new_profile)
            
            refreshed_result = await session.execute(stmt)
            return refreshed_result.scalar_one()
        
    async def update_profile(self, user_id: str, profile: PlayerProfile) -> None:
        async with self.session_factory() as session:
            existing_profile = await session.get(PlayerProfile, profile.id)
            if existing_profile:
                existing_profile.cooldown_expiration = profile.cooldown_expiration
                existing_profile.user.twitch_name = profile.user.twitch_name
                existing_profile.channel.name = profile.channel.name
                existing_profile.se_stats = profile.se_stats
                existing_profile.fish_stats = profile.fish_stats
                existing_profile.unlocked_rewards = profile.unlocked_rewards
                await session.commit()

    async def delete_profile(self, user_id: str) -> None:
        async with self.session_factory() as session:
            existing_profile = await session.execute(
                select(PlayerProfile).where(PlayerProfile.user_id == user_id)
            )
            profile = existing_profile.scalar_one_or_none()
            if profile:
                await session.delete(profile)
                await session.commit()

    async def get_top_by_points_income(self, channel_id: str, limit: int = 10) -> list[PlayerProfile]:
        async with self.session_factory() as session:
            stmt = (
                select(PlayerProfile)
                .join(PlayerProfile.se_stats)
                .where(PlayerProfile.channel_id == channel_id)
                .order_by(PlayerProfile.se_stats.fishing_income.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def get_top_by_fishes_caught(self, channel_id: str, limit: int = 10) -> list[PlayerProfile]:
        async with self.session_factory() as session:
            stmt = (
                select(PlayerProfile)
                .join(PlayerProfile.fish_stats)
                .where(PlayerProfile.channel_id == channel_id)
                .order_by(PlayerProfile.fish_stats.fishes_caught.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return result.scalars().all()