import os.path
import json
import random
import copy

class FishRewards:
    def __init__(self, chatterRole, rewardsFilePath):
        self.rewardsFile = rewardsFilePath
        with open(self.rewardsFile, 'r', encoding='utf-8') as file:
            self.rewardsJSON = json.load(file)
        self.chatterRole = chatterRole
        self.baseRewards = self.rewardsJSON["rewards"]
        self.cmds = self.rewardsJSON["cmds"]
        self.multiplier = self.rewardsJSON["base_multiplier"]
        if self.chatterRole == "sub":
            self.multiplier = self.rewardsJSON["sub_multiplier"]
        self.chosenReward = self.choose_default_reward()

    def get_probabilities(self):

        total_weight = sum(
            item.get("weight", 0) 
            for category in self.baseRewards.values() 
            for item in category
        )
    
        reward_probabilities = {}

        for category_name, category in self.baseRewards.items():
            if category_name == "nothing":
                continue  
            
            reward_probabilities[category_name] = []

            for item in category:
                weight = item.get("weight", 0)
                probability = round(weight / total_weight, 4) if total_weight > 0 else 0

                item_data = {"probability": probability}
            
                if "value" in item:
                    item_data["value"] = item["value"] * self.multiplier
                if "seconds" in item:
                    item_data["seconds"] = item["seconds"]
                if "percentage" in item:
                    item_data["percentage"] = item["percentage"]
                if "penalty_type" in item:
                    item_data["penalty_type"] = item["penalty_type"]
                
                reward_probabilities[category_name].append(item_data)
        return reward_probabilities
       

    def choose_default_reward(self):
        base_rewards_copy = copy.deepcopy(self.baseRewards)
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
        
        if chosen_reward["type"] == "points":
            chosen_reward["value"] *= self.multiplier 
        print(f"Chosen reward: {chosen_reward}")
        return chosen_reward


