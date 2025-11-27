from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import Command
from config import ADMIN_ID

async def cmd_user(message: Message, bot: Bot):
    """Обработчик команды /user для получения информации о пользователе по ID"""
    
    # Проверяем, что команду использует админ
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    # Получаем аргумент команды (ID пользователя)
    command_args = message.text.split()
    if len(command_args) < 2:
        await message.answer("❌ Использование: /user <user_id>\n\nПример: /user 123456789")
        return
    
    try:
        user_id = int(command_args[1])
    except ValueError:
        await message.answer("❌ ID пользователя должен быть числом.\n\nПример: /user 123456789")
        return
    
    try:
        # Получаем информацию о пользователе
        chat = await bot.get_chat(user_id)
        
        # Формируем ответ
        username = f"@{chat.username}" if chat.username else "Не указан"
        first_name = chat.first_name or "Не указано"
        last_name = f" {chat.last_name}" if chat.last_name else ""
        full_name = f"{first_name}{last_name}"
        
        response = (
            f"👤 Информация о пользователе:\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Имя: {full_name}\n"
            f"📱 Username: {username}"
        )
        
        await message.answer(response)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении информации о пользователе: {str(e)}\n\nВозможно, пользователь не найден или бот не может получить к нему доступ.")

def register_user_handlers(dp: Dispatcher):
    dp.message.register(cmd_user, Command("user"))

