import os.path
import json
import random

class FishRewards:
    def __init__(self, chatterRole):
        self.rewardsFile = 'fishRewards.json'
        with open(self.rewardsFile, 'r') as file:
            self.rewardsJSON = json.load(file)
        self.chatterRole = chatterRole
        self.baseRewards = self.rewardsJSON["rewards"]
        self.cmds = self.rewardsJSON["cmds"]
        self.multiplier = self.rewardsJSON["base_multiplier"]
        if self.chatterRole == "sub":
            self.multiplier = self.rewardsJSON["sub_multiplier"]
        self.chosenReward = self.choose_default_reward()

    def choose_default_reward(self):
        all_rewards = []
        weights = []
        types = []

        for key, category in self.baseRewards.items():
            for reward in category:
                all_rewards.append(reward)
                weights.append(reward["weight"])
                types.append(key)

        chosen_reward = random.choices(all_rewards, weights=weights, k=1)[0]
        chosen_type = types[all_rewards.index(chosen_reward)]

        chosen_reward["type"] = chosen_type
        if chosen_type != "nothing":
            chosen_reward["cmd"] = self.cmds[chosen_type]
        else:
            chosen_reward["cmd"] = ""
        
        if chosen_reward["type"] == "points":
            chosen_reward["value"] *= self.multiplier 
        return chosen_reward

#for i in range(2000):
#    test = FishRewards()
#    print(test.chosenReward)