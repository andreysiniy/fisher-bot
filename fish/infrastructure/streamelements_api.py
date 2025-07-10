
from aiohttp import ClientSession
from fish.helpers.logger import get_logger
from fish.core.interfaces.points_provider_abs import PointsProviderAbstract

logger = get_logger("streamelements_log")

class StreamElementsApi(PointsProviderAbstract):
    def __init__(self, config):
        self.config = config
        self.jwt = self.config.streamelementsJWT
        print(f"StreamElements Initialized")    

    async def get_channel_id(self, name: str) -> str:
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
                    print(f"Failed to get channel ID for {name}: {response.status}")
                    print(f"Response: {await response.text()}")
                    response.raise_for_status()

    async def get_user_points(self, user: str, channel_id: str) -> int:
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
                    print(f"User: {user} has {data.get('points')} points on channel_id: {channel_id}")
                    return data.get("points")
                else:
                    print(f"Failed to get points for user {user} on channel_id: {channel_id}: {response.status}")
                    print(f"Response: {await response.text()}")
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
                    data = await response.json()
                    logger.info(f"Added {points} to user {user} on channel_id: {channel_id}", extra={'response_data': data})
                    return data
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Failed to add points for user '{user}'. "
                        f"Request to {url} failed with status {response.status}.",
                        extra={
                            'user': user,
                            'channel_id': channel_id,
                            'status_code': response.status,
                            'response_text': error_text
                            }
                        )
                    print(f"Failed to add points to user {user} on channel_id: {channel_id}")
                    print(f"Response: {error_text}")
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
            async with session.put(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Removed {points} from user {user} on channel_id: {channel_id}", extra={'response_data': data})
                    print(f"Removed {points} points from user {user} on channel_id: {channel_id}")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Failed to add points for user '{user}'. "
                        f"Request to {url} failed with status {response.status}.",
                        extra={
                            'user': user,
                            'channel_id': channel_id,
                            'status_code': response.status,
                            'response_text': error_text
                            }
                        )
                    print(f"Failed to remove points from user {user} on channel_id: {channel_id}")
                    print(f"Response: {error_text}")
                    response.raise_for_status()
    
    async def get_user_rank(self, user: str, channel_id: str) -> int:
        """
        Retrieve the rank of a user in a specific channel.
        
        Args:
            user (str): The username of the user.
            channel_id (str): The ID of the channel.
        
        Returns:
            str: The rank of the user.
        """
        async with ClientSession() as session:
            url = f"https://api.streamelements.com/kappa/v2/points/{channel_id}/{user}/rank"
            headers = {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.jwt}"
            }
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"User {user} rank is {data.get('rank', -1)} on channel_id: {channel_id}", extra={'response_data': data})
                    print(f"User: {user} has rank: {data.get('rank')} on channel_id: {channel_id}")
                    return data.get("rank")
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Failed to add points for user '{user}'. "
                        f"Request to {url} failed with status {response.status}.",
                        extra={
                            'user': user,
                            'channel_id': channel_id,
                            'status_code': response.status,
                            'response_text': error_text
                            }
                        )
                    print(f"Failed to get rank for user {user} on channel_id: {channel_id}: {response.status}")
                    print(f"Response: {error_text}")
                    response.raise_for_status()
    
    async def get_username_by_rank(self, rank: int, channel_id: str) -> str:
        """
        Retrieve the user with a specific rank in a specific channel.
        
        Args:
            rank (int): The rank of the user.
            channel_id (str): The ID of the channel.
        
        Returns:
            str: The username of the user.
        """
        async with ClientSession() as session:
            url = f"https://api.streamelements.com/kappa/v2/points/{channel_id}/top?limit=1&offset={rank - 1}"
            headers = {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.jwt}"
            }
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if "users" in data and len(data["users"]) > 0:
                        username = data["users"][0].get("username")
                        print(f"User with rank {rank} on channel_id: {channel_id} is {username}")
                        logger.info(f"User with rank {rank} on channel {channel_id} is '{username}'.")
                        return username
                    else:
                        print(f"No user found for rank {rank} on channel_id: {channel_id}")
                        logger.warning(f"No user found for rank {rank} on channel {channel_id}. The rank may be out of bounds.")
                        return ""
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Failed to get user by rank. API returned status {response.status}.",
                        extra={
                            'rank': rank,
                            'channel_id': channel_id,
                            'status_code': response.status,
                            'response_text': error_text
                        }
                    )
                    print(f"Failed to get user by rank {rank} on channel_id: {channel_id}: {response.status}")
                    print(f"Response: {error_text}")
                    response.raise_for_status()