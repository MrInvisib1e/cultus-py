from aiogram import Router, types, F
from aiogram.filters import Command
from bot.models.static.text_type import TextType
from bot.services.database_service import DatabaseService

class ProphecyCommand:
    
    router = Router()
    
    @router.message(F.text.startswith('культус скажи'))
    @router.message(F.text.startswith('культус, скажи'))
    @router.message(F.text.startswith('Культус скажи'))
    @router.message(F.text.startswith('Культус, скажи'))
    @router.message(Command(commands='prophecy'))
    async def get_prophecy(message: types.Message):
        text = await DatabaseService.get_message_by_type(TextType.Prophecy)
        await message.answer(
            text, 
            reply_to_message_id=message.message_id, 
            parse_mode='HTML')
    
