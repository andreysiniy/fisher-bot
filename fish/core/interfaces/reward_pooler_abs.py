from abc import abstractmethod
from typing import Protocol

class RewardPoolerAbstract(Protocol):
    """
    Interface for a reward pooler that manages rewards for users in a Twitch channel.
    """

    @abstractmethod
    def get_random_reward(self, rewards: list[dict]) -> dict:
        """
        Get a random reward for a user in a specific channel.

        Args:
            rewards (list[dict]): A list of reward dictionaries.

        Returns:
            dict: A dictionary representing the reward.
        """
        pass