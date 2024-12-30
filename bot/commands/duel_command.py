import asyncio
import random
from aiogram import F, Router, types
from aiogram.types import CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

active_duels = {}
buttons = [
    {"text": "Конфундус", "answer": "conf"},
    {"text": "Протеґо", "answer": "prot"},
    {"text": "Бомбарда", "answer": "bomb"},
    {"text": "Імпедімента", "answer": "impe"},
    {"text": "Фліпендо", "answer": "flip"}
]

class DuelAction(CallbackData, prefix="duel"):
    event: str
    answer: str
    first_user: int
    second_user: int

class DuelCommand:
    router = Router()
    
    @router.message(Command(commands='duel'))
    async def duel(message: types.Message):
        builder = InlineKeyboardBuilder()
        user_id = message.reply_to_message.from_user.id if message.reply_to_message else None
        chat_id = message.chat.id
        
        if active_duels.get(chat_id):
            await message.answer("На жаль у нас лише один помост для дуелей. \nПочекайте трохи.")
            return
        
        if not user_id:
            await message.answer("Щоб розпочати дуель, виберіть суперника, відповівши на його повідомлення з командою.")
            return
        
        if user_id == message.from_user.id:
            await message.answer("Ви не можете викликати себе на дуель.")
            return
        
        if message.from_user.is_bot:
            await message.answer("Ви не можете битись з големами.")
            return
        
        active_duels[chat_id] = {
            "status": 0,
            "oponent1": {
                "id": user_id,
                "name": message.reply_to_message.from_user.full_name,
                "action": None,
                "text": ''
            },
            "oponent2": {
                "id": message.from_user.id,
                "name": message.from_user.full_name,
                "action": None,
                "text": ''
            }
        }
        
        builder.button(
            text='Відмовляюсь', 
            callback_data=DuelAction(
                event='duel_starting', 
                answer='no', 
                first_user=user_id, 
                second_user=message.from_user.id 
            ))
        builder.button(
            text='Приймаю', 
            callback_data=DuelAction(
                event="duel_starting", 
                answer="yes", 
                first_user=user_id, 
                second_user=message.from_user.id 
            ))
        builder.adjust(1) 
        
        msg = await message.answer("Почати дуель? 30 секунд щоб підтвердити!!", reply_markup=builder.as_markup())
        await DuelCommand.duel_timeout(msg)
            
    @router.callback_query(DuelAction.filter(F.event == 'duel_starting'))
    async def handle_duel_start(callback_query: CallbackQuery):
        data = callback_query.data.split(':')
        if len(data) != 5:
            await callback_query.answer("Неправильний формат даних.")
            return
        
        _, action, answ, user_id, init_user_id = data
        chat_id = callback_query.message.chat.id
        active_duels[chat_id]["status"] = 10
        
        if int(user_id) != callback_query.from_user.id:
            await callback_query.answer("Будь ласка, не втручайтесь у дуель!")
            return
        
        if answ == "no":
            del active_duels[chat_id]
            await callback_query.message.delete()
            await callback_query.message.answer("Дуель відмінено.")
            return
        
        if answ == "yes":
            builder = InlineKeyboardBuilder()

            random.shuffle(buttons)
    
            for button in buttons:
                builder.button(
                    text=button["text"], 
                    callback_data=DuelAction(
                        event="duel_process", 
                        answer=button["answer"], 
                        first_user=user_id, 
                        second_user=init_user_id 
                    )
                )
                
            builder.adjust(1)
            
            await callback_query.message.delete()
            msg = await callback_query.message.answer("Леді та джентельмени, Відьми та Чаклуни, починаємо дуель!\n\nДуелянти, зробіть свій вибір!", reply_markup=builder.as_markup())
            await DuelCommand.duel_timeout(msg, 60)
            
    @router.callback_query(DuelAction.filter(F.event == 'duel_process'))
    async def handle_duel_process(callback_query: CallbackQuery):
        data = callback_query.data.split(':')
        if len(data) != 5:
            await callback_query.answer("Неправильний формат даних.")
            return
        
        _, action, answ, first_user_id, second_user_id = data
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id

        if int(first_user_id) != user_id and int(second_user_id) != user_id:
            await callback_query.answer("Будь ласка, не втручайтесь у дуель!")
            return
        
        if chat_id not in active_duels:
            await callback_query.message.delete()
            await callback_query.answer("Дуель було відмінено.")
            return
        
        active_duels[chat_id]["status"] = 20
        duel = active_duels[chat_id]
        if duel["oponent1"]["id"] == callback_query.from_user.id:
            duel["oponent1"]["action"] = answ
            duel["oponent1"]["text"] = next(button["text"] for button in buttons if button["answer"] == answ)
        elif duel["oponent2"]["id"] == callback_query.from_user.id:
            duel["oponent2"]["action"] = answ
            duel["oponent2"]["text"] = next(button["text"] for button in buttons if button["answer"] == answ)
        
        if duel["oponent1"]["action"] is not None and duel["oponent2"]["action"] is not None:
            winner = await DuelCommand.calculate_winner(chat_id)
            action1_text = duel["oponent1"]["text"]
            action2_text = duel["oponent2"]["text"]
            name_one = duel['oponent1']['name']
            name_two = duel['oponent2']['name']
            
            del active_duels[chat_id]
            
            await callback_query.message.delete()
            await callback_query.message.answer(f"Дуель завершено! \n{name_one} використовує {action1_text}\n {name_two} використовує {action2_text}. \n\nЗ піднятою рукою у нас: {winner}")
            
    @staticmethod
    async def calculate_winner(chat_id):
        duel = active_duels[chat_id]
        oponent1_action = duel["oponent1"]["action"]
        oponent2_action = duel["oponent2"]["action"]
        oponent1_name = duel["oponent1"]["name"]
        oponent2_name = duel["oponent2"]["name"]

        # Determine the winner based on the game rules
        if oponent1_action == oponent2_action:
            return "Нічия!"
        elif (oponent1_action == "conf" and (oponent2_action == "prot" or oponent2_action == "impe")) or \
             (oponent1_action == "prot" and (oponent2_action == "bomb" or oponent2_action == "flip")) or \
             (oponent1_action == "bomb" and (oponent2_action == "conf" or oponent2_action == "impe")) or \
             (oponent1_action == "impe" and (oponent2_action == "prot" or oponent2_action == "flip")) or \
             (oponent1_action == "flip" and (oponent2_action == "bomb" or oponent2_action == "conf")):
            return f"{oponent1_name}!"
        else:
            return f"{oponent2_name}!"

    @staticmethod
    async def cleanup_duel(chat_id):
        if chat_id in active_duels:
            del active_duels[chat_id]
            
    @staticmethod
    async def duel_timeout(message, timeout=30):
        old_status = active_duels[message.chat.id]["status"]
        await asyncio.sleep(timeout)
        chat_id = message.chat.id
        if(await DuelCommand.check_status(chat_id, old_status)):
            return
        
        await DuelCommand.cleanup_duel(chat_id)
        await message.delete()
        await message.answer("Час на очікування вичерпано. Дуель було відмінено.")
        return


    @staticmethod
    async def check_status(chat_id, old_status):
        if chat_id not in active_duels or active_duels[chat_id]["status"] > old_status:
            return True
        return False