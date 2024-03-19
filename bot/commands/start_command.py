from aiogram import types, Router
from aiogram.filters import CommandStart
from bot.services.database_service import DatabaseService

class StartCommand:
    router = Router()
    
    @router.message(CommandStart())
    async def start(message: types.Message):
        welcome_text = 'Some start text here'
        await message.reply(welcome_text)
        

