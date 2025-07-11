from fish.core.interfaces.reward_pooler_abs import RewardPoolerAbstract
import random
import copy

class RewardPooler(RewardPoolerAbstract):

    def get_random_reward(self, rewards: dict) -> dict:
        if not rewards:
            return {}
        base_rewards_copy = copy.deepcopy(rewards)
        all_rewards = []
        weights = []
        types = []

        for key, category in base_rewards_copy.items():
            for reward in category:
                all_rewards.append(reward)
                weights.append(reward["weight"])
                types.append(key)
        chosen_reward = random.choices(all_rewards, weights=weights, k=1)[0]
        chosen_type = types[all_rewards.index(chosen_reward)]

        chosen_reward["type"] = chosen_type

        chosen_reward["cmd"] = self.cmds.get(chosen_type, "")

        return chosen_reward
