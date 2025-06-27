import os.path
import json
import random
import copy
from fish.helpers.user_state import get_user_state
from fish.helpers.logger import get_logger

logger = get_logger()

def deep_merge(base, new):
    for key, new_value in new.items():
        if key in base:
            base_value = base[key]
            if isinstance(base_value, dict) and isinstance(new_value, dict):
                deep_merge(base_value, new_value)
            elif isinstance(base_value, list) and isinstance(new_value, list):
                base_value.extend(new_value)
            else:
                base[key] = new_value
        else:
            base[key] = new_value
    return base

def load_rewards_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"Warning: File not found, skipping: {file_path}")
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def resolve_inheritance_chain(config, file_path):
    
    if "extends" in config:
        parent_filename = config.pop("extends") 
        directory = os.path.dirname(file_path)
        parent_path = directory + "/"+ parent_filename
        parent_config = load_rewards_from_file(parent_path)
        merged_config = deep_merge(copy.deepcopy(parent_config), config)
        return resolve_inheritance_chain(merged_config, file_path)
    else:
        return config

def load_rewards_recursively(file_path):
    current_config = load_rewards_from_file(file_path)
    return resolve_inheritance_chain(current_config, file_path)

class FishRewards:
    def __init__(self, chatterRole, rewardsFilePath, username: str, channel_name: str):
        self.rewardsFile = rewardsFilePath
        self.rewardsJSON = load_rewards_recursively(rewardsFilePath)
        self.chatterRole = chatterRole
        self.channelName = channel_name
        self.username = username

        user_state = get_user_state(self.channelName, self.username)
        global_state = get_user_state(self.channelName, "global")
        unlocked_ids = set(user_state.get("unlocked_ids"))
        unlocked_ids.update(set(global_state.get("unlocked_ids")))
        filtered_base_rewards = {}
        for category, rewards_list in self.rewardsJSON["rewards"].items():
            
            available_rewards = []
            for reward in rewards_list:
                is_locked = reward.get("locked", False)
                reward_id = reward.get("id")

                if not is_locked or (reward_id and reward_id in unlocked_ids):
                    available_rewards.append(reward)
            
            if available_rewards:
                filtered_base_rewards[category] = available_rewards

        self.baseRewards = filtered_base_rewards
        self.cmds = self.rewardsJSON["cmds"]
        self.multiplier = self.rewardsJSON["base_multiplier"]
        if self.chatterRole == "sub":
            self.multiplier = self.rewardsJSON["sub_multiplier"]
        self.chosenReward = None

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
                    item_data["value"] = item["value"] 
                if "seconds" in item:
                    item_data["seconds"] = item["seconds"]
                if "percentage" in item:
                    item_data["percentage"] = item["percentage"]
                if "penalty_type" in item:
                    item_data["penalty_type"] = item["penalty_type"]
                if "amount" in item:
                    item_data["amount"] = item["amount"]
                if "title" in item:
                    item_data["title"] = item["title"]

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
        
        mult_mapper = {
            "value": lambda: chosen_reward.update({
                "value": (
                    int(chosen_reward["value"] * self.multiplier)
                    if chosen_reward["value"] > 0
                    else int(chosen_reward["value"] - chosen_reward["value"] * (self.multiplier - 1))
                )
            }),
            "percentage": lambda: chosen_reward.update({
                "percentage": (
                    chosen_reward["percentage"] * self.multiplier
                    if chosen_reward["percentage"] > 0
                    else chosen_reward["percentage"] - chosen_reward["percentage"] * (self.multiplier - 1)
                )
            }),
            "seconds": lambda: chosen_reward.update({
                "seconds": (
                    int(chosen_reward["seconds"] - chosen_reward["seconds"] * (self.multiplier - 1))
                )
            })
        }
        
        for key, handler in mult_mapper.items():
            if key in chosen_reward:
                handler()

        logger.info(f"{self.username} fished! on {self.channelName} channel", extra={"user": self.username, "channel": self.channelName, "reward": chosen_reward, "reward_path": self.rewardsFile})
        print(f"Chosen reward: {chosen_reward}")
        return chosen_reward


