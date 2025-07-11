from fish.core.interfaces.player_profile_repository_abs import PlayerProfileRepositoryAbstract
from fish.core.interfaces.channel_repository_abs import ChannelRepositoryAbstract
from fish.core.interfaces.points_provider_abs import PointsProviderAbstract
from fish.core.interfaces.twitch_actions_provider_abs import TwitchActionsProviderAbstract
from fish.core.interfaces.reward_loader_abs import RewardLoaderAbstract
from fish.core.interfaces.reward_pooler_abs import RewardPoolerAbstract 

from fish.core.entities import PlayerProfile, UnlockedReward, Channel

class FishingUseCase:
    def __init__(
        self,
        points_provider: PointsProviderAbstract,
        twitch_actions_provider: TwitchActionsProviderAbstract,
        player_profile_repository: PlayerProfileRepositoryAbstract,
        channel_repository: ChannelRepositoryAbstract,
        reward_loader: RewardLoaderAbstract,
        reward_pooler: RewardPoolerAbstract
    ):
        self.points_provider = points_provider
        self.twitch_actions_provider = twitch_actions_provider
        self.player_profile_repository = player_profile_repository
        self.channel_repository = channel_repository
        self.reward_loader = reward_loader
        self.reward_pooler = reward_pooler

    async def execute(self, user_ctx: dict) -> PlayerProfile:
        user_twitch_id = user_ctx.get("user_id")
        user_name = user_ctx.get("username")
        channel_name = user_ctx.get("channel_name")
        channel_id = user_ctx.get("channel_id")
        user_role = user_ctx.get("user_role", "base")
        channel = await self.channel_repository.get_channel(channel_id)
        channel_se_id = channel.se_id if channel else None
        if not channel_se_id:
            channel_se_id = await self.points_provider.get_channel_se_id(channel_name)
            channel = Channel(name=channel_name, twitch_id=channel_id, se_id=channel_se_id)
            await self.channel_repository.create_channel(channel)
        is_subscriber = user_ctx.get("is_subscriber", False)
        user_profile = await self.player_profile_repository.get_or_create_profile(
            user_id=user_twitch_id,
            username=user_name,
            channel_info={ "channel_id": channel_id, "se_id": channel_se_id, "name": channel_name }
        )

        global_profile = await self.player_profile_repository.get_or_create_profile(
            user_id="global",
            username="global",
            channel_info={ "channel_id": channel_id, "se_id": channel_se_id, "name": channel_name }
        )

        rewards_pool = self.reward_loader.load_rewards(
            channel_name=channel_name, 
            user_role=user_role
            )
        if not rewards_pool:
            raise ValueError("No rewards available for this channel or user role.")
        
        available_rewards = self._filter_locked_rewards(rewards_pool, user_profile, global_profile)

        if not available_rewards:
            raise ValueError("No available rewards for this user profile.")
        
        reward = self.reward_pooler.get_random_reward(available_rewards)

        if not reward:
            raise ValueError("No reward could be selected from the available pool.")
        
        mult_dict = {
            "base_multiplier": rewards_pool.get("base_multiplier", 1.0),
            "sub_multiplier": rewards_pool.get("sub_multiplier", 1.0)
        }

        multiplier = self._get_multiplier(is_subscriber, mult_dict)
        reward = self._handle_multiplier(reward, multiplier)


        pass


    def _filter_locked_rewards(self, rewards_pool: dict, user_profile: PlayerProfile, global_profile: PlayerProfile) -> dict:
        filtered_rewards = {}
        unlocked_ids = {reward.id for reward in user_profile.unlocked_rewards}
        unlocked_ids.update({reward.id for reward in global_profile.unlocked_rewards})
        for category, reward_list in rewards_pool["rewards"].items():
            available_rewards = []
            for reward in reward_list:
                is_locked = reward.get("locked", False)
                reward_id = reward.get("id")
                if not is_locked or (reward_id and reward_id in unlocked_ids):
                    available_rewards.append(reward)
                
            if available_rewards:
                filtered_rewards[category] = available_rewards
        return filtered_rewards

    def _get_multiplier(self, is_subscriber: bool, mult_dict: dict) -> float:
        if is_subscriber:
            return mult_dict.get("sub_multiplier", 1.0)
        return mult_dict.get("base_multiplier", 1.0)
    
    def _handle_multiplier(self, reward: dict, multiplier: float) -> dict:
        mult_mapper = {
            "value": lambda: reward.update({
                "value": (
                    int(reward["value"] * multiplier)
                    if reward["value"] > 0
                    else int(reward["value"] - reward["value"] * (multiplier - 1))
                )
            }),
            "percentage": lambda: reward.update({
                "percentage": (
                    reward["percentage"] * multiplier
                    if reward["percentage"] > 0
                    else reward["percentage"] - reward["percentage"] * (multiplier - 1)
                )
            }),
            "seconds": lambda: reward.update({
                "seconds": (
                    int(reward["seconds"] - reward["seconds"] * (multiplier - 1))
                )
            })
        }
        for key, update_func in mult_mapper.items():
            if key in reward:
                update_func()
        return reward