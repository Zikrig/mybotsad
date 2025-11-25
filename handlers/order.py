from aiogram import Dispatcher, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import get_main_menu_keyboard
from config import ADMIN_ID
from data.bot_types import BOT_TYPES
from data.texts import (
    ASK_NAME, ASK_NAME_ERROR, ASK_CONTACT, ASK_CONTACT_ERROR, ASK_TASKS, ASK_DETAILS,
    ORDER_SUCCESS, ORDER_NEW, ORDER_NAME, ORDER_CONTACT, ORDER_TELEGRAM, ORDER_ID,
    ORDER_TASKS, ORDER_TASKS_NOT_SELECTED, ORDER_DETAILS, ORDER_DETAILS_NOT_PROVIDED,
    ORDER_DETAILS_TEXT, ORDER_DETAILS_PHOTO_WITH_CAPTION, ORDER_DETAILS_PHOTO_WITHOUT_CAPTION,
    ORDER_DETAILS_VOICE, ORDER_DETAILS_AUDIO, ORDER_DETAILS_VIDEO_NOTE, ORDER_STATUS_NOT_READY, ORDER_STATUS_READY,
    ADMIN_DONE_CALLBACK, PHOTO_FROM, VOICE_FROM, AUDIO_FROM, VIDEO_NOTE_FROM, NOT_SPECIFIED, NOT_SPECIFIED_USERNAME
)

# Список задач для выбора
TASK_OPTIONS = [
    "Рассказать о себе/фирме/продукции",
    "Сопровождать мероприятие",
    "Получить контакты или другие данные от клиентов",
    "Проверка знаний или другие тесты",
    "Информирование людей/база знаний",
    "Умный помощник",
    "Интеграция нейросети",
    "Пока не решили"
]

class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()
    waiting_for_tasks = State()
    waiting_for_details = State()

def get_tasks_keyboard(selected_tasks: list) -> InlineKeyboardMarkup:
    """Создать клавиатуру для выбора задач с галочками/крестиками"""
    keyboard = []
    selected_set = set(selected_tasks)  # Преобразуем в set для быстрой проверки
    
    for i, task in enumerate(TASK_OPTIONS):
        # Используем эмодзи: ✅ для выбранных, ❌ для невыбранных
        if i in selected_set:
            emoji = "✅"
        else:
            emoji = "❌"
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"{emoji} {task}",
                callback_data=f"task_toggle_{i}"
            )
        ])
    
    # Кнопка "ГОТОВО" внизу
    keyboard.append([
        InlineKeyboardButton(
            text="ГОТОВО",
            callback_data="tasks_done"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def start_order(callback: CallbackQuery, state: FSMContext):
    """Начать процесс заказа"""
    await callback.answer()
    await state.set_state(OrderStates.waiting_for_name)
    await state.update_data(selected_tasks=[], bot_type=None)
    await callback.message.answer(ASK_NAME)

async def start_order_from_bot_type(callback: CallbackQuery, state: FSMContext):
    """Начать процесс заказа из детального просмотра типа бота"""
    await callback.answer()
    # Извлекаем тип бота (например, "order_anketnik" -> "anketnik")
    bot_type = callback.data.replace("order_", "")
    # Проверяем, что это валидный тип бота
    if bot_type not in BOT_TYPES:
        await callback.message.answer("Ошибка: тип бота не найден.")
        return
    await state.set_state(OrderStates.waiting_for_name)
    await state.update_data(selected_tasks=[], bot_type=bot_type)
    await callback.message.answer(ASK_NAME)

async def process_name(message: Message, state: FSMContext):
    """Обработать имя"""
    name = message.text.strip()
    if not name:
        await message.answer(ASK_NAME_ERROR)
        return
    
    await state.update_data(name=name)
    await state.set_state(OrderStates.waiting_for_contact)
    await message.answer(ASK_CONTACT)

async def process_contact(message: Message, state: FSMContext):
    """Обработать контакт"""
    contact = message.text.strip()
    if not contact:
        await message.answer(ASK_CONTACT_ERROR)
        return
    
    await state.update_data(contact=contact)
    await state.set_state(OrderStates.waiting_for_tasks)
    
    # Показываем выбор задач
    data = await state.get_data()
    selected_tasks = data.get('selected_tasks', [])
    
    await message.answer(
        ASK_TASKS,
        reply_markup=get_tasks_keyboard(selected_tasks)
    )

async def toggle_task(callback: CallbackQuery, state: FSMContext):
    """Переключить выбор задачи"""
    await callback.answer()
    
    # Извлекаем индекс задачи
    task_index = int(callback.data.split("_")[-1])
    
    data = await state.get_data()
    selected_tasks = list(data.get('selected_tasks', []))
    
    # Переключаем выбор
    if task_index in selected_tasks:
        selected_tasks.remove(task_index)
    else:
        selected_tasks.append(task_index)
    
    await state.update_data(selected_tasks=selected_tasks)
    
    # Обновляем клавиатуру
    await callback.message.edit_reply_markup(
        reply_markup=get_tasks_keyboard(selected_tasks)
    )

async def tasks_done(callback: CallbackQuery, state: FSMContext):
    """Завершить выбор задач"""
    await callback.answer()
    
    data = await state.get_data()
    selected_tasks = data.get('selected_tasks', [])
    
    # Разрешаем продолжить даже без выбора задач
    await state.set_state(OrderStates.waiting_for_details)
    
    # Создаем клавиатуру для пропуска
    skip_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip_details")]
    ])
    
    await callback.message.answer(
        ASK_DETAILS,
        reply_markup=skip_keyboard
    )

async def skip_details(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Пропустить подробности"""
    await callback.answer()
    await process_order_complete(state, bot, callback.message, details=None)

async def process_details(message: Message, state: FSMContext, bot: Bot):
    """Обработать подробности о проекте"""
    details = None
    
    # Определяем тип контента (проверяем в порядке приоритета)
    if message.photo:
        caption = message.caption or ""
        details = {"type": "photo", "content": caption, "file_id": message.photo[-1].file_id}
    elif message.video_note:
        details = {"type": "video_note", "file_id": message.video_note.file_id}
    elif message.voice:
        details = {"type": "voice", "file_id": message.voice.file_id}
    elif message.audio:
        details = {"type": "audio", "file_id": message.audio.file_id}
    elif message.text:
        details = {"type": "text", "content": message.text}
    
    await process_order_complete(state, bot, message, details=details)

async def process_order_complete(state: FSMContext, bot: Bot, message: Message, details=None):
    """Завершить заказ и отправить отчет админу"""
    data = await state.get_data()
    name = data.get('name', NOT_SPECIFIED)
    contact = data.get('contact', NOT_SPECIFIED)
    selected_tasks = data.get('selected_tasks', [])
    bot_type = data.get('bot_type')
    
    user = message.from_user
    username = f"@{user.username}" if user.username else NOT_SPECIFIED_USERNAME
    
    # Формируем список выбранных задач
    if selected_tasks:
        tasks_text = "\n".join([f"• {TASK_OPTIONS[i]}" for i in sorted(selected_tasks)])
    else:
        tasks_text = ORDER_TASKS_NOT_SELECTED
    
    # Формируем текст отчета
    order_text = (
        f"{ORDER_NEW}\n\n"
        f"{ORDER_NAME} {name}\n"
        f"{ORDER_CONTACT} {contact}\n"
        f"{ORDER_TELEGRAM} {username}\n"
        f"{ORDER_ID} {user.id}\n\n"
    )
    
    # Добавляем информацию о типе бота, если он был выбран
    if bot_type and bot_type in BOT_TYPES:
        bot_type_name = BOT_TYPES[bot_type]['name']
        order_text += f"🤖 Тип бота: {bot_type_name}\n\n"
    
    order_text += f"{ORDER_TASKS}\n{tasks_text}\n\n"
    
    # Добавляем подробности если есть
    if details:
        if details["type"] == "text":
            order_text += f"{ORDER_DETAILS_TEXT} {details['content']}\n"
        elif details["type"] == "photo":
            if details['content']:
                order_text += f"{ORDER_DETAILS_PHOTO_WITH_CAPTION} {details['content']}\n"
            else:
                order_text += f"{ORDER_DETAILS_PHOTO_WITHOUT_CAPTION}\n"
        elif details["type"] == "voice":
            order_text += f"{ORDER_DETAILS_VOICE}\n"
        elif details["type"] == "audio":
            order_text += f"{ORDER_DETAILS_AUDIO}\n"
        elif details["type"] == "video_note":
            order_text += f"{ORDER_DETAILS_VIDEO_NOTE}\n"
    else:
        order_text += f"{ORDER_DETAILS} {ORDER_DETAILS_NOT_PROVIDED}\n"
    
    order_text += f"\n{ORDER_STATUS_NOT_READY}"
    
    # Создаем клавиатуру с кнопкой ГОТОВО
    done_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ГОТОВО", callback_data=f"admin_done_{user.id}")]
    ])
    
    # Отправляем админу
    try:
        sent_message = await bot.send_message(ADMIN_ID, order_text, reply_markup=done_keyboard)
        
        # Сохраняем ID сообщения для последующего обновления
        await state.update_data(admin_message_id=sent_message.message_id)
        
        # Прикрепляем сообщение сразу
        try:
            await bot.pin_chat_message(
                chat_id=ADMIN_ID,
                message_id=sent_message.message_id,
                disable_notification=True
            )
        except Exception as e:
            print(f"Ошибка прикрепления сообщения: {e}")
        
        # Если есть медиа, отправляем отдельно
        if details and details["type"] in ["photo", "voice", "audio", "video_note"]:
            if details["type"] == "photo":
                await bot.send_photo(ADMIN_ID, details["file_id"], caption=f"{PHOTO_FROM} {name}")
            elif details["type"] == "voice":
                await bot.send_voice(ADMIN_ID, details["file_id"], caption=f"{VOICE_FROM} {name}")
            elif details["type"] == "audio":
                await bot.send_audio(ADMIN_ID, details["file_id"], caption=f"{AUDIO_FROM} {name}")
            elif details["type"] == "video_note":
                await bot.send_video_note(ADMIN_ID, details["file_id"])
                await bot.send_message(ADMIN_ID, f"{VIDEO_NOTE_FROM} {name}")
    except Exception as e:
        print(f"Ошибка отправки сообщения админу: {e}")
    
    # Подтверждение пользователю
    await message.answer(
        ORDER_SUCCESS,
        reply_markup=get_main_menu_keyboard()
    )
    
    await state.clear()

async def handle_admin_done(callback: CallbackQuery, bot: Bot):
    """Обработать нажатие кнопки ГОТОВО админом"""
    await callback.answer(ADMIN_DONE_CALLBACK)
    
    # Обновляем сообщение - убираем кнопку и меняем статус
    message_text = callback.message.text
    if ORDER_STATUS_NOT_READY in message_text:
        new_text = message_text.replace(ORDER_STATUS_NOT_READY, ORDER_STATUS_READY)
    else:
        new_text = message_text.replace(ORDER_STATUS_READY, ORDER_STATUS_NOT_READY)
    
    # Удаляем кнопку
    await callback.message.edit_text(new_text, reply_markup=None)
    
    # Открепляем сообщение
    try:
        # Открепляем конкретное сообщение по его ID
        await bot.unpin_chat_message(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id
        )
    except Exception as e:
        # Если не получилось открепить конкретное сообщение, пробуем открепить последнее
        try:
            await bot.unpin_chat_message(chat_id=callback.message.chat.id)
        except Exception as e2:
            print(f"Ошибка открепления сообщения: {e2}")

def register_order_handlers(dp: Dispatcher):
    # Обработка заказа из главного меню
    dp.callback_query.register(start_order, F.data == "order")
    # Обработка заказа из детального просмотра типа бота (order_anketnik, order_control и т.д.)
    # Должен быть после start_order, чтобы не перехватывать "order"
    dp.callback_query.register(start_order_from_bot_type, F.data.startswith("order_"))
    # Обработка переключения задач
    dp.callback_query.register(toggle_task, F.data.startswith("task_toggle_"))
    # Обработка завершения выбора задач
    dp.callback_query.register(tasks_done, F.data == "tasks_done")
    # Обработка пропуска подробностей
    dp.callback_query.register(skip_details, F.data == "skip_details")
    # Обработка кнопки ГОТОВО админом (нужно передать bot)
    # Регистрируем через lambda или создаем отдельную функцию-обертку
    async def admin_done_wrapper(callback: CallbackQuery, bot: Bot):
        await handle_admin_done(callback, bot)
    
    dp.callback_query.register(admin_done_wrapper, F.data.startswith("admin_done_"))
    # Обработка сообщений в состояниях
    dp.message.register(process_name, OrderStates.waiting_for_name)
    dp.message.register(process_contact, OrderStates.waiting_for_contact)
    # Обработка подробностей (любой тип контента)
    dp.message.register(
        process_details, 
        OrderStates.waiting_for_details
    )

