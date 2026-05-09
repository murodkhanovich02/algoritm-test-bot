from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.keyboards.main import BTN_BACK
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

BTN_TEST_START = "🧪 Test topshirish"
BTN_ADMIN_PANEL = "⚙️ Admin panel"
BTN_BACK = "🔙 Orqaga"


def main_menu(
        user_id: int,
        is_admin: bool = False,
) -> ReplyKeyboardMarkup:
    if is_admin:
        keyboard = [
            [KeyboardButton(text=BTN_ADMIN_PANEL)],
        ]
    else:
        keyboard = [
            [KeyboardButton(text=BTN_TEST_START)],
        ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Kerakli bo‘limni tanlang",
    )


def back_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
    )


BTN_CREATE_TEST = "📄 Test qo‘shish"
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
                InlineKeyboardButton(text="20 minut", callback_data="test_time:1200"),
                InlineKeyboardButton(text="30 minut", callback_data="test_time:1800"),
            ],
            [
                InlineKeyboardButton(text="40 minut", callback_data="test_time:2400"),
                InlineKeyboardButton(text="50 minut", callback_data="test_time:3000"),
            ],
            [
                InlineKeyboardButton(text="60 minut", callback_data="test_time:3600"),
                InlineKeyboardButton(text="70 minut", callback_data="test_time:4200"),
            ],
            [
                InlineKeyboardButton(text="80 minut", callback_data="test_time:4800"),
                InlineKeyboardButton(text="90 minut", callback_data="test_time:5400"),
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


def student_results_keyboard(results: list, test_code: str) -> InlineKeyboardMarkup:
    keyboard = []

    for result in results:
        total = result.correct_count + result.wrong_count

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"👤 {result.full_name} — {result.correct_count}/{total}",
                    callback_data=f"student_result:{result.id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="📄 PDF hisobot",
                callback_data=f"results_pdf:{test_code}",
            )
        ]
    )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Admin panel",
                callback_data="admin_back",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def student_result_back_keyboard(test_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 O‘quvchilar ro‘yxatiga qaytish",
                    callback_data=f"back_results:{test_code}",
                )
            ]
        ]
    )
