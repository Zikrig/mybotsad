import os
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto
from keyboards import get_bot_types_keyboard, get_bot_type_detail_keyboard
from data.bot_types import BOT_TYPES
from data.texts import SELECT_BOT_TYPE, BOT_TYPE_NOT_FOUND, SELECT_ACTION

async def show_bot_types(callback: CallbackQuery):
    """Показать список типов ботов"""
    await callback.answer()
    await callback.message.edit_text(SELECT_BOT_TYPE, reply_markup=get_bot_types_keyboard())

async def show_bot_type_detail(callback: CallbackQuery):
    """Показать детальную информацию о типе бота"""
    await callback.answer()
    
    # Извлекаем тип бота из callback_data (например, "bot_type_anketnik" -> "anketnik")
    bot_type = callback.data.replace("bot_type_", "")
    
    if bot_type not in BOT_TYPES:
        await callback.message.answer(BOT_TYPE_NOT_FOUND)
        return
    
    bot_info = BOT_TYPES[bot_type]
    text = (
        f"📋 {bot_info['name']}\n\n"
        f"{bot_info['description']}\n\n"
        f"💰 Цена: {bot_info['price']}"
    )
    
    # Отправляем фото из папки типа бота
    photos_dir = bot_info['photos_dir']
    if os.path.exists(photos_dir):
        photos = [f for f in os.listdir(photos_dir) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        photos.sort()
        
        if photos:
            try:
                # Отправляем все фото медиа-группой (максимум 10 фото)
                media_group = []
                for i, photo_name in enumerate(photos[:10]):  # Telegram позволяет максимум 10 фото в группе
                    photo_path = os.path.join(photos_dir, photo_name)
                    # Проверяем, что файл существует
                    if not os.path.exists(photo_path):
                        print(f"Файл не найден: {photo_path}")
                        continue
                    photo_file = FSInputFile(photo_path)
                    # Caption добавляем только к первому фото
                    if i == 0:
                        media_group.append(InputMediaPhoto(media=photo_file, caption=text))
                    else:
                        media_group.append(InputMediaPhoto(media=photo_file))
                
                if media_group:
                    # Удаляем предыдущее сообщение перед отправкой медиа-группы
                    try:
                        await callback.message.delete()
                    except:
                        pass  # Игнорируем ошибку, если сообщение уже удалено
                    
                    # Отправляем медиа-группу через бота
                    await callback.bot.send_media_group(
                        chat_id=callback.message.chat.id,
                        media=media_group
                    )
                    # Отправляем кнопки отдельным сообщением
                    await callback.bot.send_message(
                        chat_id=callback.message.chat.id,
                        text=SELECT_ACTION,
                        reply_markup=get_bot_type_detail_keyboard(bot_type)
                    )
                else:
                    # Если не удалось создать медиа-группу, отправляем текст
                    await callback.message.answer(
                        text,
                        reply_markup=get_bot_type_detail_keyboard(bot_type)
                    )
            except Exception as e:
                print(f"Ошибка при отправке фотографий для {bot_type}: {e}")
                import traceback
                traceback.print_exc()
                # В случае ошибки отправляем текст
                await callback.message.answer(
                    text,
                    reply_markup=get_bot_type_detail_keyboard(bot_type)
                )
        else:
            await callback.message.answer(
                text,
                reply_markup=get_bot_type_detail_keyboard(bot_type)
            )
    else:
        await callback.message.answer(
            text,
            reply_markup=get_bot_type_detail_keyboard(bot_type)
        )

def register_bot_types_handlers(dp: Dispatcher):
    dp.callback_query.register(show_bot_types, F.data == "bot_types")
    dp.callback_query.register(show_bot_type_detail, F.data.startswith("bot_type_"))

