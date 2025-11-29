import os
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from keyboards import get_main_menu_keyboard, get_back_to_menu_keyboard
from data.texts import WELCOME_TEXT, ABOUT_TEXT, SELECT_ACTION, SELECT_ACTION_FROM_MENU
from handlers.order import OrderStates

async def show_main_menu(callback: CallbackQuery):
    """Показать главное меню"""
    await callback.answer()
    await callback.message.edit_text(
        WELCOME_TEXT,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )

async def show_about(callback: CallbackQuery):
    """Показать информацию о нас"""
    await callback.answer()
    
    # Отправляем фото из папки data/about если они есть
    about_photos_dir = "data/about"
    if os.path.exists(about_photos_dir):
        photos = [f for f in os.listdir(about_photos_dir) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        photos.sort()
        
        if photos:
            try:
                # Отправляем все фото медиа-группой (максимум 10 фото)
                media_group = []
                for i, photo_name in enumerate(photos[:10]):  # Telegram позволяет максимум 10 фото в группе
                    photo_path = os.path.join(about_photos_dir, photo_name)
                    # Проверяем, что файл существует
                    if not os.path.exists(photo_path):
                        print(f"Файл не найден: {photo_path}")
                        continue
                    photo_file = FSInputFile(photo_path)
                    # Caption добавляем только к первому фото
                    if i == 0:
                        media_group.append(InputMediaPhoto(media=photo_file, caption=ABOUT_TEXT, parse_mode="Markdown"))
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
                        reply_markup=get_back_to_menu_keyboard()
                    )
                else:
                    # Если не удалось создать медиа-группу, отправляем текст
                    await callback.message.answer(
                        ABOUT_TEXT,
                        reply_markup=get_back_to_menu_keyboard(),
                        parse_mode="Markdown"
                    )
            except Exception as e:
                print(f"Ошибка при отправке фотографий 'О нас': {e}")
                import traceback
                traceback.print_exc()
                # В случае ошибки отправляем текст
                await callback.message.answer(
                    ABOUT_TEXT,
                    reply_markup=get_back_to_menu_keyboard(),
                    parse_mode="Markdown"
                )
        else:
            await callback.message.answer(
                ABOUT_TEXT,
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="Markdown"
            )
    else:
        await callback.message.answer(
            ABOUT_TEXT,
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )

async def handle_any_message(message: Message, state: FSMContext):
    """Обработчик всех сообщений - показывает главное меню"""
    # Пропускаем команды
    if message.text and message.text.startswith('/'):
        return
    
    # Пропускаем, если пользователь находится в состоянии заказа
    current_state = await state.get_state()
    if current_state in [OrderStates.waiting_for_name, OrderStates.waiting_for_contact, 
                         OrderStates.waiting_for_tasks, OrderStates.waiting_for_details]:
        return
    
    await message.answer(
        SELECT_ACTION_FROM_MENU,
        reply_markup=get_main_menu_keyboard()
    )

def register_menu_handlers(dp: Dispatcher):
    dp.callback_query.register(show_main_menu, F.data == "main_menu")
    dp.callback_query.register(show_about, F.data == "about")
    # Регистрируем с низким приоритетом, чтобы не перехватывать другие обработчики
    dp.message.register(handle_any_message)

