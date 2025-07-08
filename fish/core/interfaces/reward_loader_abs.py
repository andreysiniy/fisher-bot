from abc import abstractmethod
from typing import Protocol


class RewardLoaderAbstract(Protocol):
    """
    Interface for loading rewards from a source.
    """

    @abstractmethod
    async def load_rewards(self, username: str, channel_name: str) -> list[dict]:
        """
        Load rewards from the source.

        Args:
            username (str): The username of the user.
            channel_name (str): The name of the channel.

        Returns:
            list[dict]: A list of rewards, where each reward is represented as a dictionary.
        """
        pass
