from fish.core.interfaces.reward_loader_abs import RewardLoaderAbstract
from fish.core.interfaces.reward_pooler_abs import RewardPoolerAbstract 
from fish.core.interfaces.player_profile_repository_abs import PlayerProfileRepositoryAbstract

from fish.core.entities import PlayerProfile

class SelectRewardUseCase:
    def __init__(
        self,
        player_profile_repository: PlayerProfileRepositoryAbstract,
        reward_loader: RewardLoaderAbstract,
        reward_pooler: RewardPoolerAbstract
    ):
        self.player_profile_repository = player_profile_repository
        self.reward_loader = reward_loader
        self.reward_pooler = reward_pooler

    async def execute(self, user_ctx: dict, user_profile: PlayerProfile) -> dict:
        channel_name = user_ctx.get("channel_name")
        user_role = user_ctx.get("user_role", "base")
        channel_se_id = user_profile.channel.se_id if user_profile.channel else None
        if not channel_se_id:
            raise ValueError("Channel SE ID is not available.")

        global_profile = await self.player_profile_repository.get_or_create_profile(
            user_id="global",
            username="global",
            channel_info={ "channel_id": user_ctx.get("channel_id"), "se_id": user_ctx.get("se_id"), "name": channel_name }
        )

        rewards_pool = self.reward_loader.load_rewards(
            channel_name=channel_name, 
            user_role=user_role
        )
        if not rewards_pool:
            raise ValueError("No rewards available for this channel or user role.")
        
        available_rewards = self._filter_locked_rewards(rewards_pool, user_profile, global_profile)

        if not available_rewards:
            raise ValueError("No available rewards to select from.")

        reward = self.reward_pooler.get_random_reward(available_rewards)

        if not reward:
            raise ValueError("No reward could be selected from the available rewards.")
        
        rewards_with_selected = {
            "reward": reward,
            "rewards_pool": rewards_pool
        }

        return rewards_with_selected

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