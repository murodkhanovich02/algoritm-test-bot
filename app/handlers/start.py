from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.admin import admin_menu
from app.keyboards.main import BTN_ADMIN_PANEL, BTN_BACK, main_menu
from app.services.admin_service import is_admin_user


router = Router()


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    user_id = message.from_user.id
    is_admin = await is_admin_user(user_id)

    if is_admin:
        text = (
            "Assalomu alaykum, admin.\n\n"
            "Bu bot orqali test kalitlarini kiritish, "
            "o‘quvchi javoblarini tekshirish va natijalarni ko‘rish mumkin."
        )
    else:
        text = (
            "Assalomu alaykum.\n\n"
            "Bu bot orqali test javoblaringizni topshirishingiz mumkin."
        )

    await message.answer(
        text=text,
        reply_markup=main_menu(user_id, is_admin=is_admin),
    )


@router.message(lambda message: message.text == BTN_ADMIN_PANEL)
async def open_admin_panel(message: Message) -> None:
    user_id = message.from_user.id

    if not await is_admin_user(user_id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    await message.answer(
        text="⚙️ <b>Admin panel</b>",
        reply_markup=admin_menu(),
    )


@router.message(lambda message: message.text == BTN_BACK)
async def back_to_main_menu(message: Message) -> None:
    user_id = message.from_user.id
    is_admin = await is_admin_user(user_id)

    await message.answer(
        text="Asosiy menyu",
        reply_markup=main_menu(user_id, is_admin=is_admin),
    )