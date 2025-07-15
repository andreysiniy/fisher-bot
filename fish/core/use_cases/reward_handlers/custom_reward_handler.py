from fish.core.use_cases.reward_handlers.base_reward_handler import BaseRewardHandler

class CustomRewardHandler(BaseRewardHandler):
    def __init__(self, reward, rewards_pool, user_ctx):
        super().__init__(reward, rewards_pool, user_ctx)

    def handle(self):
        # TODO: Implement custom actions handling
        return super().handle()