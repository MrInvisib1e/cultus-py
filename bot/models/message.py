from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.types import Enum
from .base import Base
from .static.text_type import TextType


class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    type = Column(Enum(TextType))  
    media = Column(String(5000))  
    text = Column(String(255)) 
    is_active = Column(Boolean, default=True)