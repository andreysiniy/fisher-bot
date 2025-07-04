import os
import json
import fish.helpers.log_checker as LogChecker
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

def add_fish_stats(channel_name: str, username: str, stats: dict):
    state = get_user_state(channel_name, username)
    if "fish_stats" not in state:
        state["fish_stats"] = {}
    
    state["fish_stats"].update(stats)
    
    save_user_state(channel_name, username, state)
    print(f"Fish stats for {username} on channel {channel_name} updated with: {stats}")

def add_fish_stats_from_logs(channel_name: str, start_date: str, log_files: list):
    temp_stats = LogChecker.generate_fish_stats_report(log_files, start_date)
    if not temp_stats:
        print("No valid log data found.")
        return
    
    channel_stats = temp_stats.get(channel_name, {})
    if not channel_stats:
        print(f"No stats found for channel {channel_name}.")
        return
    
    for username, user_stats in  channel_stats.items():
        add_fish_stats(channel_name, username, user_stats)