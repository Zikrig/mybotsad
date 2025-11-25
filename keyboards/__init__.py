from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.texts import (
    BOT_TYPE_ANKETNIK_NAME, BOT_TYPE_CONTROL_NAME,
    BOT_TYPE_VIZITKA_NAME, BOT_TYPE_CUSTOM_NAME
)

def get_main_menu_keyboard():
    """Главное меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Типы ботов", callback_data="bot_types")],
        [InlineKeyboardButton(text="ℹ️ О нас", callback_data="about")],
        [InlineKeyboardButton(text="🛒 Заказать", callback_data="order")]
    ])
    return keyboard

def get_back_to_menu_keyboard():
    """Кнопка возврата в главное меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="main_menu")]
    ])
    return keyboard

def get_bot_types_keyboard():
    """Меню типов ботов"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📝 {BOT_TYPE_ANKETNIK_NAME}", callback_data="bot_type_anketnik")],
        [InlineKeyboardButton(text=f"👥 {BOT_TYPE_CONTROL_NAME}", callback_data="bot_type_control")],
        [InlineKeyboardButton(text=f"💼 {BOT_TYPE_VIZITKA_NAME}", callback_data="bot_type_vizitka")],
        [InlineKeyboardButton(text=f"🎨 {BOT_TYPE_CUSTOM_NAME}", callback_data="bot_type_custom")],
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="main_menu")]
    ])
    return keyboard

def get_bot_type_detail_keyboard(bot_type: str):
    """Кнопки для детального просмотра типа бота"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Заказать", callback_data=f"order_{bot_type}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="bot_types")]
    ])
    return keyboard

def get_order_bot_type_keyboard():
    """Выбор типа бота при заказе"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📝 {BOT_TYPE_ANKETNIK_NAME}", callback_data="order_type_anketnik")],
        [InlineKeyboardButton(text=f"👥 {BOT_TYPE_CONTROL_NAME}", callback_data="order_type_control")],
        [InlineKeyboardButton(text=f"💼 {BOT_TYPE_VIZITKA_NAME}", callback_data="order_type_vizitka")],
        [InlineKeyboardButton(text=f"🎨 {BOT_TYPE_CUSTOM_NAME}", callback_data="order_type_custom")],
        [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="order_skip_type")]
    ])
    return keyboard

