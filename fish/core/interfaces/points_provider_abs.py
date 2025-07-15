from abc import abstractmethod
from typing import Protocol

class PointsProviderAbstract(Protocol):

    @abstractmethod
    async def get_channel_id(self, name: str) -> str:
        """
        Retrieve the channel ID for a given channel name.
        
        Args:
            name (str): The name of the channel.
        
        Returns:
            str: The channel ID.        
        """
        pass

    @abstractmethod
    async def get_user_points(self, user: str, channel_id: str) -> int:
        """
        Retrieve the points of a user in a specific channel.
        
        Args:
            user (str): The username of the user.
            channel_id (str): The ID of the channel.
        
        Returns:
            int: The number of points the user has.
        """
        pass

    @abstractmethod
    async def add_user_points(self, user: str, channel_id: str, points: int):
        """
        Add points to a user's account in a specific channel.
        
        Args:
            user (str): The username of the user.
            channel_id (str): The ID of the channel.
            points (int): The number of points to add.
        """
        pass

    @abstractmethod
    async def remove_user_points(self, user: str, channel_id: str, points: int):
        """
        Remove points from a user's account in a specific channel.
        
        Args:
            user (str): The username of the user.
            channel_id (str): The ID of the channel.
            points (int): The number of points to remove.
        """
        pass

    @abstractmethod
    async def get_user_rank(self, user: str, channel_id: str) -> int:
        """
        Retrieve the rank of a user in a specific channel.
        
        Args:
            user (str): The username of the user.
            channel_id (str): The ID of the channel.
        
        Returns:
            int: The rank of the user.
        """
        pass

    @abstractmethod
    async def get_username_by_rank(self, rank: int, channel_id: str) -> str:
        """
        Retrieve the username of a user by their rank in a specific channel.
        
        Args:
            rank (int): The rank of the user.
            channel_id (str): The ID of the channel.
        
        Returns:
            str: The username of the user with the specified rank.
        """
        pass

    @abstractmethod
    async def list_top_userpoints(self, limit: int, offset: int, channel_id: str) -> dict:
        """
        Retrieve the userpoints top in a specific channel

        Args:
            limit (int): Number of items per page.
            offset (int): Number of items to be skipped.
            channel_id (str): The ID of the channel.
        
        Returns:
            dict: Dictionary that contains a list of items containing userpoints of users in the specific limits.
        """
        pass