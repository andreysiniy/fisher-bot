import json
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Generator


LOG_FILE_TEMPLATE =  "logs/{log_name}"

reward_order = [
    "total",
    "nothing",
    "points",
    "points_negative",
    "percentage_points",
    "percentage_points_negative",
    "robbery",
    "dupe",
    "russian_roulette",
    "timeout"
]

def parse_timestamp(timestamp_str):
    try:   
        if '.' in timestamp_str:
            dt_object = datetime.strptime(timestamp_str.replace('Z', ''), "%Y-%m-%dT%H:%M:%S.%f")
        else:
            dt_object = datetime.strptime(timestamp_str.replace('Z', ''), "%Y-%m-%dT%H:%M:%S")
        return dt_object.replace(tzinfo=timezone.utc)
    except ValueError as e:
        print(f"Timestamp parsing error: {timestamp_str} - {e}")
        return None

def calculate_stats_from_fish_log_data(log_data_list):
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for data in log_data_list:
        channel = data.get("channel")
        user = data.get("user")
        reward_info = data.get("reward", {}) 
        reward_type = reward_info.get("type")

        if not (channel and user and reward_type):
            continue

        
        if reward_type == "points":
            value = reward_info.get("value", 0)
            
            try:
                numeric_value = float(value)
                if numeric_value < 0:
                    reward_type = "points_negative"
            except (ValueError, TypeError):
                pass 
        elif reward_type == "percentage_points":
            percentage = reward_info.get("percentage", 0)
            try:
                numeric_percentage = float(percentage)
                if numeric_percentage < 0:
                    reward_type = "percentage_points_negative"
            except (ValueError, TypeError):
                pass

        stats[channel][user][reward_type] += 1
        stats[channel][user]["total"] += 1
    return stats

def calculate_se_stats_from_fish_log_data(log_data_list):
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for data in log_data_list:
        response_data = data.get("response_data", {})
        channel = response_data.get("channel")
        username = response_data.get("username")
        amount = response_data.get("amount", 0)
        if amount > 0:
            stats[channel][username]["gained_points"] += amount
            stats[channel][username]["biggest_fish_income"] = max(stats[channel][username]["biggest_fish_income"], amount)
        if amount < 0:
            stats[channel][username]["lost_points"] += abs(amount)
            stats[channel][username]["biggest_fish_loss"] = max(stats[channel][username]["biggest_fish_loss"], abs(amount))
        stats[channel][username]["fishing_income"] += amount
    
    return stats

def format_stats_output(stats_data):
    formatted_output = OrderedDict() 
    for channel, users in stats_data.items():
        
        sorted_users = sorted(users.items(), key=lambda item: item[1].get("total", 0), reverse=True)
        
        channel_dict = OrderedDict()  
        for user, counts in sorted_users:
            sorted_counts = OrderedDict()
            
            for key in reward_order:
                if key in counts:
                    sorted_counts[key] = counts[key]
            
            for key in sorted(counts.keys()): 
                if key not in sorted_counts:
                    sorted_counts[key] = counts[key]
            channel_dict[user] = sorted_counts
        formatted_output[channel] = channel_dict
    return formatted_output


def _stream_log_entries(file_path: str) -> Generator[Dict[str, Any], None, None]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    log_entry = json.loads(line)
                    timestamp_str = log_entry.get("timestamp")
                    if timestamp_str:
                        log_entry["timestamp"] = parse_timestamp(timestamp_str)
                        yield log_entry
                except json.JSONDecodeError:
                    print(f"Skipping malformed JSON on line {i} in {file_path}")
    except FileNotFoundError:
        print(f"Log file not found: {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred reading {file_path}: {e}")

def get_all_log_data(file_names: List[str], start_date: Optional[str] = None) -> Generator[Dict[str, Any], None, None]:
    start_datetime = parse_timestamp(start_date) if start_date else None

    for file_name in file_names:
        log_file_path = LOG_FILE_TEMPLATE.format(log_name=file_name)
        for entry in _stream_log_entries(log_file_path):
            if start_datetime and entry["timestamp"] < start_datetime:
                continue
            yield entry

def generate_fish_stats_report(file_names: List[str], start_date: Optional[str] = None) -> str:
    all_entries_stream = get_all_log_data(file_names, start_date)
    raw_stats = calculate_stats_from_fish_log_data(all_entries_stream)
    formatted_report = format_stats_output(raw_stats)

    return formatted_report

def generate_se_stats_report(file_names: List[str], start_date: Optional[str] = None) -> str:
    all_entries_stream = get_all_log_data(file_names, start_date)
    raw_stats = calculate_se_stats_from_fish_log_data(all_entries_stream)

    return raw_stats