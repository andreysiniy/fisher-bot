from fish.core.use_cases.reward_handlers.base_reward_handler import BaseRewardHandler
import random

class RobberyRewardHandler(BaseRewardHandler):
    def __init__(self, reward: dict, rewards_pool: dict, user_ctx: dict):
        super().__init__(reward, rewards_pool, user_ctx)

    def handle(self) -> dict:
        actions = super().handle()

        robbed_user = self._get_robbed_user()    
        username = self.user_ctx.get("username", "")

        points = self.reward.get("value", 0)
        percentage = self.reward.get("percentage", 0)
        delay = self.reward.get("delay", 0)

        if not robbed_user:
            actions["actions"].append({
                "message": {
                    "username": username,
                    "message": self.rewards_pool.get("robbery_failure_message", ""),
                    "delay": delay
                }
            })
            return actions

        victim = robbed_user.get("username", "") 
        victim_points = robbed_user.get("points", 0)
        

        if points > 0:
            points_to_rob = min(points, victim_points)
            actions["actions"].extend(self.handle_points_swap(username, victim, points_to_rob, delay).get("actions", []))
        if percentage > 0:
            points_to_rob = min(int(victim_points * percentage), victim_points)
            actions["actions"].extend(self.handle_points_swap(username, victim, points_to_rob, delay).get("actions", []))
        if self.reward.get("robbery_message"):
            actions["actions"].append({
                "username": username,
                "points": points_to_rob,
                "victim": victim,
                "victim_points": victim_points,
                "message": self.reward.get("robbery_message", "")
            })

        return actions

    def handle_points_swap(self, user1: str, user2: str, points: int, delay: int) -> dict:
        actions = {"actions": []}

        if points > 0:
            actions["actions"].append({
                "add_points": {
                    "username": user1,
                    "points": int(points),
                    "delay": delay
                }
            })
            actions["actions"].append({
                "remove_points": {
                    "username": user2,
                    "points": int(points),
                    "delay": delay
                }
            })

        return actions
    
    def _get_robbed_user(self) -> dict:
        robbery_users_pool = self.user_ctx.get("robbery_users_pool", [])
        if not robbery_users_pool:
            return None
        return random.choice(robbery_users_pool) if robbery_users_pool else None
        