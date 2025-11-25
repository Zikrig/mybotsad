from data.texts import (
    BOT_TYPE_ANKETNIK_NAME, BOT_TYPE_ANKETNIK_DESCRIPTION, BOT_TYPE_ANKETNIK_PRICE,
    BOT_TYPE_CONTROL_NAME, BOT_TYPE_CONTROL_DESCRIPTION, BOT_TYPE_CONTROL_PRICE,
    BOT_TYPE_VIZITKA_NAME, BOT_TYPE_VIZITKA_DESCRIPTION, BOT_TYPE_VIZITKA_PRICE,
    BOT_TYPE_CUSTOM_NAME, BOT_TYPE_CUSTOM_DESCRIPTION, BOT_TYPE_CUSTOM_PRICE
)

BOT_TYPES = {
    "anketnik": {
        "name": BOT_TYPE_ANKETNIK_NAME,
        "description": BOT_TYPE_ANKETNIK_DESCRIPTION,
        "price": BOT_TYPE_ANKETNIK_PRICE,
        "photos_dir": "data/bot_types/anketnik"
    },
    "control": {
        "name": BOT_TYPE_CONTROL_NAME,
        "description": BOT_TYPE_CONTROL_DESCRIPTION,
        "price": BOT_TYPE_CONTROL_PRICE,
        "photos_dir": "data/bot_types/control"
    },
    "vizitka": {
        "name": BOT_TYPE_VIZITKA_NAME,
        "description": BOT_TYPE_VIZITKA_DESCRIPTION,
        "price": BOT_TYPE_VIZITKA_PRICE,
        "photos_dir": "data/bot_types/vizitka"
    },
    "custom": {
        "name": BOT_TYPE_CUSTOM_NAME,
        "description": BOT_TYPE_CUSTOM_DESCRIPTION,
        "price": BOT_TYPE_CUSTOM_PRICE,
        "photos_dir": "data/bot_types/custom"
    }
}

