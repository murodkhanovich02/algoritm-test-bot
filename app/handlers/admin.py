from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.database.session import AsyncSessionLocal
from app.keyboards.admin import (
    BTN_ADD_ADMIN,
    BTN_ADMIN_LIST,
    BTN_CREATE_TEST,
    BTN_DELETE_ADMIN,
    BTN_RESULTS,
    BTN_TEST_LIST,
    admin_menu,
    test_delete_confirm_keyboard,
    tests_list_keyboard,
    time_limit_keyboard,
)
from app.keyboards.main import BTN_BACK, back_menu
from app.repositories.admin_repository import AdminRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.test_repository import TestRepository
from app.services.admin_service import is_admin_user
from app.states.admin_states import AdminResultState, CreateTestState, ManageAdminState
from app.utils.validators import (
    is_valid_answer,
    is_valid_question_count,
    is_valid_test_code,
    normalize_answer,
    normalize_test_code,
)


router = Router()


@router.message(F.text == BTN_CREATE_TEST)
async def create_test_start(message: Message, state: FSMContext) -> None:
    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    await state.clear()
    await state.set_state(CreateTestState.waiting_for_pdf)

    await message.answer(
        text=(
            "📄 <b>Test savollari PDF faylini yuboring.</b>\n\n"
            "Avval PDF yuborasiz, keyin bot test kodini, vaqtini va kalitlarni so‘raydi."
        ),
        reply_markup=back_menu(),
    )


@router.message(CreateTestState.waiting_for_pdf)
async def create_test_pdf(message: Message, state: FSMContext) -> None:
    if message.text == BTN_BACK:
        await state.clear()
        await message.answer(
            text="Admin panel",
            reply_markup=admin_menu(),
        )
        return

    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    if not message.document:
        await message.answer(
            "❌ Iltimos, PDF fayl yuboring.\n\n"
            "Matn yoki rasm emas, aynan <b>PDF document</b> bo‘lishi kerak."
        )
        return

    document = message.document

    if document.mime_type != "application/pdf":
        await message.answer(
            "❌ Fayl PDF formatida emas.\n\n"
            "Iltimos, <b>.pdf</b> fayl yuboring."
        )
        return

    await state.update_data(
        pdf_file_id=document.file_id,
        pdf_file_unique_id=document.file_unique_id,
        pdf_file_name=document.file_name or "test.pdf",
    )

    await state.set_state(CreateTestState.waiting_for_test_code)

    await message.answer(
        text=(
            "✅ PDF qabul qilindi.\n\n"
            "🔑 <b>Endi test uchun kalit so‘zini kiriting.</b>\n\n"
            "Masalan:\n"
            "<code>02052026TEST01#</code>"
        ),
    )


@router.message(CreateTestState.waiting_for_test_code)
async def create_test_code(message: Message, state: FSMContext) -> None:
    if message.text == BTN_BACK:
        await state.clear()
        await message.answer(
            text="Admin panel",
            reply_markup=admin_menu(),
        )
        return

    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    test_code = normalize_test_code(message.text or "")

    if not is_valid_test_code(test_code):
        await message.answer(
            "❌ Test kodi noto‘g‘ri.\n\n"
            "Masalan: <code>02052026TEST01#</code>"
        )
        return

    async with AsyncSessionLocal() as session:
        existing_test = await TestRepository.get_by_code(session, test_code)

    if existing_test:
        await message.answer(
            "❌ Bu test kodi oldin yaratilgan.\n\n"
            "Boshqa test kodi kiriting."
        )
        return

    await state.update_data(test_code=test_code)
    await state.set_state(CreateTestState.waiting_for_time_limit)

    await message.answer(
        text=(
            "⏱ <b>Test vaqtini tanlang.</b>\n\n"
            "Hozircha qiymatlar <b>sekund</b> sifatida ishlaydi."
        ),
        reply_markup=time_limit_keyboard(),
    )


@router.callback_query(
    CreateTestState.waiting_for_time_limit,
    F.data.startswith("test_time:"),
)
async def create_test_time_limit(callback: CallbackQuery, state: FSMContext) -> None:
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("Siz admin emassiz.", show_alert=True)
        return

    raw_value = callback.data.split(":")[1]

    if not raw_value.isdigit():
        await callback.answer("Vaqt noto‘g‘ri.", show_alert=True)
        return

    time_limit_seconds = int(raw_value)

    await state.update_data(time_limit_seconds=time_limit_seconds)
    await state.set_state(CreateTestState.waiting_for_question_count)

    await callback.message.edit_text(
        text=(
            f"✅ Test vaqti tanlandi: <b>{time_limit_seconds} sekund</b>\n\n"
            "📌 <b>Endi testlar sonini kiriting.</b>\n\n"
            "Masalan: <code>30</code>"
        )
    )

    await callback.answer()


@router.message(CreateTestState.waiting_for_question_count)
async def create_test_question_count(message: Message, state: FSMContext) -> None:
    if message.text == BTN_BACK:
        await state.clear()
        await message.answer(
            text="Admin panel",
            reply_markup=admin_menu(),
        )
        return

    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    value = message.text or ""

    if not is_valid_question_count(value):
        await message.answer(
            "❌ Testlar soni noto‘g‘ri.\n\n"
            "Faqat raqam kiriting. Masalan: <code>30</code>\n"
            "Eng kam: 1\n"
            "Eng ko‘p: 500"
        )
        return

    question_count = int(value.strip())

    await state.update_data(
        question_count=question_count,
        current_question=1,
        answers=[],
    )
    await state.set_state(CreateTestState.waiting_for_answer)

    await message.answer(
        text="1-kalitni kiriting:\n\nMasalan: <code>A</code>"
    )


@router.message(CreateTestState.waiting_for_answer)
async def create_test_answer(message: Message, state: FSMContext) -> None:
    if message.text == BTN_BACK:
        await state.clear()
        await message.answer(
            text="Admin panel",
            reply_markup=admin_menu(),
        )
        return

    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    answer = normalize_answer(message.text or "")

    if not is_valid_answer(answer):
        await message.answer(
            "❌ Javob noto‘g‘ri.\n\n"
            "Faqat quyidagilardan birini kiriting:\n"
            "<code>A</code>, <code>B</code>, <code>C</code>, <code>D</code>"
        )
        return

    data = await state.get_data()

    test_code = data["test_code"]
    question_count = data["question_count"]
    current_question = data["current_question"]
    answers = data["answers"]

    answers.append(answer)

    if current_question < question_count:
        next_question = current_question + 1

        await state.update_data(
            current_question=next_question,
            answers=answers,
        )

        await message.answer(
            text=f"{next_question}-kalitni kiriting:"
        )
        return

    answer_key = "".join(answers)

    async with AsyncSessionLocal() as session:
        await TestRepository.create_test(
            session=session,
            test_code=test_code,
            question_count=question_count,
            answer_key=answer_key,
            created_by=message.from_user.id,
            time_limit_seconds=data["time_limit_seconds"],
            pdf_file_id=data["pdf_file_id"],
            pdf_file_unique_id=data["pdf_file_unique_id"],
            pdf_file_name=data["pdf_file_name"],
        )

    await state.clear()

    await message.answer(
        text=(
            "✅ <b>Test muvaffaqiyatli yaratildi.</b>\n\n"
            f"📄 <b>PDF:</b> {data['pdf_file_name']}\n"
            f"🧪 <b>Test kodi:</b> <code>{test_code}</code>\n"
            f"⏱ <b>Vaqt:</b> {data['time_limit_seconds']} sekund\n"
            f"📌 <b>Savollar soni:</b> {question_count} ta\n"
            f"🔑 <b>Kalitlar:</b> <code>{answer_key}</code>"
        ),
        reply_markup=admin_menu(),
    )


@router.message(F.text == BTN_TEST_LIST)
async def show_test_list(message: Message) -> None:
    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    async with AsyncSessionLocal() as session:
        tests = await TestRepository.get_all(session)

    if not tests:
        await message.answer("📭 Hozircha testlar mavjud emas.")
        return

    await message.answer(
        text=(
            "📋 <b>Testlar ro‘yxati</b>\n\n"
            "O‘chirmoqchi bo‘lgan test kodini tanlang:"
        ),
        reply_markup=tests_list_keyboard(tests),
    )


@router.callback_query(F.data.startswith("test_detail:"))
async def show_test_delete_confirm(callback: CallbackQuery) -> None:
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("Siz admin emassiz.", show_alert=True)
        return

    test_id_raw = callback.data.split(":")[1]

    if not test_id_raw.isdigit():
        await callback.answer("Test ID noto‘g‘ri.", show_alert=True)
        return

    test_id = int(test_id_raw)

    async with AsyncSessionLocal() as session:
        test = await TestRepository.get_by_id(session, test_id)

    if not test:
        await callback.message.edit_text("❌ Test topilmadi yoki o‘chirib yuborilgan.")
        await callback.answer()
        return

    status = "🟢 faol" if test.is_active else "🔴 yopilgan"
    pdf_status = "📄 PDF bor" if test.pdf_file_id else "📄 PDF yo‘q"

    await callback.message.edit_text(
        text=(
            "⚠️ <b>Testni o‘chirish</b>\n\n"
            f"🧪 <b>Test kodi:</b> <code>{test.test_code}</code>\n"
            f"📌 <b>Savollar soni:</b> {test.question_count} ta\n"
            f"⏱ <b>Vaqt:</b> {test.time_limit_seconds} sekund\n"
            f"{pdf_status}\n"
            f"Holat: {status}\n\n"
            "Shu test o‘chirilsinmi?"
        ),
        reply_markup=test_delete_confirm_keyboard(test.id),
    )

    await callback.answer()


@router.callback_query(F.data.startswith("delete_test_yes:"))
async def delete_test_yes(callback: CallbackQuery) -> None:
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("Siz admin emassiz.", show_alert=True)
        return

    test_id_raw = callback.data.split(":")[1]

    if not test_id_raw.isdigit():
        await callback.answer("Test ID noto‘g‘ri.", show_alert=True)
        return

    test_id = int(test_id_raw)

    async with AsyncSessionLocal() as session:
        test = await TestRepository.get_by_id(session, test_id)

        if not test:
            await callback.message.edit_text("❌ Test topilmadi yoki oldin o‘chirilgan.")
            await callback.answer()
            return

        test_code = test.test_code
        deleted = await TestRepository.delete_test_by_id(session, test_id)

    if not deleted:
        await callback.message.edit_text("❌ Testni o‘chirishda xatolik yuz berdi.")
        await callback.answer()
        return

    await callback.message.edit_text(
        text=(
            "✅ <b>Test o‘chirildi.</b>\n\n"
            f"🧪 <b>Test kodi:</b> <code>{test_code}</code>"
        )
    )

    await callback.answer("Test o‘chirildi.")


@router.callback_query(F.data == "delete_test_no")
async def delete_test_no(callback: CallbackQuery) -> None:
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("Siz admin emassiz.", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        tests = await TestRepository.get_all(session)

    if not tests:
        await callback.message.edit_text("📭 Hozircha testlar mavjud emas.")
        await callback.answer()
        return

    await callback.message.edit_text(
        text=(
            "📋 <b>Testlar ro‘yxati</b>\n\n"
            "O‘chirmoqchi bo‘lgan test kodini tanlang:"
        ),
        reply_markup=tests_list_keyboard(tests),
    )

    await callback.answer()


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery) -> None:
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("Siz admin emassiz.", show_alert=True)
        return

    await callback.message.edit_text("⚙️ Admin panelga qaytildi.")
    await callback.message.answer(
        text="⚙️ <b>Admin panel</b>",
        reply_markup=admin_menu(),
    )

    await callback.answer()


@router.message(F.text == BTN_RESULTS)
async def result_start(message: Message, state: FSMContext) -> None:
    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    await state.clear()
    await state.set_state(AdminResultState.waiting_for_test_code)

    await message.answer(
        text=(
            "📊 <b>Natijalarini ko‘rmoqchi bo‘lgan test kodini kiriting.</b>\n\n"
            "Masalan:\n"
            "<code>02052026TEST01#</code>"
        ),
        reply_markup=back_menu(),
    )


@router.message(AdminResultState.waiting_for_test_code)
async def show_results_by_code(message: Message, state: FSMContext) -> None:
    if message.text == BTN_BACK:
        await state.clear()
        await message.answer(
            text="Admin panel",
            reply_markup=admin_menu(),
        )
        return

    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    test_code = normalize_test_code(message.text or "")

    async with AsyncSessionLocal() as session:
        test = await TestRepository.get_by_code(session, test_code)

        if not test:
            await message.answer(
                "❌ Bunday test topilmadi.\n\n"
                "Test kodini qayta tekshirib kiriting."
            )
            return

        results = await ResultRepository.get_results_by_test_code(session, test_code)

    await state.clear()

    if not results:
        await message.answer(
            text=(
                f"📊 <b>Test:</b> <code>{test_code}</code>\n\n"
                "Bu test bo‘yicha hali natijalar mavjud emas."
            ),
            reply_markup=admin_menu(),
        )
        return

    lines = [
        f"📊 <b>Test natijalari:</b> <code>{test_code}</code>",
        f"📌 <b>Savollar soni:</b> {test.question_count} ta",
        f"⏱ <b>Vaqt:</b> {test.time_limit_seconds} sekund",
        "",
    ]

    for index, result in enumerate(results, start=1):
        username = f"@{result.telegram_username}" if result.telegram_username else "username yo‘q"

        lines.append(
            f"{index}. <b>{result.full_name}</b>\n"
            f"   👤 Telegram: {username}\n"
            f"   ✅ Natija: {result.correct_count}/{test.question_count}\n"
            f"   ❌ Xato: {result.wrong_count} ta\n"
            f"   📊 Foiz: {result.percentage}%"
        )

    await message.answer(
        text="\n\n".join(lines),
        reply_markup=admin_menu(),
    )


@router.message(F.text == BTN_ADD_ADMIN)
async def add_admin_start(message: Message, state: FSMContext) -> None:
    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    await state.clear()
    await state.set_state(ManageAdminState.waiting_for_admin_id)

    await message.answer(
        "➕ <b>Admin qo‘shish</b>\n\n"
        "Admin qilinadigan Telegram user ID ni kiriting.\n\n"
        "Masalan:\n"
        "<code>123456789</code>",
        reply_markup=back_menu(),
    )


@router.message(ManageAdminState.waiting_for_admin_id)
async def add_admin_finish(message: Message, state: FSMContext) -> None:
    if message.text == BTN_BACK:
        await state.clear()
        await message.answer("Admin panel", reply_markup=admin_menu())
        return

    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    text = (message.text or "").strip()

    if not text.isdigit():
        await message.answer("❌ Telegram ID faqat raqam bo‘lishi kerak.")
        return

    new_admin_id = int(text)

    if new_admin_id in settings.admin_ids:
        await state.clear()
        await message.answer(
            "⚠️ Bu user allaqachon .env orqali admin qilingan.",
            reply_markup=admin_menu(),
        )
        return

    async with AsyncSessionLocal() as session:
        exists = await AdminRepository.is_admin(
            session=session,
            telegram_user_id=new_admin_id,
        )

        if exists:
            await state.clear()
            await message.answer(
                "⚠️ Bu user allaqachon admin.",
                reply_markup=admin_menu(),
            )
            return

        await AdminRepository.add_admin(
            session=session,
            telegram_user_id=new_admin_id,
            created_by=message.from_user.id,
        )

    await state.clear()

    await message.answer(
        f"✅ Yangi admin qo‘shildi:\n\n<code>{new_admin_id}</code>",
        reply_markup=admin_menu(),
    )


@router.message(F.text == BTN_ADMIN_LIST)
async def show_admin_list(message: Message) -> None:
    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    async with AsyncSessionLocal() as session:
        db_admins = await AdminRepository.get_all_admins(session)

    lines = [
        "👥 <b>Adminlar ro‘yxati</b>",
        "",
        "📌 <b>.env orqali berilgan adminlar:</b>",
    ]

    for index, admin_id in enumerate(settings.admin_ids, start=1):
        lines.append(f"{index}. <code>{admin_id}</code>")

    lines.append("")
    lines.append("📌 <b>Bot orqali qo‘shilgan adminlar:</b>")

    if not db_admins:
        lines.append("Hozircha yo‘q.")
    else:
        for index, admin in enumerate(db_admins, start=1):
            lines.append(f"{index}. <code>{admin.telegram_user_id}</code>")

    await message.answer("\n".join(lines))


@router.message(F.text == BTN_DELETE_ADMIN)
async def delete_admin_start(message: Message, state: FSMContext) -> None:
    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    await state.clear()
    await state.set_state(ManageAdminState.waiting_for_delete_admin_id)

    await message.answer(
        "🗑 <b>Admin o‘chirish</b>\n\n"
        "O‘chiriladigan admin Telegram ID sini kiriting.\n\n"
        "Masalan:\n"
        "<code>123456789</code>",
        reply_markup=back_menu(),
    )


@router.message(ManageAdminState.waiting_for_delete_admin_id)
async def delete_admin_finish(message: Message, state: FSMContext) -> None:
    if message.text == BTN_BACK:
        await state.clear()
        await message.answer("Admin panel", reply_markup=admin_menu())
        return

    if not await is_admin_user(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    text = (message.text or "").strip()

    if not text.isdigit():
        await message.answer("❌ Telegram ID faqat raqam bo‘lishi kerak.")
        return

    admin_id = int(text)

    if admin_id in settings.admin_ids:
        await message.answer(
            "⛔ .env ichidagi adminni bot orqali o‘chirib bo‘lmaydi.\n\n"
            "Uni faqat .env fayldan olib tashlash mumkin."
        )
        return

    async with AsyncSessionLocal() as session:
        deleted = await AdminRepository.remove_admin(
            session=session,
            telegram_user_id=admin_id,
        )

    await state.clear()

    if not deleted:
        await message.answer(
            "❌ Bunday admin bazadan topilmadi.",
            reply_markup=admin_menu(),
        )
        return

    await message.answer(
        f"✅ Admin o‘chirildi:\n\n<code>{admin_id}</code>",
        reply_markup=admin_menu(),
    )