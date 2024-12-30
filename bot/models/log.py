from sqlalchemy import BigInteger, Column, Integer, String
from .base import Base

class Log(Base):
    __tablename__ = 'user_log' 

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True, index=True)
    user_name = Column(String(255), nullable=True) 
    full_name = Column(String(255), nullable=True)
    chat_id = Column(BigInteger, index=True)
    log_message = Column(String(5000))