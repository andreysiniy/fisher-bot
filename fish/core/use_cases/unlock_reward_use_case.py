from fish.core.interfaces.player_profile_repository_abs import PlayerProfileRepositoryAbstract

from fish.core.entities import PlayerProfile, UnlockedReward

class UnlockRewardUseCase:
    def __init__(
        self,
        player_profile_repository: PlayerProfileRepositoryAbstract
    ):
        self.player_profile_repository = player_profile_repository

    async def execute(self, user_profile: PlayerProfile, reward_id: str) -> PlayerProfile:
        if not user_profile:
            raise ValueError("User profile is required.")
        
        user_profile = self.unlock_reward(user_profile, reward_id)

        await self.player_profile_repository.update_profile(user_profile.user.twitch_id, user_profile)

        return user_profile
    
    def unlock_reward(self, user_profile: PlayerProfile, reward_id: str) -> PlayerProfile:
        if not reward_id:
            raise ValueError("Reward ID must be provided.")

        if any(reward.id == reward_id for reward in user_profile.unlocked_rewards):
            raise ValueError("Reward is already unlocked.")

        unlocked_reward = UnlockedReward(id=reward_id)

        user_profile.unlocked_rewards.append(unlocked_reward)

        return user_profile