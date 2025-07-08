from abc import abstractmethod
from typing import Protocol

class TwitchActionsProvider(Protocol):
    """
    Interface for providing Twitch actions.
    """

    @abstractmethod
    async def timeout_user(self, channel_name: str, user: str, duration: int, reason: str = "") -> None:
        """
        Timeout a user in the Twitch channel.

        Args:
            channel_name (str): The name of the Twitch channel.
            user (str): The username of the user to timeout.
            duration (int): Duration of the timeout in seconds.
            reason (str): Reason for the timeout.
        """
        pass

    @abstractmethod
    async def send_formatted_message(self, channel_name: str, message: str) -> None:
        """
        Send a formatted message to the Twitch channel.

        Args:
            channel_name (str): The name of the channel.
            message (str): The message to send.
        """
        pass