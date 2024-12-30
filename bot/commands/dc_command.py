from aiogram import Router, types
from aiogram.filters import Command
from bot.models.static.text_type import TextType
from bot.services.database_service import DatabaseService
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class Form(StatesGroup):
    draco = State()
    
class DracoCommand:
    
    router = Router()
    
    @router.message(Command(commands='dc'))
    async def calc_dc(message: types.Message, state: FSMContext):
        args = message.text.split()[1:] 
        if not args: 
            await DracoCommand.prompt_for_number(message, state)
            return
         
        arg = ' '.join(args)
        try:
            parsed_number = int(arg)
            await DracoCommand.process_calc(message, parsed_number, state)
        except ValueError:
            await DracoCommand.prompt_for_number(message, state)
    
    async def prompt_for_number(message: types.Message, state: FSMContext):
        """Sets the state to Form.draco and prompts the user for a number."""
        await state.set_state(Form.draco)
        text = await DatabaseService.get_message_by_type(TextType.DracoWait)
        await message.answer(
            text, 
            reply_to_message_id=message.message_id, 
            parse_mode='HTML')
        
    @router.message(Form.draco)
    async def process_dc(message: types.Message, state: FSMContext) -> None:
        try:
            await state.clear()
            parsed_number = int(message.text)
            await DracoCommand.process_calc(message, parsed_number, state)
        except ValueError:
            text = await DatabaseService.get_message_by_type(TextType.DracoError)
            await message.answer(text, reply_to_message_id=message.message_id)
        
    async def process_calc(message: types.Message, number: int, state: FSMContext):
        await state.clear()
        text = await DatabaseService.get_message_by_type(TextType.DracoCalc)
        if(number == 1):
            text += f"\n<b>{number/150:.2f}</b> Дракочлен"
        else:
            text += f"\n<b>{number/150:.2f}</b> Дракочлена"

        await message.answer(
            text,
            reply_to_message_id=message.message_id,
            parse_mode='HTML')