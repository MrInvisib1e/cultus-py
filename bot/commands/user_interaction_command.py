import json
import os
import random
from aiogram import types, Router, enums, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import aiohttp

from collections import defaultdict
from bot.models import Book, BookUser, BookRating, BookSize, BookStatus, BookPair, BookTag
from bot.models.static.text_type import TextType
from bot.services.database_service import DatabaseService
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

ovell_url = os.getenv('OVELL_URL')
ovell_api = os.getenv('OVELL_FF_API')
 
user_scores = defaultdict(lambda: {'Gryffindor': 0, 'Hufflepuff': 0, 'Ravenclaw': 0, 'Slytherin': 0})
user_status = {}

with open('questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)
   
class QuizAction(CallbackData, prefix="quiz"):
    event: str
    user_id: int
    question_index: int
    house: str
    
class UserInteractionCommand:
    router = Router()
    
    @router.message(F.content_type == enums.content_type.ContentType.NEW_CHAT_MEMBERS)
    async def user_join(message: types.Message):
        text = await DatabaseService.get_message_by_type(TextType.JoinCongratulation)
        await message.reply(text, parse_mode='HTML')
    
    @router.message(Command(commands='rules'))
    async def show_rules(message: Message):
        text = await DatabaseService.get_message_by_type(TextType.Rules)
        await message.answer(text, parse_mode='HTML')
        
    @router.message(Command(commands='get'))
    async def get_me(message: Message):
        photo = message.reply_to_message.photo;
        video = message.reply_to_message.video;
        files = message.reply_to_message.document;
        
        text = "Переслав в особисті."
        if(photo):
            try:
                await message.bot.send_photo(message.from_user.id, photo[-1].file_id)
            except Exception:
                text = "Не вдалося відправити фото. Спробуй спершу почати зі мною розмову."
        elif(video):
            try:
                await message.bot.send_video(message.from_user.id, video.file_id)
            except Exception:
                text = "Не вдалося відправити відео. Спробуй спершу почати зі мною розмову."
        elif(files):
            try:
                await message.bot.send_document(message.from_user.id, files.file_id)
            except Exception:
                text = "Не вдалося відправити файл. Спробуй спершу почати зі мною розмову."
        else:
            text = "Я дозволяю отримати лише файли, картинки та відео."
            
        await message.answer(text, reply_to_message_id=message.message_id, parse_mode='HTML')
        
    @router.message(Command(commands='v'))
    async def get_version(message: Message):
        await message.answer("1.04", reply_to_message_id=message.message_id, parse_mode='HTML')
        
    @router.message(Command(commands='ff'))
    async def get_fanfic(message: Message):
        json_data = {
            "Id": "4d298a95-60ac-46b5-5b95-08db780cfc13"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(ovell_api, json=json_data) as response:
                if response.status == 200:
                    json_result = await response.json()
                    book = parse_book(json_result)
                    if book:
                        await send_book(message, book)
                else:
                    raise aiohttp.ClientResponseError(response.status, message="Не вдалося отримати дані фанфіку.")

    @router.message(Command(commands='quiz'))
    async def house_test(message: Message):
        user_id = message.from_user.id

        if user_id in user_scores:
            del user_scores[user_id]
            del user_status[user_id]

        user_scores[user_id] = {'Gryffindor': 0, 'Hufflepuff': 0, 'Ravenclaw': 0, 'Slytherin': 0}
        user_status[user_id] = { 'first_name': message.from_user.first_name }
        
        await message.answer(f"Ласкаво просимо на тест на визначення гуртожитку Гоґвортсу, {message.from_user.first_name}! Давайте побачимо, куди ви належите...")
        await ask_question(message, user_id, 0)

    @router.callback_query(QuizAction.filter(F.event == 'answer'))
    async def process_answer(callback_query: types.CallbackQuery, callback_data: QuizAction):
        user_id = callback_data.user_id
        question_index = callback_data.question_index
        house = callback_data.house
    
        if callback_query.from_user.id != user_id:
            await callback_query.answer("Це не ваш тест!", show_alert=True)
            return
    
        user_scores[user_id][house] += 1
    
        await ask_question(callback_query.message, user_id, question_index + 1)

async def ask_question(message: Message, user_id: int, question_index: int):
    user_first_name = user_status[user_id]['first_name']
    
    if question_index < len(questions):
        question_data = questions[question_index]
        question_text = question_data['question']
        options = question_data['options']
        
        current_question_number = question_index + 1
        total_questions = len(questions)
        
        shuffled_options = list(options.items())
        random.shuffle(shuffled_options)

        builder = InlineKeyboardBuilder()
        
        option_texts = []
        for option, house in shuffled_options:
            builder.button(
                text=option,
                callback_data=QuizAction(
                    event="answer",
                    user_id=user_id,
                    question_index=question_index,
                    house=house
            ))
            option_texts.append(option)
            
        builder.adjust(1);
        
        options_display = "\n".join(f"{index + 1}. {option}" for index, option in enumerate(option_texts));
        if question_index == 0:
           await message.answer(
               f"Квіз для <b>{user_first_name}</b> ({current_question_number}/{total_questions}):\n\n"
               f"<b>{question_text}</b>\n"
               f"{options_display}\n",
               reply_markup=builder.as_markup(),
               parse_mode="HTML"
           )
        else:
            await message.edit_text(
                f"Квіз для <b>{user_first_name}</b> ({current_question_number}/{total_questions}):\n\n"
                f"<b>{question_text}</b>\n"
                f"{options_display}\n",
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
    else:
        await finalize_quiz(message, user_id, user_first_name)

async def finalize_quiz(message: Message, user_id: int, username: str):
    await message.delete()
    scores = user_scores[user_id]
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_house = sorted_scores[0][0]
    
    house_translation = {
        "Gryffindor": "Ґрифіндор",
        "Hufflepuff": "Гафелпаф",
        "Ravenclaw": "Рейвенклов",
        "Slytherin": "Слизерин"
    }
    
    await message.answer(f"<b>{username}</b> - ви були розподілені у <b>{house_translation[top_house]}</b>!", parse_mode="HTML")
    
    house_details = {
        "Gryffindor": "Ґрифіндор цінує мужність та відвагу.",
        "Hufflepuff": "Гафелпаф цінує наполегливу працю, терпіння та вірність.",
        "Ravenclaw": "Рейвенклов цінує інтелект, креативність та дотепність.",
        "Slytherin": "Слизерин цінує амбіції, хитрість та лідерство."
    }
    
    await message.answer(f"{house_details[top_house]}\n\nПитання до квізу були складені <b>AnyaVashchenko</b> ^^", parse_mode="HTML")
    del user_scores[user_id]
    del user_status[user_id]

async def send_book(message: types.Message, book: Book):
    response = []

    response.append("")
    response.append(f"НАЗВА: [{book.title}]({ovell_url}/book/{book.id})")
    response.append(f"АВТОР(-КА): [{book.author.name}]({ovell_url}/p/{book.author.id})")
    response.append("")
    response.append(f"ПЕРЕКЛАД: {'Так' if book.is_translation else 'Ні'}")
    if book.is_translation:
        response.append(f"ОРИГІНАЛ: [*тиць сюди*]({book.original_link})")
        response.append("")

    response.append(f"СТАТУС: {book.book_status_text if book.book_status else 'Unknown'}")
    response.append(f"РЕЙТИНГ: {book.rating_text if book.rating else 'Unknown'}")
    response.append(f"НАПИСАНО: {book.pages_count}ст.")
    response.append(f"РОЗМІР: {book.book_size_text if book.book_size else 'Unknown'}")
    if book.expected_book_size and book.book_status != BookStatus.COMPLETED:
        response.append(f"ОЧІКУЄТЬСЯ: {book.expected_book_size_text}")

    if book.pairings:
        response.append("")
        response.append("ПЕЙРИНҐИ: " + ', '.join(
            f"{pair.first_character['firstName']} {pair.first_character['lastName']} - {pair.second_character['firstName']} {pair.second_character['lastName']}"
            for pair in book.pairings[:5]
        ) + ('...' if len(book.pairings) > 5 else ''))

    if book.tags:
        response.append("")
        response.append("ТЕҐИ: " + ', '.join(tag.title for tag in book.tags[:5]) + ('...' if len(book.tags) > 5 else ''))

    response.append("")
    if book.description:
        description = book.description
        if len(description) > 300:
            description = description[:300] + '...'
        response.append(f"ОПИС:\n{description}")

    response.append("")

    await message.answer(
        text="\n".join(response),
        parse_mode='MARKDOWN'
    )
    
def parse_book(data: dict) -> Book:
    author = BookUser(id=data['author']['id'], name=data['author']['name'])
    pairings = [BookPair(first_character=pair['firstCharacter'], second_character=pair['secondCharacter']) for pair in data.get('pairings', [])]
    tags = [BookTag(title=tag['title']) for tag in data.get('tags', [])]
    
    book = Book(
        id=data['id'],
        title=data['title'],
        likes_count=data['likesCount'],
        description=data['description'],
        author=author,
        is_translation=data['isTranslation'],
        original_link=data.get('originalLink', ''),
        rating=parse_enum(BookRating, data['rating']),
        book_size=parse_enum(BookSize, data['bookSize']) if data['bookSize'] is not None else None,
        expected_book_size=parse_enum(BookSize, data['expectedBookSize']) if data['expectedBookSize'] is not None else None,
        pages_count=data['pagesCount'],
        book_status=parse_enum(BookStatus, data['bookStatus']),
        pairings=pairings,
        tags=tags
    )
    return book

def parse_enum(enum_class, value, default=None):
    try:
        return enum_class(value)
    except ValueError:
        return default