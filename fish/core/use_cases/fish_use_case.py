from fish.core.use_cases.prepare_fishing_context_use_case import PrepareFishingContextUseCase
from fish.core.use_cases.unlock_reward_use_case import UnlockRewardUseCase
from fish.core.use_cases.select_reward_use_case import SelectRewardUseCase
from fish.core.use_cases.apply_multiplier_use_case import ApplyMultiplierUseCase
from fish.core.interfaces.player_profile_repository_abs import PlayerProfileRepositoryAbstract

from fish.core.entities import PlayerProfile

class FishingUseCase:
    def __init__(
        self,
        prepare_fishing_context_use_case: PrepareFishingContextUseCase,
        select_reward_use_case: SelectRewardUseCase,
        unlock_reward_use_case: UnlockRewardUseCase,
        apply_multiplier_use_case: ApplyMultiplierUseCase,
        player_profile_repository: PlayerProfileRepositoryAbstract = PlayerProfileRepositoryAbstract
    ):
        self.prepare_fishing_context_use_case = prepare_fishing_context_use_case
        self.select_reward_use_case = select_reward_use_case
        self.unlock_reward_use_case = unlock_reward_use_case
        self.apply_multiplier_use_case = apply_multiplier_use_case
        self.player_profile_repository = player_profile_repository

    async def execute(self, user_ctx: dict):
        fishing_context_profile = await self.prepare_fishing_context_use_case.execute(user_ctx)
        selected_reward = await self.select_reward_use_case.execute(user_ctx=user_ctx, user_profile=fishing_context_profile)
        for id in selected_reward["reward"].get("unlocks", []):
            if id:
                fishing_context_profile = await self.unlock_reward_use_case.unlock_reward(user_profile=fishing_context_profile, reward_id=id)
        if selected_reward["reward"].get("global_unlocks"):
            global_profile = await self.unlock_reward_use_case.player_profile_repository.get_or_create_profile(
                user_id="global",
                username="global",
                channel_info={
                    "channel_id": fishing_context_profile.channel.id, 
                    "se_id": fishing_context_profile.channel.se_id, 
                    "name": fishing_context_profile.channel.name
                    }
            )
            for id in selected_reward["reward"].get("global_unlocks", []):
                if id:
                    global_profile = await self.unlock_reward_use_case.unlock_reward(user_profile=global_profile, reward_id=id)
            self.player_profile_repository.update_profile("global", global_profile)
        
        reward_buffed = await self.apply_multiplier_use_case.execute(
            reward=selected_reward["reward"],
            rewards_pool=selected_reward["rewards_pool"]
        )

        

        
