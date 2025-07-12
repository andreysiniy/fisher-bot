from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from fish.core.entities.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    twitch_id = Column(String, unique=True, nullable=False, index=True)
    twitch_name = Column(String, nullable=False)

    player_profiles = relationship("PlayerProfile", back_populates="user", cascade="all, delete-orphan")

class PlayerProfile(Base):
    __tablename__ = 'player_profiles'

    id = Column(Integer, primary_key=True)
    cooldown_expiration = Column(Float, default=0.0, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    channel_id = Column(Integer, ForeignKey('channels.id'), nullable=False)

    user = relationship("User", back_populates="player_profiles")
    channel = relationship("Channel", back_populates="player_profiles")
    
    se_stats = relationship("SE_Stats", back_populates="profile", uselist=False, cascade="all, delete-orphan")
    fish_stats = relationship("FishCatchStats", back_populates="profile", cascade="all, delete-orphan")
    unlocked_rewards = relationship("UnlockedReward", back_populates="profile", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint('user_id', 'channel_id', name='_user_channel_uc'),)