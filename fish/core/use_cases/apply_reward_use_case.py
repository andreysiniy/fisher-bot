from fish.core.use_cases.reward_handlers.reward_handler_factory import RewardHandlerFactory
from fish.core.use_cases.fish_use_case import FishingUseCase
from fish.core.interfaces.twitch_actions_provider_abs import TwitchActionsProviderAbstract
from fish.core.interfaces.points_provider_abs import PointsProviderAbstract
import fish.core.helpers.message_utils as MessageUtils
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
        prepared_ctx = self._handle_preparations(user_ctx, reward)
        handler = self.reward_handler_factory.get_handler(
            user_ctx=prepared_ctx,
            reward=reward,
            rewards_pool=rewards_pool
        )
        actions = handler.handle().get("actions", [])


        for action in actions:
            actions_map = {
                'message': lambda: self._send_message(action_ctx=action.get("message"), user_ctx=prepared_ctx),
                'timeout': lambda: self._timeout_user(action_ctx=action.get("timeout"), user_ctx=prepared_ctx),
                'add_points': lambda: prepared_ctx.update(self._add_points(action_ctx=action.get("add_points"), user_ctx=prepared_ctx)),
                'remove_points': lambda: prepared_ctx.update(self._remove_points(action_ctx=action.get("remove_points"), user_ctx=prepared_ctx))
            }
            for key in actions_map:
                if key in action:
                    await actions_map[key]()
            

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
            raise ValueError(f"Couldn't remove points from {username} on channel {channel_se_id}")
        
        updated_ctx.update({"points": response.get("newAmount")})

        return updated_ctx

    async def _timeout_user(self, action_ctx: dict, user_ctx: dict):
        channel_name = user_ctx.get("channel_name")
        username = action_ctx.get("username")
        seconds = action_ctx.get("timeout")
        delay = action_ctx.get("delay", 0)
        reason = action_ctx.get("reason")
        await asyncio.sleep(delay)
        await self.twitch_actions_provider.timeout_user(channel_name, username, seconds, reason)
    
    async def _send_message(self, action_ctx: dict, user_ctx: dict):
        channel_name = user_ctx.get("channel_name")

        if not channel_name:
            raise ValueError("Couldn't get the channel name for messsage sending")

        format_map = {
            'username': action_ctx.get("username", "unknown"),
            'value': MessageUtils.format_large_number(action_ctx.get("points", 0)),
            'time': MessageUtils.format_time(action_ctx.get("seconds", 0)),
            'victim': action_ctx.get("victim", "unknown"),
            'victim_points': MessageUtils.format_large_number(action_ctx.get("victim_points", 0)),
            'bullets': action_ctx.get("bullets", 0),
            'chambers': action_ctx.get("chambers", 0),
            'percentage': action_ctx.get("percentage", 0),
            'delay': MessageUtils.format_time(action_ctx.get("seconds", 0)),
            'total_points': MessageUtils.format_large_number(user_ctx.get("points", 0))
        }
        message = action_ctx.get("message", "").format_map(format_map)
        await asyncio.sleep(action_ctx.get("delay", 0))
        await self.twitch_actions_provider.send_message(channel_name, message) 

    async def _handle_preparations(self, user_ctx: dict, reward: dict):
        updated_ctx = user_ctx
        if "percentage" in reward:
            updated_ctx = await self._prepare_userpoints(updated_ctx)
        if reward.get("type") == "robbery":
            updated_ctx = await self._prepare_robbery(updated_ctx, reward)
        return updated_ctx