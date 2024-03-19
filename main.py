import asyncio
import logging
from aiogram import Bot, Dispatcher, Router
from bot.commands.bday_command import BdayCommand
from bot.commands.start_command import StartCommand
from bot.commands.test_command import TestCommand
from bot.middleware.user_check_middleware import UserCheckMiddleware
from config import LOG_FILE, API_TOKEN
# from init_db import init_db

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

middleware_router = Router()
middleware_router.message.outer_middleware(UserCheckMiddleware())

# Register handlers
dp.include_router(middleware_router)
dp.include_router(StartCommand.router)
dp.include_router(TestCommand.router)
dp.include_router(BdayCommand.router)

async def main() -> None:
    # init_db() 
    print("-------------Bot started-------------")
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())