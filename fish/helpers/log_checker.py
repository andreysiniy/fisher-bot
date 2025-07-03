import json
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta, timezone



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

def format_stats_output(stats_data):
    formatted_output = OrderedDict() 
    for channel, users in stats_data.items():
        
        sorted_users = sorted(users.items(), key=lambda item: item[1].get("total", 0), reverse=True)
        
        channel_dict = OrderedDict() # 
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

def read_fish_log_files(file_names : list, start_date: str = None):
    log_data_list = []
    for file_name in file_names:
        log_file_path = LOG_FILE_TEMPLATE.format(log_name=file_name)
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip(): 
                        try:
                            log_data = json.loads(line.strip())
                            timestamp_str = log_data.get("timestamp")
                            if timestamp_str:
                                log_data["timestamp"] = parse_timestamp(timestamp_str)
                                if start_date:
                                    if log_data["timestamp"] < parse_timestamp(start_date):
                                        continue
                                log_data_list.append(log_data)
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error in file {log_file_path}: {e}")
        except FileNotFoundError as e:
            print(f"Log file not found: {log_file_path} - {e}")
    recent_stats_raw = calculate_stats_from_fish_log_data(log_data_list)
    formatted_stats = format_stats_output(recent_stats_raw)
    return formatted_stats

