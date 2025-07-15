class BaseRewardHandler:
    def __init__(
            self, 
            reward: dict,
            rewards_pool: dict,
            user_ctx: dict
    ):
        self.reward = reward
        self.user_ctx = user_ctx
        self.rewards_pool = rewards_pool

    def handle(self) -> dict:
        actions = []
        username = self.user_ctx.get("username", "")
        base_msg = { "message":  {
            "username": username,
            "message": self.rewards_pool.get("base_message", "") + self.reward.get("message", "")
            }
        }

        if base_msg.get("message"):
            actions.append(base_msg)

        return {"actions": actions}