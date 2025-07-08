from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from fish.core.entities.base import Base

class SE_Stats(Base):
    __tablename__ = 'se_stats'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('player_profiles.id'), unique=True, nullable=False)
    
    gained_points = Column(Integer, default=0, nullable=False)
    biggest_fish_income = Column(Integer, default=0, nullable=False)
    fishing_income = Column(Integer, default=0, nullable=False)
    lost_points = Column(Integer, default=0, nullable=False)
    biggest_fish_loss = Column(Integer, default=0, nullable=False)
    points = Column(Integer, default=0, nullable=False)

    profile = relationship("PlayerProfile", back_populates="se_stats")

class FishCatchStats(Base):
    __tablename__ = 'fish_catch_stats'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('player_profiles.id'), nullable=False)
    
    reward_type = Column(String, nullable=False)  
    count = Column(Integer, default=0, nullable=False)

    profile = relationship("PlayerProfile", back_populates="fish_stats")
    
    __table_args__ = (UniqueConstraint('profile_id', 'reward_type', name='_profile_reward_type_uc'),)


class UnlockedReward(Base):
    __tablename__ = 'unlocked_rewards'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('player_profiles.id'), nullable=False)
    
    reward_id = Column(String, nullable=False, index=True)

    profile = relationship("PlayerProfile", back_populates="unlocked_rewards")

    __table_args__ = (UniqueConstraint('profile_id', 'reward_id', name='_profile_reward_id_uc'),)