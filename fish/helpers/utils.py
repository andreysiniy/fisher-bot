

def format_number(value):
    if value % 1 == 0:
        return str(int(value))
    else:
        formatted_value = f"{value:.2f}"
        return str(float(formatted_value))
    
def format_large_number(value):
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000_000:
        value = value / 1_000_000_000_000_000
        return f"{value:.2f}".rstrip('0').rstrip('.') + "Q"
    elif abs_value >= 1_000_000_000_000:
        value = value / 1_000_000_000_000
        return f"{value:.2f}".rstrip('0').rstrip('.') + "T"
    elif abs_value >= 1_000_000_000:
        value = value / 1_000_000_000
        return f"{value:.2f}".rstrip('0').rstrip('.') + "B"
    elif abs_value >= 1_000_000:
        value = value / 1_000_000
        return f"{value:.2f}".rstrip('0').rstrip('.') + "M"
    elif abs_value >= 1_000:
        value = value / 1_000
        return f"{value:.2f}".rstrip('0').rstrip('.') + "K"
    else:
        return f"{value:.2f}".rstrip('0').rstrip('.')  
    
def format_large_number_sign(value):
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000_000:
        value = value / 1_000_000_000_000_000
        return f"{value:+.2f}".rstrip('0').rstrip('.') + "Q"
    elif abs_value >= 1_000_000_000_000:
        value = value / 1_000_000_000_000
        return f"{value:+.2f}".rstrip('0').rstrip('.') + "T"
    elif abs_value >= 1_000_000_000:
        value = value / 1_000_000_000
        return f"{value:+.2f}".rstrip('0').rstrip('.') + "B"
    elif abs_value >= 1_000_000:
        value = value / 1_000_000
        return f"{value:+.2f}".rstrip('0').rstrip('.') + "M"
    elif abs_value >= 1_000:
        value = value / 1_000
        return f"{value:+.2f}".rstrip('0').rstrip('.') + "K"
    else:
        return f"{value:+.2f}".rstrip('0').rstrip('.')  

def format_time(seconds):
    seconds = int(seconds)

    days = seconds // 86400
    seconds %= 86400

    hours = seconds // 3600
    seconds %= 3600

    minutes = seconds // 60
    seconds %= 60

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")

    return ' '.join(parts)

def format_percent(value):
    percent = value * 100
    formatted = f"{percent:.2f}".rstrip('0').rstrip('.')
    return f"{formatted}%"


def generate_reward_strings(reward_probabilities):
    reward_strings = []

    reward_formatters = {
        "points": lambda item: f"Points: {format_large_number_sign(item['value'])} - {format_percent(item['probability'])}",
        "timeout": lambda item: f"Timeout: {format_time(item['seconds'])} - {format_percent(item['probability'])}",
        "vip": lambda item: f"VIP - {format_percent(item['probability'])}",
        "russian_roulette": lambda item: f"RR: {item['penalty_type']} - {format_percent(item['probability'])}",
        "percentage_points": lambda item: f"Percentage Points: {format_percent(item['percentage'])} - {format_percent(item['probability'])}",
        "robbery": lambda item: (
    f"Robbery: "
    + (
        f"{format_large_number(item['value'])}"
        if "value" in item
        else f"{format_percent(item['percentage'])}"
        if "percentage" in item
        else ""
    )
    + f" - {format_percent(item['probability'])}"
)

    }

    reward_strings = []

    for category_name, items in reward_probabilities.items():
        for item in items:
            formatter = reward_formatters.get(category_name, lambda item: f"Custom Reward: {format_percent(item['probability'])}")
            reward_string = formatter(item)
            reward_strings.append(reward_string)

    return reward_strings