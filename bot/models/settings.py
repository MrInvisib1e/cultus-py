from sqlalchemy import BigInteger, Column, String, Integer, Boolean
from sqlalchemy.types import Enum

from bot.models.static.setting_type import SettingType
from .base import Base


class Setting(Base):
    __tablename__ = 'Setting'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, index=True)
    user_id = Column(BigInteger, index=True)
    type = Column(Enum(SettingType))  
    description = Column(String(255)) 
    is_active = Column(Boolean, default=True)
    