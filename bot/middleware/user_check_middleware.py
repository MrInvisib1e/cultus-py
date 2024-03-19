# from aiogram import BaseMiddleware, types

# from bot.models.chat_user import ChatUser
# from bot.services.database_service import DatabaseService

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.models.chat_user import ChatUser
from bot.services.database_service import DatabaseService


class UserCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ):
        try:
            user = await DatabaseService.get_user_by_id(message.from_user.id, message.chat.id)
        except Exception as e:
            user = None
            
        if(user is None):
            user = ChatUser();
            user.user_id=message.from_user.id, 
            user.user_name=message.from_user.username, 
            user.user_full_name=message.from_user.full_name,
            user.register_date = message.date,
            user.last_message_date = message.date,
            user.messages_count=1,
            user.chat_id=message.chat.id
            await DatabaseService.add_user(user)
        else:
            user.full_name = message.from_user.full_name
            user.last_message_date = message.date
            user.messages_count += 1
            user.user_name = message.from_user.username
            await DatabaseService.update_user(user, message.chat.id)
        return await handler(message, data)