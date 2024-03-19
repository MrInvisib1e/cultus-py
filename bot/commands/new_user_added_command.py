from aiogram import types, Router, enums
from magic_filter import F

class NewUserAddedCommand:
    router = Router()
    
    @router.message(F.content_type == enums.content_type.ContentType.NEW_CHAT_MEMBERS)
    async def start(message: types.Message):
        welcome_text = 'Some start text here'
        await message.reply(welcome_text)