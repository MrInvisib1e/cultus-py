import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router
from bot.commands.admin_command import AdminCommand
from bot.commands.bday_command import BdayCommand
from bot.commands.duel_command import DuelCommand
from bot.commands.prophecy_command import ProphecyCommand
from bot.commands.start_command import StartCommand
from bot.commands.dc_command import DracoCommand
from bot.commands.user_interaction_command import UserInteractionCommand
from bot.services.logger_service import AsyncTelegramLoggingHandler, send_logs
from bot.middleware.user_check_middleware import UserCheckMiddleware
from bot.tasks.bd_reminder import init_bd_scheduler
from dotenv import load_dotenv

load_dotenv()

log_file = os.getenv('LOG_FILE')
api_token = os.getenv('API_TOKEN')
log_group = os.getenv('LOG_GROUP_ID')

logging.basicConfig(filename=log_file, level=logging.INFO)

bot = Bot(token=api_token)
dp = Dispatcher()

telegram_handler = AsyncTelegramLoggingHandler(bot, log_group)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
telegram_handler.setFormatter(formatter)
telegram_handler.setLevel(logging.ERROR)
logging.getLogger('').addHandler(telegram_handler)

middleware_router = Router()
middleware_router.message.outer_middleware(UserCheckMiddleware())

# Register handlers
dp.include_router(middleware_router)
# dp.include_router(StartCommand.router)
dp.include_router(ProphecyCommand.router)
dp.include_router(UserInteractionCommand.router)
dp.include_router(BdayCommand.router)
dp.include_router(DracoCommand.router)
dp.include_router(AdminCommand.router)
dp.include_router(DuelCommand.router)

async def main() -> None:
    print("-------------Bot started-------------")
    log_task = asyncio.create_task(send_logs(bot, log_group))
    
    init_bd_scheduler(bot)
    
    try:
        await dp.start_polling(bot)
    finally:    
        log_task.cancel()
        await log_task

if __name__ == '__main__':
    asyncio.run(main())