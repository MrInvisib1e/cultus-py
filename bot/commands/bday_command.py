from typing import Optional
from aiogram import Router, F
from sqlalchemy import DateTime
from bot.models.static.text_type import TextType
from bot.services.database_service import DatabaseService
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import (
    Message
)
from dateparser import *

class Form(StatesGroup):
    birth_day = State()

month_names_uk = {
    "January": "Січня", "February": "Лютого",
    "March": "Березня", "April": "Квітня",
    "May": "Травня", "June": "Червня",
    "July": "Липня", "August": "Серпня",
    "September": "Вересня", "October": "Жовтня",
    "November": "Листопада", "December": "Грудня"
}
    
class BdayCommand:
    router = Router()
    
    @router.message(F.text.startswith('культус збережи дн'))
    @router.message(Command(commands='savebday'))
    async def save_bd(message: Message, state: FSMContext):
        await state.set_state(Form.birth_day)
        text = await DatabaseService.get_message_by_type(TextType.SaveBirthday)
        await message.answer(
            text, 
            reply_to_message_id=message.message_id, 
            parse_mode='HTML')
    
    @router.message(Form.birth_day)
    async def process_bd(message: Message, state: FSMContext) -> None:
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
            user.birthday_date = birthday
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
    
    @router.message(Command(commands='deletebday'))
    async def delete_bd(message: Message) -> None:
        try:
            user = await DatabaseService.get_user_by_id(message.from_user.id, message.chat.id)
            user.birthday_date = None
            await DatabaseService.update_user_bday(user, message.chat.id)
                
        except Exception as e:
            print(e)
            text = await DatabaseService.get_message_by_type(TextType.Error)
            await message.answer(
                text,
                reply_to_message_id=message.message_id
            )
            return
        
        text = await DatabaseService.get_message_by_type(TextType.DeleteBirthday)
        await message.answer(
            text,
            reply_to_message_id=message.message_id, 
            parse_mode='HTML')
        
    @router.message(Command(commands='allbdays'))
    async def show_all_bdays(message: Message) -> None:
        users = await DatabaseService.get_all_users_with_closest_birthday(chat_id=message.chat.id)
        text = await DatabaseService.get_message_by_type(TextType.AllBirthdays)
        text += '\n\n'.join([f'{user.full_name if user.full_name != None else user.user_name} - {user.birthday_date.strftime("%d %B")}' for user in users])
        await message.answer(
            text,
            reply_to_message_id=message.message_id, 
            parse_mode='HTML')
    
    @router.message(Command(commands='closestbday'))
    async def show_closest_bday(message: Message) -> None:
        users = await DatabaseService.get_only_users_with_closest_birthday(chat_id=message.chat.id)
        if(len(users) > 1):
            text = await DatabaseService.get_message_by_type(TextType.NextBirthdayMulti) + '\n\n'
        elif(len(users) == 1):
            text = await DatabaseService.get_message_by_type(TextType.NextBirthday) + '\n\n'
        else:
            text = await DatabaseService.get_message_by_type(TextType.NoBirthdays) + '\n\n'
            
        text += ('\n'.join([f'{user.full_name if user.full_name != None else user.user_name} - {user.birthday_date.strftime("%d ")}{month_names_uk[user.birthday_date.strftime("%B")]}'for user in users]))
        
        await message.answer(
            text,
            reply_to_message_id=message.message_id, 
            parse_mode='HTML')
        
    