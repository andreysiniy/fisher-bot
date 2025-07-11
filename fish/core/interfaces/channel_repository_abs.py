from abc import ABC, abstractmethod
from typing import Protocol
from ..entities import Channel

class ChannelRepositoryAbstract(Protocol):
    @abstractmethod
    async def get_channel(self, channel_id: str) -> Channel:
        pass

    @abstractmethod
    async def create_channel(self, channel: Channel) -> Channel:
        pass

    @abstractmethod
    async def update_channel(self, channel: Channel) -> Channel:
        pass

    @abstractmethod
    async def delete_channel(self, channel_id: str) -> None:
        pass
