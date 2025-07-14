from fish.core.use_cases.reward_handlers.base_reward_handler import BaseRewardHandler

class PercentagePointsRewardHandler(BaseRewardHandler):
    def __init__(self, reward: dict, rewards_pool: dict, user_ctx: dict):
        super().__init__(reward, rewards_pool, user_ctx)

    def handle(self) -> dict:
        actions = super().handle()
        actions["actions"].extend(self.handle_percentage())
        return actions
    
    def handle_percentage(self) -> dict:    
        percentage = self.reward.get("percentage", 0)
        username = self.user_ctx.get("username", "")
        delay = self.reward.get("delay", 0)
        user_points = self.user_ctx.get("points", 0)
        points_to_add = int(user_points * percentage)
        actions = {"actions": []}

        if points_to_add > 0:
            actions["actions"].append({
                "add_points": {
                    "username": username,
                    "points": int(points_to_add),
                    "delay": delay
                }
            })
        else:
            actions["actions"].append({
                "remove_points": {
                    "username": username,
                    "points": int(abs(points_to_add)),
                    "delay": delay
                }
            })

        if self.rewards_pool.get("points_message"):
            actions["actions"].append({
                "message": {
                    "username": username,
                    "points": points_to_add,
                    "message": self.rewards_pool.get("points_message", "")
                }
            })

        return actions