from sqlalchemy import delete, update, func
from bot.models.static.text_type import TextType
from database import Session
from bot.models.message import Message
from bot.models.chat_user import ChatUser
from sqlalchemy.exc import NoResultFound

class DatabaseService:
    
    @staticmethod
    async def get_message_by_type(message_type: TextType):
        session = Session()
        message = (session
                .query(Message)
                .filter(Message.type==message_type,
                    Message.is_active==True)
                .order_by(func.random())
                .first())
        
        session.close()
        return message.text if message else ''
    
    @staticmethod
    async def get_user_by_id(user_id, chat_id):
        session = Session()
        user = (session
            .query(ChatUser)
            .filter(
                ChatUser.user_id == user_id, 
                ChatUser.chat_id == chat_id)
            .first())
        
        session.close()
        return user
        
    @staticmethod
    async def get_users(chat_id):
        session = Session()
        users = (session
            .query(ChatUser)
            .filter_by(chat_id=chat_id)
            .all())
        session.close()
        return users
    
    @staticmethod
    async def get_users_with_closest_birthday(self, chat_id):
        session = Session()
        users = (session.query(ChatUser)
            .filter(
                ChatUser.chat_id == chat_id, 
                ChatUser.birthday_date != None)
            .order_by(ChatUser.birthday_date)
            .all())
        
        session.close()
        return users
    
    # Creations Section 
    @staticmethod
    async def add_user(user):
        session = Session()
        session.add(user)
        session.commit()
        session.close()
    
    # Update Section
    @staticmethod
    async def update_user(user, chat_id):
        session = Session()
        try:
            stmt = (
                update(ChatUser)
                .where(
                    ChatUser.user_id == user.user_id,
                    ChatUser.chat_id == chat_id)
                .values(
                    full_name=user.full_name,
                    last_message_date=user.last_message_date,
                    messages_count=user.messages_count,
                    user_name=user.user_name,
                    birthday_date=user.birthday_date,
                    personal_score=user.personal_score,
                    house_type=user.house_type,
                    house_reroll=user.house_reroll
                )
            )
            result = session.execute(stmt)
            if result.rowcount == 0:
                raise NoResultFound("User not found in the database.")
            session.commit()
        except NoResultFound as e:
            print(str(e))
        finally:
            session.close()
            
    @staticmethod
    async def update_user_score(user, chat_id):
        session = Session()
        try:
            stmt = (
                update(ChatUser)
                .where(
                    ChatUser.user_id == user.user_id,
                    ChatUser.chat_id == chat_id)
                .values(
                    personal_score=user.personal_score
                )
            )
            result = session.execute(stmt)
            if result.rowcount == 0:
                raise NoResultFound("User not found in the database.")
            session.commit()
        except NoResultFound as e:
            print(str(e))
        finally:
            session.close()
    
    @staticmethod
    async def update_user_bday(user, chat_id):
        session = Session()
        try:
            stmt = (
                update(ChatUser)
                .where(
                    ChatUser.user_id == user.user_id,
                    ChatUser.chat_id == chat_id)
                .values(
                    birthday_date=user.birthday_date
                )
            )
            result = session.execute(stmt)
            if result.rowcount == 0:
                raise NoResultFound("User not found in the database.")
            session.commit()
        except NoResultFound as e:
            print(str(e))
        finally:
            session.close()
    
    # Deletion Section
    
    
    