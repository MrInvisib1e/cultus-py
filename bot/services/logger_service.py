import asyncio
import logging
from aiogram import Bot
            
log_queue = asyncio.Queue()

class AsyncTelegramLoggingHandler(logging.Handler):
    def __init__(self, bot: Bot, chat_id: int):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        try:
            asyncio.run_coroutine_threadsafe(log_queue.put(record.getMessage()), asyncio.get_event_loop())
        except Exception:
            self.handleError(record)

async def send_logs(bot, group_id):
    while True:
        log_message = await log_queue.get()
        try:
            await bot.send_message(chat_id=group_id, text=log_message)
        except Exception as e:
            print(f"Failed to send log message: {e}")