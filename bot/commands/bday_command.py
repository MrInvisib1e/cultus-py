from typing import Optional
from aiogram import Router
from magic_filter import F
from sqlalchemy import DateTime
from bot.models.chat_user import ChatUser
from bot.models.static.text_type import TextType
from bot.services.database_service import DatabaseService
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import (
    Message
)
from dateutil.parser import *

class Form(StatesGroup):
    birth_day = State()
    
    
class BdayCommand:
    router = Router()

    @router.message(F.text.startswith('культус збережи дн'))
    @router.message(Command(commands='savebday'))
    async def start(message: Message, state: FSMContext):
        await state.set_state(Form.birth_day)
        text = await DatabaseService.get_message_by_type(TextType.SaveBirthday)
        await message.answer(
            text, 
            reply_to_message_id=message.message_id, 
            parse_mode='HTML')
    
    @router.message(Form.birth_day)
    async def process_name(message: Message, state: FSMContext) -> None:
        await state.clear()
        birthday: Optional[DateTime] = None
        
        try:
            birthday = parse(message.text)
        except: 
            pass
        
        if(birthday is None):
            text = await DatabaseService.get_message_by_type(TextType.SaveBirthdayError)
            await message.answer(
                text, 
                reply_to_message_id=message.message_id,
                parse_mode='HTML')
            return
        
        try:
            user = await DatabaseService.get_user_by_id(message.from_user.id, message.chat.id)
            user.birthday = birthday
            await DatabaseService.update_user_bday(user, message.chat.id)
                
        except Exception as e:
            print(e)
            text = await DatabaseService.get_message_by_type(TextType.Error)
            await message.answer(
                text,
                reply_to_message_id=message.message_id
            )
            return
        
        text = await DatabaseService.get_message_by_type(TextType.SavedBirthday)
        await message.answer(
            text,
            reply_to_message_id=message.message_id, 
            parse_mode='HTML')
