from datetime import datetime, timedelta
import json
from sqlalchemy import case, update, func
from sqlalchemy.future import select
from bot.models.settings import Setting
from bot.models.static.setting_type import SettingType
from bot.models.static.text_type import TextType
from database import AsyncSession
from bot.models.message import Message
from bot.models.chat_user import ChatUser
from sqlalchemy.exc import NoResultFound

class DatabaseService:
    
    @staticmethod
    async def user_special_settings(user_id):
        async with AsyncSession() as session:
            async with session.begin():
                query = (select(Setting)
                    .filter(Setting.user_id == user_id))
                
                result = await session.execute(query)
                return result.scalars().all()
    
    @staticmethod
    async def get_message_by_type(message_type: TextType):
        async with AsyncSession() as session:
            async with session.begin():
                query = (select(Message)
                        .filter(Message.type==message_type,
                            Message.is_active==True)
                        .order_by(func.random()))
                
                result = await session.execute(query)
                message = result.scalars().first()
                
                if message:
                    return message.text.replace('\\n', '\n')

            return ""  
    
    @staticmethod
    async def get_all_messages_by_type(message_type: TextType) -> Message:
        async with AsyncSession() as session:
            async with session.begin():
                query = (select(Message)
                        .filter(Message.type==message_type)
                        .order_by(Message.id))
                
                result = await session.execute(query)
                messages = result.scalars().all()
                
                return messages
    
    @staticmethod
    async def get_user_by_id(user_id, chat_id):
        async with AsyncSession() as session:
            async with session.begin():
                query = (select(ChatUser)
                    .filter(
                        ChatUser.user_id == user_id, 
                        ChatUser.chat_id == chat_id))
                result  = await session.execute(query)
                return result.scalars().first()
        
    @staticmethod
    async def get_all_chats_id():
        async with AsyncSession() as session:
            async with session.begin():
                query = select(ChatUser.chat_id).distinct()
                result = await session.execute(query)
                
                return result.scalars().all()

    
    @staticmethod
    async def get_users(chat_id):
        async with AsyncSession() as session:
            async with session.begin():
                query = (select(ChatUser)
                    .filter_by(chat_id=chat_id))
                
                users = await session.execute(query)
                return users.scalars().all()
    
    @staticmethod
    async def get_all_users_with_closest_birthday(chat_id):
        async with AsyncSession() as session:
            async with session.begin():
                upcoming_birthday = case(
                    (
                        func.concat(func.year(func.current_date()), '-', func.month(ChatUser.birthday_date), '-', func.day(ChatUser.birthday_date)) > func.current_date(),
                        func.str_to_date(func.concat(func.year(func.current_date()), '-', func.month(ChatUser.birthday_date), '-', func.day(ChatUser.birthday_date)), '%Y-%m-%d')
                    ),
                    else_=func.str_to_date(func.concat(func.year(func.current_date()) + 1, '-', func.month(ChatUser.birthday_date), '-', func.day(ChatUser.birthday_date)), '%Y-%m-%d')
                ).label('upcoming_birthday')

                query = (select(ChatUser, upcoming_birthday)
                        .filter(ChatUser.birthday_date != None, ChatUser.chat_id == chat_id)
                        .order_by(upcoming_birthday))
                result = await session.execute(query)
                results = result.all()

        users_with_upcoming_birthdays = []
        for user, up_birthday in results:
            user.upcoming_birthday = up_birthday  # Set the additional attribute
            users_with_upcoming_birthdays.append(user)

        return users_with_upcoming_birthdays
    
    @staticmethod
    async def get_only_users_with_closest_birthday(chat_id):
        async with AsyncSession() as session:
            async with session.begin():
                all_users = await DatabaseService.get_all_users_with_closest_birthday(chat_id)
                if not all_users:
                    return []
        
        closest_user = all_users[0];
        range_end_date = closest_user.upcoming_birthday + timedelta(days=7)
        
        filtered_users = [
            user for user in all_users
            if closest_user.upcoming_birthday <= user.upcoming_birthday <= range_end_date
        ]

        return filtered_users
    
    # Creations Section 
    @staticmethod
    async def add_user(user):
        async with AsyncSession() as session:
            async with session.begin():
                session.add(user)
    
    # Update Section
    @staticmethod
    async def update_user(user, chat_id):
        async with AsyncSession() as session:
            async with session.begin():
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
                    result = await session.execute(stmt)
                    if result.rowcount == 0:
                        raise NoResultFound("User not found in the database.")
                except NoResultFound as e:
                    print(str(e))
            
    @staticmethod
    async def update_user_score(user, chat_id):
        async with AsyncSession() as session:
            async with session.begin():
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
                    result = await session.execute(stmt)
                    if result.rowcount == 0:
                        raise NoResultFound("User not found in the database.")
                except NoResultFound as e:
                    print(str(e))
    
    @staticmethod
    async def update_user_bday(user, chat_id):
        async with AsyncSession() as session:
            async with session.begin():
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
                    result = await session.execute(stmt)
                    if result.rowcount == 0:
                        raise NoResultFound("User not found in the database.")
                except NoResultFound as e:
                    print(str(e))
    
    @staticmethod
    async def update_message_by_id(message_id: int, message: str):
        async with AsyncSession() as session:
            async with session.begin():
                try:
                    stmt = (
                        update(Message)
                        .where(
                            Message.id == message_id)
                        .values(
                            text=message
                        )
                    )
                    result = await session.execute(stmt)
                    if result.rowcount == 0:
                        raise NoResultFound("Message not found in the database.")
                    return True
                except NoResultFound as e:
                    print(str(e))
                    
    @staticmethod
    async def change_message_status(message_id: int, is_active: bool):
        async with AsyncSession() as session:
            async with session.begin():
                try:
                    stmt = (
                        update(Message)
                        .where(
                            Message.id == message_id)
                        .values(
                            is_active=is_active
                        )
                    )
                    result = await session.execute(stmt)
                    if result.rowcount == 0:
                        raise NoResultFound("Message not found in the database.")
                    return True
                except NoResultFound as e:
                    print(str(e))
    
    # Deletion Section
    
    
    