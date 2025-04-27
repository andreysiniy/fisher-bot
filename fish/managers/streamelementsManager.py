from helpers.configurator import Config
from aiohttp import ClientSession

class StreamElementsManager:
    def __init__(self):
        self.config = Config()
        self.jwt = self.config.streamelementsJWT
        print(f"StreamElements Initialized")    

    async def get_channel_id(self, name: str):
        """
        Retrieve the channel ID for a given channel name.
        
        Args:
            name (str): The name of the channel.
        
        Returns:
            str: The channel ID.
        """
        async with ClientSession() as session:
            url = f"https://api.streamelements.com/kappa/v2/channels/{name}"
            headers = {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.jwt}"
            }
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Channel ID for {name}: {data.get('_id')}")
                    return data.get("_id")
                else:
                    response.raise_for_status()

    async def get_user_points(self, user: str, channel_id: str):
        """
        Retrieve the points of a user in a specific channel.
        
        Args:
            user (str): The username of the user.
            channel_id (str): The ID of the channel.
        
        Returns:
            int: The number of points the user has.
        """
        async with ClientSession() as session:
            url = f"https://api.streamelements.com/kappa/v2/points/{channel_id}/{user}"
            headers = {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.jwt}"
            }
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"User: {user} has {data.get("points")} points on channel_id: {channel_id}")
                    return data.get("points")
                else:
                    response.raise_for_status()


    async def add_user_points(self, user: str, channel_id: str, points: int):
        """
        Add points to a user's account in a specific channel.
        
        Args:
            user (str): The username of the user.
            channel_id (str): The ID of the channel.
            points (int): The number of points to add.
        """
        async with ClientSession() as session:
            url = f"https://api.streamelements.com/kappa/v2/points/{channel_id}/{user}/{points}"
            headers = {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.jwt}"
            }
            async with session.put(url, headers=headers) as response:
                if response.status == 200:
                    print(f"Added {points} points to user {user} on channel_id: {channel_id}")
                    return await response.json()
                else:
                    response.raise_for_status()

    async def remove_user_points(self, user: str, channel_id: str, points: int):
        """
        Remove points from a user's account in a specific channel.
        
        Args:
            user (str): The username of the user.
            channel_id (str): The ID of the channel.
            points (int): The number of points to remove.
        """
        async with ClientSession() as session:
            url = f"https://api.streamelements.com/kappa/v2/points/{channel_id}/{user}/-{points}"
            headers = {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.jwt}"
            }
            async with session.delete(url, headers=headers) as response:
                if response.status == 200:
                    print(f"Removed {points} points from user {user} on channel_id: {channel_id}")
                    return await response.json()
                else:
                    response.raise_for_status()