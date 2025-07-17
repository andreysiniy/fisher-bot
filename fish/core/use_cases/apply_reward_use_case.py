from fish.core.use_cases.reward_handlers.reward_handler_factory import RewardHandlerFactory
from fish.core.use_cases.fish_use_case import FishingUseCase
from fish.core.interfaces.twitch_actions_provider_abs import TwitchActionsProviderAbstract
from fish.core.interfaces.points_provider_abs import PointsProviderAbstract
import asyncio

class ApplyRewardUseCase:
    def __init__(
            self,
            points_provider: PointsProviderAbstract,
            twitch_actions_provider: TwitchActionsProviderAbstract,
            reward_handler_factory: RewardHandlerFactory
            ):
        self.points_provider = points_provider,
        self.twitch_actions_provider = twitch_actions_provider,
        self.reward_handler_factory = reward_handler_factory
        
    async def execute(self, user_ctx: dict, reward: dict, rewards_pool: dict):
        handler = self.reward_handler_factory.get_handler(
            user_ctx=user_ctx,
            reward=reward,
            rewards_pool=rewards_pool
        )
        actions = handler.handle().get("actions", [])



        for action in actions:
            pass

    async def _prepare_robbery(self, user_ctx: dict, reward: dict) -> dict:
        updated_ctx = user_ctx
        _range = reward.get("range", 1)
        channel_se_id = user_ctx.get("channel_se_id")
        username = user_ctx.get("username")

        if not channel_se_id:
            raise ValueError("Couldn't get channel StreamElements ID for robbery reward preparation")
        
        rank = await self.points_provider.get_user_rank(user=username, channel_id=channel_se_id)
        offset = max(rank - _range - 1, 0)
        limit = min(_range, rank - 1) 
        if rank == 1:
            offset = 1
            limit = 1
        
        robbery_users_pool = await self.points_provider.list_top_userpoints(
            limit=limit,
            offset=offset,
            channel_id=channel_se_id
        )
        updated_ctx.update(robbery_users_pool)

        return updated_ctx
    
    async def _prepare_userpoints(self, user_ctx: dict) -> dict:
        updated_ctx = user_ctx
        channel_se_id = user_ctx.get("channel_se_id")
        username = user_ctx.get("username")

        if not channel_se_id:
            raise ValueError("Couldn't get channel StreamElements ID for userpoints preparation")
        
        current_points = await self.points_provider.get_user_points(user=username, channel_id=channel_se_id)
        
        if not current_points:
            raise ValueError(f"Couldn't get {username} points on channel id : {channel_se_id}")

        updated_ctx.update({"points": current_points})

        return updated_ctx

    async def _add_points(self, action_ctx: dict, user_ctx: dict) -> dict:
        updated_ctx = user_ctx
        channel_se_id = user_ctx.get("channel_se_id")
        username = action_ctx.get("username")
        delay = action_ctx.get("delay", 0)
        points_to_add = action_ctx.get("points")

        if not channel_se_id:
            raise ValueError("Couldn't get channel StreamElements ID for adding points operation")
    
        await asyncio.sleep(delay)
        response = await self.points_provider.add_user_points(
            user=username,
            channel_id=channel_se_id,
            points=points_to_add
        )

        if not response:
            raise ValueError(f"Couldn't add points to {username} on channel {channel_se_id}")
        
        updated_ctx.update({"points": response.get("newAmount")})

        return updated_ctx
    
    async def _remove_points(self, action_ctx: dict, user_ctx: dict) -> dict:
        updated_ctx = user_ctx
        channel_se_id = user_ctx.get("channel_se_id")
        username = action_ctx.get("username")
        delay = action_ctx.get("delay", 0)
        points_to_remove = action_ctx.get("points")

        if not channel_se_id:
            raise ValueError("Couldn't get channel StreamElements ID for adding points operation")
    
        await asyncio.sleep(delay)
        response = await self.points_provider.remove_user_points(
            user=username,
            channel_id=channel_se_id,
            points=points_to_remove
        )

        if not response:
            raise ValueError(f"Couldn't add points to {username} on channel {channel_se_id}")
        
        updated_ctx.update({"points": response.get("newAmount")})

        return updated_ctx   
