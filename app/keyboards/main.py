from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


BTN_TEST_START = "🧪 Test topshirish"
BTN_ADMIN_PANEL = "⚙️ Admin panel"
BTN_BACK = "🔙 Orqaga"


def main_menu(
    user_id: int,
    is_admin: bool = False,
) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=BTN_TEST_START)]
    ]

    if is_admin:
        buttons.append([KeyboardButton(text=BTN_ADMIN_PANEL)])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Kerakli bo‘limni tanlang",
    )


def back_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_BACK)]
        ],
        resize_keyboard=True,
    )