from aiogram import Dispatcher
from .start import register_start_handlers
from .order import register_order_handlers
from .bot_types import register_bot_types_handlers
from .menu import register_menu_handlers

def register_handlers(dp: Dispatcher):
    # Регистрируем в правильном порядке - сначала специфичные обработчики
    register_start_handlers(dp)
    register_order_handlers(dp)  # Состояния должны обрабатываться раньше
    register_bot_types_handlers(dp)
    register_menu_handlers(dp)  # Общий обработчик в конце

