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

        base_msg = { "message": self.rewards_pool.get("base_message", "") + self.reward.get("message", "")}

        actions.append(base_msg)

        return {"actions": actions}