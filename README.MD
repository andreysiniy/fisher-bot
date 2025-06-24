# Man I Love Fishing

Fisher Bot is a highly configurable Twitch chat bot that allows viewers to play a "fishing" game. Users can use the `!fish` command to receive a random reward from a weighted pool. The bot is designed to be deeply customizable on a per-channel basis, with a powerful reward system managed through JSON files and integration with StreamElements for channel points.

## Core Features

*   **Weighted Fishing Game**: A `!fish` command that pulls rewards from a weighted, random pool.
*   **Rich Reward System**: Supports various reward types:
    *   Add/remove StreamElements points (fixed or percentage-based).
    *   User timeouts.
    *   Point robbery from other users.
    *   Russian Roulette (chance-based penalties).
    *   Reward Duplication (`!fish` again multiple times).
    *   Custom message-based rewards.
*   **Role-Based Rewards**: Different reward pools and cooldowns for regular users, VIPs, and moderators.
*   **Configuration Inheritance**: Reward files can `extend` other files, allowing for a base configuration to be easily modified for different roles without duplication.
*   **Persistent Reward Unlocks**: A system to unlock new, rare rewards for individual users or globally for the channel by "fishing" up special items.
*   **StreamElements Integration**: Manages user points and leaderboard lookups via the StreamElements API.
*   **Dockerized**: Comes with a `Dockerfile` for easy, containerized deployment.
*   **Customizable**: Cooldowns, multipliers, messages, and probabilities are all configurable.


## Configuration

Before running the bot, you must create and configure the `cfg.ini` file.

```ini
[TWITCH]
# The channel(s) list that bot will join.
# To join multiple channels, separate them with a comma: channel1, channel2
username = example
# The prefix for commands (e.g., !, ?)
command-prefix = !
# Twitch OAuth token for the bot account. Get one from https://twitchapps.com/tmi/
token = oauth:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Yours Bot StreamElements JWT token for point management. Needs a Bot Supervisor permission. Get one from https://streamelements.com/dashboard/account/channels
streamelements-jwt = ...
# (Optional) Set to True to notify users when a command is on cooldown.
enable-cooldown-msg = True
# (Optional) Your Twitch application's client secret. Not currently used.
client-secret =
```

## The Reward System

The core of Fisher Bot is its JSON-based reward system, located in the `rewards/` directory. Each channel the bot operates in requires its own subdirectory.

### 1. Channel and Role Configuration (`rewards/<channel_name>/path_cfg.json`)

This file tells the bot which reward file to use based on the user's role in chat.

**Example: `rewards/example/path_cfg.json`**
```json
{
    "base": "fishRewards.json",
    "vip": "fishRewards_vip.json",
    "mod": "fishRewards_mod.json"
}
```
*   `base`: The file for a regular user.
*   `vip`: The file for a VIP.
*   `mod`: The file for a moderator or the broadcaster.

### 2. Reward File Structure & Inheritance

Reward files define the possible outcomes of the `!fish` command. The `extends` key is used to build configurations on top of each other, reducing repetition.

**Example Inheritance Chain:**
`fishRewards.json` → `extends: "fishRewards_vip.json"` → `extends: "fishRewards_mod.json"`

In this chain, `fishRewards.json` will contain all rewards from `fishRewards_vip.json`, which in turn contains all rewards from `fishRewards_mod.json`. This allows you to define a base set of rewards for mods, add more for VIPs, and add even more for regular users.

**Example: `rewards/example/fishRewards_mod.json`**
```json
{
    "base_message": "{username} is fishing! !fish ... ",
    "base_multiplier": 1.0,
    "sub_multiplier": 1.3,
    "base_cooldown": 600,
    "sub_cooldown": 300,
    "rewards": {
        "nothing": [
            { "weight": 450, "message": "NOTHING..." }
        ],
        "points": [
            { "value": 10000, "weight": 350, "message": "You caught a big one! +{value}" }
        ]
    }
}
```

**Example: `rewards/example/fishRewards_vip.json`**
```jsonc
{
    "extends": "fishRewards_mod.json",
    "rewards": {
        "timeout": [
            { "seconds": 120, "weight": 50, "message": "You broke your rod! Unlucky {time} timeout!" } // Adding timeout reward for users with VIP role or lower, since mods cant get timed out 
        ]
    }
}
```

### 3. Reward Types & Properties

Rewards are defined in a dictionary where the key is the reward `type`.

| Type                | Description                                                | Key Properties                                                                                                                                                             |
| ------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `points`            | Adds/removes a fixed number of SE points.                  | `value` (int, can be negative), `weight` (int), `message` (str)                                                                                                            |
| `percentage_points` | Adds/removes points based on a percentage of user's total. | `percentage` (float, e.g., 0.1 for 10%), `weight`, `message`                                                                                                               |
| `timeout`           | Times out the user.                                        | `seconds` (int), `weight`, `message`                                                                                                                                       |
| `robbery`           | Steals points from another user near the user's rank.      | `value` or `percentage`, `range` (int, how far up the leaderboard to look), `weight`, `message`, `robbery_message`                                                         |
| `russian_roulette`  | A game of chance with a configurable penalty.              | `chambers`, `bullets`, `penalty_type` (`timeout`, `points`, `percentage`), penalty properties (`seconds`, `value`, etc.), `shot_message`, `safe_message`, `weight`         |
| `dupe`              | Executes the `!fish` command again N times.                | `amount` (int, number of extra fishes), `delay` (int, seconds between fishes), `weight`, `message`                                                                         |
| `vip`               | A message-only reward, intended for granting VIP status.   | `weight`, `message`                                                                                                                                                        |
| `nothing`           | The user gets nothing.                                     | `weight`, `message`                                                                                                                                                        |
| *Custom*            | Any other key will be treated as a custom reward.          | `weight`, `message`, `cmd` (A string with placeholders like `{username}` that will be sent as a chat message)                                                               |

### 4. Message Placeholders

When defining messages for your rewards (e.g., in `message`, `shot_message`, `robbery_message`, etc.), you can use several placeholders that the bot will automatically replace with dynamic values.

| Placeholder      | Description                                                    | Example Usage (Reward Type)                       |
| ---------------- | -------------------------------------------------------------- | ------------------------------------------------- |
| `{username}`     | The name of the user who fished.                               | All                                               |
| `{value}`        | The number of points, formatted (e.g., 1.5K, 10M).             | `points`, `russian_roulette`, `robbery`           |
| `{time}`         | The duration, formatted (e.g., 5m 30s).                        | `timeout`, `russian_roulette`                     |
| `{percentage}`   | The percentage, formatted (e.g., 10.5%).                       | `percentage_points`, `russian_roulette`, `robbery`|
| `{amount}`       | The number of times to duplicate a fish.                       | `dupe`                                            |
| `{delay}`        | The delay in seconds between duplicated fishes.                | `dupe`                                            |
| `{bullets}`      | The number of bullets in the chamber.                          | `russian_roulette`                                |
| `{chambers}`     | The total number of chambers in the revolver.                  | `russian_roulette`                                |
| `{victim}`       | The name of the user being robbed. **Only in `robbery_message`** | `robbery`                                         |


### 5. Reward Unlocks (Persistent State)

You can create "locked" rewards that only become available after a specific trigger. This is useful for creating scavenger hunts or rare, evolving rewards.

**How it works:**
1.  **Create a locked reward:** Add `"locked": true` and a unique `"id"` to a reward.
    ```json
    "percentage_points": [
        {
            "id": "perc_100",
            "percentage": 1.0,
            "weight": 1000,
            "message": "WOW SECRET BITCOIN DRIVE +{percentage}",
            "locked": true
        }
    ]
    ```
2.  **Create an unlocking reward:** Add a `global_unlocks` or `unlocks` key to another reward.
    *   `global_unlocks`: Unlocks the reward for *everyone* in the channel.
    *   `unlocks`: Unlocks the reward only for the user who fished it up.

    ```jsonc
    "nothing": [
       {
            "weight": 100,
            "message": "OH YOU FISHED UP A FLOATING BOTTLE! ...",
            "global_unlocks": ["note_2"], // This unlocks the reward with id "note_2", for unlocking multiple rewards, separate ids with comma.
            "unlock_message": "{username} as you reel in your line, a strange sigil glows..."
        }
    ]
    ```
3.  **State Management**: When an unlock is triggered, the bot saves the `id` to a file in `rewards/<channel_name>/user_states/`. It will be either `global.json` or `<username>.json`. The bot checks these files to determine which locked rewards are available for a given user.

## Commands

*   `!fish`
    *   Triggers the fishing game. The bot selects a reward from the appropriate JSON file, applies any multipliers (for subs), and executes the reward logic.
    *   This command has a dynamic cooldown set in the reward files.

*   `!fishrewards`
    *   Displays all possible non-nothing rewards and their catch probabilities for the user's role. The message is split into chunks to avoid chat limits. You can set up display name for custom rewards using `"title"` parameter.

*   `!fishcooldown`
    *   Tells the user what their current cooldown is for the `!fish` command.

## Installation & Usage

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/andreysiniy/fisher-bot.git
    cd fisher-bot
    ```

2.  **Create and activate a virtual environment:**
    It's highly recommended to use a virtual environment to keep project dependencies isolated.
    
    *   **On macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **On Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure:**
    *   Create a `cfg.ini` file and fill in your bot's credentials (see Configuration section).
    *   Create a directory for your channel inside the `rewards/` folder (e.g., `rewards/mychannel/`).
    *   Populate your channel's directory with `path_cfg.json` and the corresponding reward `.json` files. You can use the files in `rewards/` as a template.

5.  **Run the bot:**
    ```bash
    python -m fish.main
    ```

### Docker Deployment

The `Dockerfile` allows you to build and run the bot in a container. It copies the entire project context, so ensure your `cfg.ini` and `rewards/` directory are configured before building.

1.  **Configure the project** as described in the local setup.

2.  **Build the Docker image:**
    ```bash
    docker build -t fisher-bot .
    ```

3.  **Run the container:**
    ```bash
    docker run -d --name fisher-bot --restart unless-stopped fisher-bot
    ```
