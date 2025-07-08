from fish.core.interfaces.reward_loader_abs import RewardLoaderAbstract
import json
import os.path
import copy

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

REWARDS_PATH_TEMPLATE = "rewards/{channel_name}/"
REWARDS_CFG_TEMPLATE = REWARDS_PATH_TEMPLATE + "path_cfg.json"

def get_fish_rewards_file_path(channel_name: str, user_role: str) -> str:
    rewardsFilePathCfg = REWARDS_CFG_TEMPLATE.format(channel_name=channel_name)
    rewardsFilePath = REWARDS_PATH_TEMPLATE.format(channel_name=channel_name)
    with open(rewardsFilePathCfg, 'r', encoding='utf-8') as f:
        pathCfg = json.load(f)
    if user_role == "vip":
        rewardsFilePath += pathCfg.get("vip", "fishRewards_vip.json")
    elif user_role == "mod" or user_role == "broadcaster":
        rewardsFilePath += pathCfg.get("mod", "fishRewards_mod.json")
    else:
        rewardsFilePath += pathCfg.get("base", "fishRewards.json")
    return rewardsFilePath
    

class RewardLoader(RewardLoaderAbstract):

    def load_rewards(self, channel_name: str, user_role: str) -> list[dict]:
        rewards_file_path = get_fish_rewards_file_path(channel_name, user_role)
        return load_rewards_recursively(rewards_file_path)
    
