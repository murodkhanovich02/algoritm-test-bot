from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.keyboards.main import BTN_BACK


BTN_CREATE_TEST = "📄 PDF test qo‘shish"
BTN_TEST_LIST = "📋 Testlar ro‘yxati"
BTN_RESULTS = "📊 Natijalar"

BTN_ADD_ADMIN = "➕ Admin qo‘shish"
BTN_ADMIN_LIST = "👥 Adminlar ro‘yxati"
BTN_DELETE_ADMIN = "🗑 Admin o‘chirish"


def admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_CREATE_TEST)],
            [
                KeyboardButton(text=BTN_TEST_LIST),
                KeyboardButton(text=BTN_RESULTS),
            ],
            [
                KeyboardButton(text=BTN_ADD_ADMIN),
                KeyboardButton(text=BTN_ADMIN_LIST),
            ],
            [KeyboardButton(text=BTN_DELETE_ADMIN)],
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Admin panel",
    )


def time_limit_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="20 sekund", callback_data="test_time:20"),
                InlineKeyboardButton(text="30 sekund", callback_data="test_time:30"),
            ],
            [
                InlineKeyboardButton(text="40 sekund", callback_data="test_time:40"),
                InlineKeyboardButton(text="50 sekund", callback_data="test_time:50"),
            ],
            [
                InlineKeyboardButton(text="60 sekund", callback_data="test_time:60"),
                InlineKeyboardButton(text="70 sekund", callback_data="test_time:70"),
            ],
            [
                InlineKeyboardButton(text="80 sekund", callback_data="test_time:80"),
                InlineKeyboardButton(text="90 sekund", callback_data="test_time:90"),
            ],
        ]
    )


def tests_list_keyboard(tests: list) -> InlineKeyboardMarkup:
    keyboard = []

    for test in tests:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"🧪 {test.test_code}",
                    callback_data=f"test_detail:{test.id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="admin_back",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def test_delete_confirm_keyboard(test_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ha, o‘chirish",
                    callback_data=f"delete_test_yes:{test_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Yo‘q, qaytish",
                    callback_data="delete_test_no",
                ),
            ]
        ]
    )