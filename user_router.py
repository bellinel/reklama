
import asyncio
import os
from aiogram import Router, F , Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from collections import defaultdict
from keyboards import start_kb, yes_photo_kb, yes_text_kb
from state_classes import User
from text import Texts
from dotenv import load_dotenv
load_dotenv()

GROUP_ID = os.getenv('GROUP_ID')
router = Router()

media_buffer = defaultdict(list)
media_group_locks = {}


@router.message(Command('start'))
async def start(message: Message):
    await message.answer(text=Texts.START_MESSAGE, reply_markup=await start_kb())


@router.callback_query(lambda callback: callback.data in ['bot','site','pars'])
async def category(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'bot':
        text = 'Бот'
    if callback.data == 'site':
        text = 'Сайт'
    if callback.data == 'pars':
        text = 'Парсер'

    await state.update_data(category=text)
    await callback.message.edit_text(text=Texts.WORK_MES)
    await state.set_state(User.quest)


@router.message(User.quest)
async def quest(message: Message, state: FSMContext, bot : Bot):
    if message.from_user.username:
        user = f'@{message.from_user.username}'
    else:
        user = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
    user_id = message.from_user.id

    if message.document:
        data = await state.get_data()
        category = data.get('category')

        await bot.send_document(chat_id=GROUP_ID,document=message.document.file_id, caption=f'Категория {category}\nЗадание от {user}\n id {user_id}',parse_mode='HTML')
        await message.answer(text="✅ Задание получено! Скоро с вами свяжется наш специалист.")
        return
    
    if message.text:
        await state.update_data(text=message.text)
        await message.answer(text="Хотите добавить фотографии?", reply_markup=await yes_text_kb())
        return
    
    if message.media_group_id:
        group_id = message.media_group_id
        file_id = message.photo[-1].file_id
        media_buffer[group_id].append(file_id)
        
        if group_id in media_group_locks:
            return
        
        media_group_locks[group_id] = True
        await asyncio.sleep(2)

        all_photos = media_buffer.pop(group_id, [])
        media_group_locks.pop(group_id, None)

        
        await message.answer(text='Хотите добавить текст к ТЗ?',reply_markup=await yes_photo_kb())
        await state.update_data(media=all_photos)
    else:
        file_id = message.photo[-1].file_id
        await state.update_data(media=[file_id])
        
        await message.answer(text="Хотите добавить текст к ТЗ?",reply_markup=await yes_photo_kb())
        
        
                
    

@router.callback_query(lambda callback: callback.data in ['yes_photo', 'no_photo'])
async def yes_photo(callback: CallbackQuery, state: FSMContext, bot : Bot):
    if callback.data == 'yes_photo':
        await callback.message.edit_text(text=f'Напишите описание и отправьте его.')
        await state.set_state(User.text)
    if callback.data == 'no_photo':
        await callback.message.edit_text(text=f'✅ Задание получено! Скоро с вами свяжется наш специалист.')
        data = await state.get_data()
        category = data.get('category')
        
        photos = data.get('media')
        if callback.from_user.username:
            user = f'@{callback.from_user.username}'
        else:
            user = f'<a href="tg://user?id={callback.from_user.id}">{callback.from_user.first_name}</a>'
        user_id = callback.from_user.id
        if len(photos) == 1:
            await bot.send_photo(chat_id=GROUP_ID, photo=photos[0], caption=f'Категория {category}\nЗадание от {user}\n id {user_id}',parse_mode='HTML')
        else:
            media = [InputMediaPhoto(media=msg) for msg in photos]
            
            await bot.send_media_group(chat_id=GROUP_ID, media=media)
            await bot.send_message(chat_id=GROUP_ID, text=f'Категория {category}\nЗадание от {user}\n id {user_id}',parse_mode='HTML')

        await state.clear()

@router.message(User.text)
async def text(message: Message, state: FSMContext, bot : Bot):
    if not message.text:
        await message.answer(text="Пожалуйста, отправьте описание в текстовом формате.")
        return
    data = await state.get_data()
    category = data.get('category')
    photos = data.get('media')
    if message.from_user.username:
        user = f'@{message.from_user.username}'
    else:
        user = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
    
    user_id = message.from_user.id
    await message.answer(text="✅ Задание получено! Скоро с вами свяжется наш специалист.")
    if len(photos) == 1:
        await bot.send_photo(chat_id=GROUP_ID, photo=photos[0], caption=f'Категория {category}\nЗадание от {user}\n id {user_id}\nТекст:{message.text}',parse_mode='HTML')
    else:
        media = [InputMediaPhoto(media=msg) for msg in photos]
        
        await bot.send_media_group(chat_id=GROUP_ID, media=media)
        await bot.send_message(chat_id=GROUP_ID, text=f'Категория {category}\nЗадание от {user}\n id {user_id}\nТекст:{message.text}',parse_mode='HTML')

    await state.clear()


@router.callback_query(lambda callback: callback.data in ['yes_text', 'no_text'])
async def yes_text(callback: CallbackQuery, state: FSMContext, bot : Bot):
    if callback.data == 'yes_text':
        await callback.message.edit_text(text="Отправьте одно фото или несколько.")
        
        await state.set_state(User.photo)
    if callback.data == 'no_text':
        await callback.message.edit_text(text=f'✅ Задание получено! Скоро с вами свяжется наш специалист.')
        data = await state.get_data()
        category = data.get('category')
        text = data.get('text')
        if callback.from_user.username:
            user = f'@{callback.from_user.username}'
        else:
            user = f'<a href="tg://user?id={callback.from_user.id}">{callback.from_user.first_name}</a>'
        user_id = callback.from_user.id
        await bot.send_message(chat_id=GROUP_ID, text=f'Категория {category}\nЗадание от {user}\n id {user_id}\nТекст:{text}',parse_mode='HTML')
        
        

@router.message(User.photo)
async def photo(message: Message, state: FSMContext, bot : Bot):
    if not message.photo:
        await message.answer(text="Пожалуйста, отправьте фото.")
    data = await state.get_data()
    category = data.get('category')
    text = data.get('text')
    if message.from_user.username:
        user = f'@{message.from_user.username}'
    else:
        user = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
    user_id = message.from_user.id
    

    if message.media_group_id:
        group_id = message.media_group_id
        file_id = message.photo[-1].file_id
        media_buffer[group_id].append(file_id)
        if message.from_user.username:
            user = f'@{message.from_user.username}'
        else:
            user = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'


        if group_id in media_group_locks:
            return
        
        media_group_locks[group_id] = True
        await asyncio.sleep(2)

        all_photos = media_buffer.pop(group_id, [])
        media_group_locks.pop(group_id, None)
        
        
        
        media = [InputMediaPhoto(media=msg) for msg in all_photos]
       
        await bot.send_media_group(chat_id=GROUP_ID, media=media)
        await bot.send_message(chat_id=GROUP_ID, text=f'Категория {category}\nЗадание от {user}\n id {user_id}\nТекст: {text}',parse_mode='HTML')
        await message.answer(text="✅ Задание получено! Скоро с вами свяжется наш специалист.") 
    else:
        file_id = message.photo[-1].file_id
        await message.answer(text="✅ Задание получено! Скоро с вами свяжется наш специалист.")
        await bot.send_photo(chat_id=GROUP_ID, photo=file_id, caption=f'Категория {category}\nЗадание от {user}\n id {user_id}\nТекст: {text}',parse_mode='HTML')
    await state.clear()