from fish.core.use_cases.reward_handlers.base_reward_handler import BaseRewardHandler
from fish.core.use_cases.reward_handlers.points_reward_handler import PointsRewardHandler
from fish.core.use_cases.reward_handlers.timeout_reward_handler import TimeoutRewardHandler
from fish.core.use_cases.reward_handlers.percentage_points_reward_handler import PercentagePointsRewardHandler
import random

class RussianRouletteRewardHandler(BaseRewardHandler):
    def __init__(
            self, 
            reward: dict, 
            rewards_pool: dict, 
            user_ctx: dict
            ):
        super().__init__(
            reward, 
            rewards_pool, 
            user_ctx
            )
        self.points_rh = PointsRewardHandler(reward, rewards_pool, user_ctx)
        self.percentage_rh = PercentagePointsRewardHandler(reward, rewards_pool, user_ctx)
        self.timeout_rh = TimeoutRewardHandler(reward, rewards_pool, user_ctx)

    def handle(self) -> dict:
        actions = super().handle()

        username = self.user_ctx.get("username", "")
        points = self.reward.get("value", 0)
        percentage = self.reward.get("percentage", 0)
        seconds = self.reward.get("seconds", 0)
        bullets = self.reward.get("bullets", 1)
        chambers = self.reward.get("chambers", 6)
        was_shot = self._was_shot(bullets, chambers)

        if was_shot:
            if points != 0:
                actions["actions"].extend(self.points_rh.handle_points().get("actions", []))
            if percentage != 0:
                actions["actions"].extend(self.percentage_rh.handle_percentage().get("actions", []))
            if seconds > 0:
                actions["actions"].extend(self.timeout_rh.handle_timeout().get("actions", []))
            actions["actions"].append({
                "message": {
                    "username": username,
                    "message": self.rewards_pool.get("shot_message", ""),
                }
            })
        else:
            actions["actions"].append({
                "message": {
                    "username": username,
                    "message": self.rewards_pool.get("miss_message", ""),
                }
            })

        return actions
    
    def _was_shot(self, bullets: int, chambers: int) -> bool:
        cylinder = [1]*bullets + [0]*(chambers - bullets)
        random.shuffle(cylinder) 
        return random.choice(cylinder) == 1  