from fish.core.use_cases.reward_handlers.base_reward_handler import BaseRewardHandler

class TimeoutRewardHandler(BaseRewardHandler):
    def __init__(self, reward: dict, rewards_pool: dict, user_ctx: dict):
        super().__init__(reward, rewards_pool, user_ctx)

    def handle(self) -> dict:
        actions = super().handle()

        seconds = self.reward.get("seconds", 0)
        username = self.user_ctx.get("username", "")
        delay = self.reward.get("delay", 0)
        reason = self.reward.get("reason", "")
        timeout_message = self.rewards_pool.get("timeout_message", "")

        if seconds > 0:
            actions["actions"].append({
                "timeout": {
                    "username": username,
                    "timeout": int(seconds),
                    "delay": int(delay),
                    "reason": reason
                }
            })
            actions["actions"].append({
                "message": timeout_message
            })

        return actions