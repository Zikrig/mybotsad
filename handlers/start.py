import os
from aiogram import Dispatcher, F
from aiogram.types import Message, FSInputFile, InputMediaPhoto
from aiogram.filters import Command
from keyboards import get_main_menu_keyboard
from data.texts import WELCOME_TEXT, SELECT_ACTION

async def cmd_start(message: Message):
    """Обработчик команды /start"""
    
    # Отправляем фото из папки data/start если они есть
    start_photos_dir = "data/start"
    if os.path.exists(start_photos_dir):
        photos = [f for f in os.listdir(start_photos_dir) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        photos.sort()
        
        if photos:
            try:
                # Отправляем все фото медиа-группой (максимум 10 фото)
                media_group = []
                for i, photo_name in enumerate(photos[:10]):  # Telegram позволяет максимум 10 фото в группе
                    photo_path = os.path.join(start_photos_dir, photo_name)
                    # Проверяем, что файл существует
                    if not os.path.exists(photo_path):
                        print(f"Файл не найден: {photo_path}")
                        continue
                    photo_file = FSInputFile(photo_path)
                    # Caption добавляем только к первому фото
                    if i == 0:
                        media_group.append(InputMediaPhoto(media=photo_file, caption=WELCOME_TEXT, parse_mode="Markdown"))
                    else:
                        media_group.append(InputMediaPhoto(media=photo_file))
                
                if media_group:
                    await message.answer_media_group(media=media_group)
                    # Отправляем кнопки отдельным сообщением
                    await message.answer(
                        SELECT_ACTION,
                        reply_markup=get_main_menu_keyboard()
                    )
                else:
                    # Если не удалось создать медиа-группу, отправляем текст
                    await message.answer(WELCOME_TEXT, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")
            except Exception as e:
                print(f"Ошибка при отправке фотографий при старте: {e}")
                # В случае ошибки отправляем текст
                await message.answer(WELCOME_TEXT, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")
        else:
            await message.answer(WELCOME_TEXT, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")
    else:
        await message.answer(WELCOME_TEXT, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")

def register_start_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))

