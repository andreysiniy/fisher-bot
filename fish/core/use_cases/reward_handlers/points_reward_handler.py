from fish.core.use_cases.reward_handlers.base_reward_handler import BaseRewardHandler

class PointsRewardHandler(BaseRewardHandler):
    def __init__(self, reward: dict, rewards_pool: dict, user_ctx: dict):
        super().__init__(reward, rewards_pool, user_ctx)

    def handle(self) -> dict:
        actions = super().handle()
        
        points = self.reward.get("points", 0)
        username = self.user_ctx.get("username", "")
        delay = self.reward.get("delay", 0)

        if points > 0:
            actions["actions"].append({
                "add_points": {
                    "username": username,
                    "points": int(points),
                    "delay": delay
                }
            })
        else:
            actions["actions"].append({
                "remove_points": {
                    "username": username,
                    "points": int(abs(points)),
                    "delay": delay
                }
            })

        if self.rewards_pool.get("points_message"):
            actions["actions"].append({
                "message": {
                    "username": username,
                    "points": int(points),
                    "message": self.rewards_pool.get("points_message", "")
                }
            })

        return actions