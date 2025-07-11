from abc import abstractmethod
from typing import Protocol


class RewardLoaderAbstract(Protocol):
    """
    Interface for loading rewards from a source.
    """

    @abstractmethod
    def load_rewards(self, channel_name: str, user_role: str) -> dict:
        """
        Load rewards from the source.

        Args:
            channel_name (str): The name of the channel.
            user_role (str): The role of the user (e.g., "vip", "mod", "base").

        Returns:
            dict: A dictionary of rewards.
        """
        pass
