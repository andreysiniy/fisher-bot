from fish.core.use_cases.reward_handlers.base_reward_handler import BaseRewardHandler

class DupeRewardHandler(BaseRewardHandler):
    def __init__(self, reward, rewards_pool, user_ctx):
        super().__init__(reward, rewards_pool, user_ctx)

    def handle(self) -> dict:
        actions = super.handle()

        amount = self.user_ctx.get("amount", 1)
        delay = self.user_ctx.get("delay", 0)

        actions["actions"].append({
            "dupe": {
                "amount": amount,
                "delay": delay
            }
        })

        return actions