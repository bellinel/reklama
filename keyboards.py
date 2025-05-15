from aiogram.utils.keyboard import InlineKeyboardBuilder

async def start_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Чат-боты", callback_data="bot")
    kb.button(text="Сайты", callback_data="site")
    kb.button(text="Паресеры", callback_data="pars")
    kb.adjust(1)

    return kb.as_markup()

async def yes_photo_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="yes_photo")
    kb.button(text="Нет", callback_data="no_photo")
    kb.adjust(1)

    return kb.as_markup()

async def yes_text_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="yes_text")
    kb.button(text="Нет", callback_data="no_text")
    kb.adjust(1)

    return kb.as_markup()