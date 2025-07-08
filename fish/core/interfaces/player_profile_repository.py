from abc import ABC, abstractmethod
from typing import Protocol
from ..entities import PlayerProfile

class PlayerProfileRepository(Protocol):

    @abstractmethod
    async def get_or_create_profile(self, user_id: str) -> PlayerProfile:
        """
        Retrieve or create player profile for a given user ID.

        Args:
            user_id (str): The ID of the user.

        Returns:
            PlayerProfile: The player profile if found, otherwise a new profile.
        """
        pass

    @abstractmethod
    async def update_profile(self, user_id: str, profile: PlayerProfile) -> None:
        """
        Update the player profile for a given user ID.

        Args:
            user_id (str): The ID of the user.
            profile (PlayerProfile): The updated player profile.
        """
        pass

    @abstractmethod
    async def delete_profile(self, user_id: str) -> None:
        """
        Delete the player profile for a given user ID.

        Args:
            user_id (str): The ID of the user.
        """
        pass

    @abstractmethod
    async def create_profile(self, user_id: str, profile: PlayerProfile) -> None:
        """
        Create a new player profile for a given user ID.

        Args:
            user_id (str): The ID of the user.
            profile (PlayerProfile): The player profile to create.
        """
        pass

    @abstractmethod
    async def get_top_by_points_income(self, channel_id: str, limit: int = 10) -> list[PlayerProfile]:
        """
        Get the top player profiles by points income in a specific channel.

        Args:
            channel_id (str): The ID of the channel.
            limit (int): The maximum number of profiles to return.

        Returns:
            list[PlayerProfile]: A list of player profiles sorted by points income.
        """
        pass

    @abstractmethod
    async def get_top_by_fishes_caught(self, channel_id: str, limit: int = 10) -> list[PlayerProfile]:
        """
        Get the top player profiles by fishes caught in a specific channel.

        Args:
            channel_id (str): The ID of the channel.
            limit (int): The maximum number of profiles to return.

        Returns:
            list[PlayerProfile]: A list of player profiles sorted by fishes caught.
        """
        pass