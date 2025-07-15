from fish.core.use_cases.reward_handlers import BaseRewardHandler, DupeRewardHandler, PercentagePointsRewardHandler, PointsRewardHandler, RussianRouletteRewardHandler, RobberyRewardHandler, TimeoutRewardHandler
from fish.core.use_cases.reward_handlers import NothingRewardHandler, CustomRewardHandler

class RewardHandlerFactory:
    def __init__(self):
        self._handlers = {
            "points": PointsRewardHandler,
            "timeout": TimeoutRewardHandler,
            "percentage_points": PercentagePointsRewardHandler,
            "russian_roulette": RussianRouletteRewardHandler,
            "robbery": RobberyRewardHandler,
            "dupe": DupeRewardHandler,
            "nothing": NothingRewardHandler
        }

    def get_handler(self, user_ctx: dict, reward: dict, rewards_pool: dict) -> BaseRewardHandler:
        reward_type = reward.get("type")
        handler_class = self._handlers.get(reward_type, CustomRewardHandler)
        handler = handler_class(reward, user_ctx, rewards_pool)

        return handler
