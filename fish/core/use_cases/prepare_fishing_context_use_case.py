from fish.core.interfaces.player_profile_repository_abs import PlayerProfileRepositoryAbstract
from fish.core.interfaces.channel_repository_abs import ChannelRepositoryAbstract
from fish.core.interfaces.points_provider_abs import PointsProviderAbstract
from fish.core.interfaces.twitch_actions_provider_abs import TwitchActionsProviderAbstract

from fish.core.entities import PlayerProfile, UnlockedReward, Channel

class PrepareFishingContextUseCase:
    def __init__(
        self,
        points_provider: PointsProviderAbstract,
        player_profile_repository: PlayerProfileRepositoryAbstract,
        channel_repository: ChannelRepositoryAbstract
    ):
        self.points_provider = points_provider
        self.player_profile_repository = player_profile_repository
        self.channel_repository = channel_repository

    async def execute(self, user_ctx: dict) -> PlayerProfile:
        user_twitch_id = user_ctx.get("user_id")
        user_name = user_ctx.get("username")
        channel_name = user_ctx.get("channel_name")
        channel_id = user_ctx.get("channel_id")
        channel = await self.channel_repository.get_channel(channel_id)
        channel_se_id = channel.se_id if channel else None
        if not channel_se_id:
            channel_se_id = await self.points_provider.get_channel_se_id(channel_name)
            channel = Channel(name=channel_name, twitch_id=channel_id, se_id=channel_se_id)
            await self.channel_repository.create_channel(channel)
        
        user_profile = await self.player_profile_repository.get_or_create_profile(
            user_id=user_twitch_id,
            username=user_name,
            channel_info={"channel_id": channel_id, "se_id": channel_se_id, "name": channel_name}
        )

        return user_profile
