import os
from aiogram import Router, types, F
from aiogram.filters import Command
from bot.models.static.setting_type import SettingType
from bot.models.static.text_type import TextType
from bot.services.database_service import DatabaseService
from aiogram.fsm.state import State, StatesGroup

vidlunya_id = os.getenv('VIDLUNYA_ID')

class Form(StatesGroup):
    messageType = State()
    
    
class AdminCommand:
    
    router = Router()
    
    @router.message(Command(commands='admin_help'))
    async def get_admin_help(message: types.Message):
        user_id = message.from_user.id
        if await AdminCommand.user_have_role(user_id, "GroupAdmin"):
            text = "Ти маєш доступ до таких команд, як адмін(-ка):\n\n"
            text += "/admin_help - команди\n"
            text += "/users_stat - статистика користувачів\n"
            text += "/set_msg_count [user_id] [count] - встановити кількість повідомлень користувачу\n"
            
            await message.answer(text, reply_to_message_id=message.message_id, parse_mode='HTML')
    
    @router.message(Command(commands='users_stat'))
    async def get_main_group_users(message: types.Message):
        user_id = message.from_user.id
        chat_id = vidlunya_id

        if await AdminCommand.user_have_role(user_id, "GroupAdmin"):
            users = await DatabaseService.get_users(chat_id) 
            if users:
                text = "<b>Статистика користувачів</b>\n\n"
                for user in users:
                    text += f'ID: {user.user_id}, Name: {user.full_name if user.full_name != None else user.user_name}, Messages: {user.messages_count}, `LM time: { user.last_message_date.strftime("%d %m %Y %H:%M") }`\n'
                await message.answer(text, reply_to_message_id=message.message_id, parse_mode='HTML')
            else:
                await message.answer("Немає користувачів.", reply_to_message_id=message.message_id, parse_mode='HTML')

    @router.message(Command(commands='set_msg_count'))
    async def set_user_messages(message: types.Message):
        user_id = message.from_user.id
        chat_id = vidlunya_id
        args = message.text.split()[1:]
        if await AdminCommand.user_have_role(user_id, "GroupAdmin"):
            if args and len(args) == 2: 
                user = await DatabaseService.get_user_by_id(args[0], chat_id)
                user.messages_count = args[1];
                await DatabaseService.update_user(user, chat_id)
                await message.answer("Збережено.", reply_to_message_id=message.message_id, parse_mode='HTML')
            else:
                await message.answer("Не правильний формат. Потрібно /set_msg_count [user_id] [count]", reply_to_message_id=message.message_id, parse_mode='HTML')
    
    @router.message(Command(commands='show_msg_types'))
    async def show_types(message: types.Message):
        user_id = message.from_user.id
        if await AdminCommand.user_have_role(user_id, "GroupAdmin"):
            text = "Зараз зареєстровано такі типи: \n\n"
            text += "\n".join([f"{type_.name}" for type_ in TextType])
            await message.answer(text, reply_to_message_id=message.message_id, parse_mode='HTML')
            
    @router.message(Command(commands='show_msgs'))
    async def show_messages(message: types.Message):
        user_id = message.from_user.id
        args = message.text.split()[1:]
        if await AdminCommand.user_have_role(user_id, "GroupAdmin"):
            if args and len(args) == 1: 
                messages = await DatabaseService.get_all_messages_by_type(args[0])
                text = f"Зараз зареєстровано такі повідомлення для {args[0]}:\n\n"
                for msg in messages:
                    text += f"{msg.id} - {msg.text} - {"active" if msg.is_active else "inactive"};\n"
                await message.answer(text, reply_to_message_id=message.message_id, parse_mode='HTML')
            else:
                await message.answer("Не правильний формат. Потрібно /show_messages [MessageType]", reply_to_message_id=message.message_id, parse_mode='HTML')
    
    @router.message(Command(commands='edit_msg'))
    async def edit_messages(message: types.Message):
        user_id = message.from_user.id
        args = message.text.split(maxsplit=2)[1:]
        if await AdminCommand.user_have_role(user_id, "GroupAdmin"):
            if len(args) >= 2:
                message_id = args[0]
                new_message_content = args[1]
                update_successful = await DatabaseService.update_message_by_id(message_id, new_message_content)
                if(update_successful):
                    await message.answer("Оновлено.", reply_to_message_id=message.message_id, parse_mode='HTML')
            else:
                await message.answer("Не правильний формат. Потрібно /edit_msg [message_id] [Message]", reply_to_message_id=message.message_id, parse_mode='HTML')
    
    @router.message(Command(commands='change_msg_status'))
    async def edit_messages(message: types.Message):
        user_id = message.from_user.id
        args = message.text.split()[1:]
        if await AdminCommand.user_have_role(user_id, "GroupAdmin"):
            if len(args) == 2:
                message_id = args[0]
                new_status = args[1] == '1'
                
                update_successful = await DatabaseService.change_message_status(message_id,  new_status)
                if(update_successful):
                    await message.answer("Оновлено.", reply_to_message_id=message.message_id, parse_mode='HTML')
            else:
                await message.answer("Не правильний формат. Потрібно /change_msg_status [message_id] [status]", reply_to_message_id=message.message_id, parse_mode='HTML')
    
    async def user_have_role(user_id: int, role: str) -> bool:
        settings = await DatabaseService.user_special_settings(user_id)
        if not settings:
            return False

        try:
            role_to_check = SettingType[role]
            lowest_role = min(setting.type for setting in settings)
            
            return lowest_role <= role_to_check
        except KeyError:
            return False
        