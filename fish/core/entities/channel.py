from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy.orm import relationship

from fish.core.entities.base import Base

class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    
    name = Column(String, unique=True, nullable=False, index=True)
    twitch_id = Column(String, unique=True, nullable=False, index=True)
    se_id = Column(String, unique=True, nullable=False, index=True)
    
    player_profiles = relationship("PlayerProfile", back_populates="channel", cascade="all, delete-orphan")