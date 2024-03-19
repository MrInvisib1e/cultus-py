from aiogram import Router, types
from aiogram.filters import Command
from bot.services.database_service import DatabaseService

class TestCommand:
    
    router = Router()
    @router.message(Command(commands='test'))
    async def start(message: types.Message):
        welcome_text = 'Some test message'
        await message.reply(welcome_text)