

def format_number(value):
    if value % 1 == 0:
        return str(int(value))
    else:
        formatted_value = f"{value:.2f}"
        return str(float(formatted_value))

def generate_reward_strings(reward_probabilities):
    reward_strings = []

    for category_name, items in reward_probabilities.items():
        for item in items:
            if category_name == "points":
                reward_string = f"Points: {format_number(item['value']//1000)}K - {item['probability']*100:.2f}%"
            elif category_name == "timeout":
                reward_string = f"Timeout: {item['seconds']} seconds - {item['probability']*100:.2f}%"
            elif category_name == "vip":
                reward_string = f"VIP - {item['probability']*100:.2f}%"
            reward_strings.append(reward_string)
    
    return reward_strings