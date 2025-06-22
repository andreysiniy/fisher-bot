import os
import json
from pathlib import Path

STATE_DIR_TEMPLATE = "rewards/{channel_name}/user_states"
STATE_FILE_TEMPLATE = STATE_DIR_TEMPLATE + "/{username}.json"

def get_user_state(channel_name: str, username: str) -> dict:
    state_path = STATE_FILE_TEMPLATE.format(channel_name=channel_name, username=username)
    if not os.path.exists(state_path):
        return {"unlocked_ids": []}
    
    with open(state_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_user_state(channel_name: str, username: str, state: dict):
    state_dir = STATE_DIR_TEMPLATE.format(channel_name=channel_name)
    Path(state_dir).mkdir(parents=True, exist_ok=True) 
    
    state_path = STATE_FILE_TEMPLATE.format(channel_name=channel_name, username=username)
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

def add_unlocked_ids(channel_name: str, username: str, ids_to_unlock: list) -> bool:
    state = get_user_state(channel_name, username)
    unlocked_set = set(state.get("unlocked_ids", []))
    
    new_ids_added = False
    for new_id in ids_to_unlock:
        if new_id not in unlocked_set:
            unlocked_set.add(new_id)
            new_ids_added = True

    if new_ids_added:
        state["unlocked_ids"] = list(unlocked_set)
        save_user_state(channel_name, username, state)
        print(f"State for {username} on channel {channel_name} updated with IDs: {ids_to_unlock}")
        return True
    return False