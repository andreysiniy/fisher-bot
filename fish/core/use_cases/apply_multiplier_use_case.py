class ApplyMultiplierUseCase:
    async def execute(self, reward: dict, rewards_pool: dict, user_ctx: dict) -> dict:
        if not reward:
            raise ValueError("Reward is required.")

        multiplier = self._get_multiplier(user_ctx.get("is_subscriber", False), rewards_pool)
        reward = self.apply_multiplier(reward, multiplier)

        return reward

    def apply_multiplier(self, reward: dict, multiplier: float) -> dict:
        mult_mapper = {
            "value": lambda: reward.update({
                "value": (
                    int(reward["value"] * multiplier)
                    if reward["value"] > 0
                    else int(reward["value"] - reward["value"] * (multiplier - 1))
                )
            }),
            "percentage": lambda: reward.update({
                "percentage": (
                    reward["percentage"] * multiplier
                    if reward["percentage"] > 0
                    else reward["percentage"] - reward["percentage"] * (multiplier - 1)
                )
            }),
            "seconds": lambda: reward.update({
                "seconds": (
                    int(reward["seconds"] - reward["seconds"] * (multiplier - 1))
                )
            })
        }
        for key, update_func in mult_mapper.items():
            if key in reward:
                update_func()
        return reward

    def _get_multiplier(self, is_subscriber: bool, mult_dict: dict) -> float:
        if is_subscriber:
            return mult_dict.get("sub_multiplier", 1.0)
        return mult_dict.get("base_multiplier", 1.0)