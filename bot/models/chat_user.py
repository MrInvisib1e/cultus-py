from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from datetime import datetime
from .base import Base

class ChatUser(Base):
    __tablename__ = 'chat_users' 

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True, index=True)
    user_name = Column(String(255), nullable=True) 
    full_name = Column(String(255), nullable=True)
    personal_score = Column(Integer, default=0)
    chat_id = Column(BigInteger, index=True)
    register_date = Column(DateTime, default=datetime.now)
    birthday_date = Column(DateTime, nullable=True)
    house_type = Column(Integer, default=0)
    house_reroll = Column(Integer, default=0)
    messages_count = Column(BigInteger, default=0)
    last_message_date = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    
