from datetime import date 
import os 
import aiocron
from aiogram import Bot
import pytz
from bot.models.static.text_type import TextType
from bot.services.database_service import DatabaseService

log_group = os.getenv('LOG_GROUP_ID')

async def send_reminder(bot: Bot):
    """
    The job that will be scheduled: checks for birthdays today and sends a message to a specific chat.
    """
    
    try:
        today = date.today().strftime("%d-%m")
        chat_ids = await DatabaseService.get_all_chats_id()
        
        for chat_id in chat_ids:  
            birthdays_today = [
                user for user in await DatabaseService.get_users(chat_id) 
                if user.birthday_date is not None and user.birthday_date.strftime("%d-%m") == today
            ]
            if birthdays_today:
                text = await DatabaseService.get_message_by_type(TextType.BirthdayToday) + '\n\n'
                users_link = [f"<a href='tg://user?id={user.id}'>{user.full_name if user.full_name != None else user.user_name}</a>" for user in birthdays_today]
                text += '\n'.join(users_link)

                await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='HTML')
            else:
                pass  

    except Exception as e:
        await bot.send_message(chat_id=log_group, text=f"An error occurred: {e}")
        
timezone = pytz.timezone("Europe/Kiev") 

def init_bd_scheduler(bot: Bot):
    """
    Initializes the birthday scheduler.
    This function sets up an aiocron job.
    """
    
    @aiocron.crontab('34 09 * * *', tz=timezone) 
    async def cronjob():
        await send_reminder(bot)
