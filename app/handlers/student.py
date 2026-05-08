import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database.session import AsyncSessionLocal
from app.keyboards.main import BTN_BACK, BTN_TEST_START, back_menu, main_menu
from app.repositories.result_repository import ResultRepository
from app.repositories.test_repository import TestRepository
from app.services.test_checker import (
    build_student_result_text,
    check_test_answers,
    details_to_json,
)
from app.states.student_states import StudentTestState
from app.utils.validators import (
    escape_html,
    is_valid_answer,
    normalize_answer,
    normalize_test_code,
    normalize_text,
)


router = Router()


async def finish_test_by_timeout(
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()

    test_id = data.get("test_id")
    test_code = data.get("test_code")
    answer_key = data.get("answer_key")
    student_answers = data.get("student_answers", [])
    full_name = data.get("full_name")

    if not test_id or not test_code or not answer_key or not full_name:
        await state.clear()
        return

    student_answers_text = "".join(student_answers)

    result = check_test_answers(answer_key, student_answers_text)
    answers_detail_json = details_to_json(result["details"])

    async with AsyncSessionLocal() as session:
        existing_result = await ResultRepository.get_result_by_test_and_user(
            session=session,
            test_id=test_id,
            telegram_user_id=message.from_user.id,
        )

        if existing_result:
            await state.clear()
            return

        await ResultRepository.create_result(
            session=session,
            test_id=test_id,
            telegram_user_id=message.from_user.id,
            telegram_username=message.from_user.username,
            full_name=full_name,
            student_answers=student_answers_text,
            correct_count=result["correct_count"],
            wrong_count=result["wrong_count"],
            percentage=result["percentage"],
            answers_detail=answers_detail_json,
        )

    await state.clear()

    safe_full_name = escape_html(full_name)

    result_text = build_student_result_text(
        full_name=safe_full_name,
        test_code=test_code,
        result=result,
        is_timeout=True,
    )

    await message.answer(
        text=result_text,
        reply_markup=main_menu(message.from_user.id),
    )


async def test_timer_task(
    message: Message,
    state: FSMContext,
    time_limit_seconds: int,
) -> None:
    await asyncio.sleep(time_limit_seconds)

    current_state = await state.get_state()

    if current_state != StudentTestState.waiting_for_answer.state:
        return

    data = await state.get_data()

    if not data.get("timer_active"):
        return

    await finish_test_by_timeout(message, state)


@router.message(F.text == BTN_TEST_START)
async def student_test_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(StudentTestState.waiting_for_full_name)

    await message.answer(
        text=(
            "🧪 <b>Test topshirish</b>\n\n"
            "Avval 👤 <b>ism-familiyangizni kiriting.</b>\n\n"
            "Masalan:\n"
            "<code>Aliyev Anvar</code>"
        ),
        reply_markup=back_menu(),
    )


@router.message(StudentTestState.waiting_for_full_name)
async def student_enter_full_name(message: Message, state: FSMContext) -> None:
    if message.text == BTN_BACK:
        await state.clear()
        await message.answer(
            text="Asosiy menyu",
            reply_markup=main_menu(message.from_user.id),
        )
        return

    full_name = normalize_text(message.text or "")

    if len(full_name) < 3:
        await message.answer(
            "❌ Ism-familiya juda qisqa.\n\n"
            "Iltimos, to‘liqroq kiriting."
        )
        return

    await state.update_data(full_name=full_name)
    await state.set_state(StudentTestState.waiting_for_test_code)

    await message.answer(
        text=(
            "✅ Ism-familiya qabul qilindi.\n\n"
            "Endi 🧪 <b>test kodini kiriting.</b>\n\n"
            "Masalan:\n"
            "<code>02052026TEST01#</code>\n\n"
            "⚠️ Test kodini to‘g‘ri kiritsangiz, vaqt shu zahoti boshlanadi "
            "va PDF savollar yuboriladi."
        )
    )


@router.message(StudentTestState.waiting_for_test_code)
async def student_enter_test_code(message: Message, state: FSMContext) -> None:
    if message.text == BTN_BACK:
        await state.clear()
        await message.answer(
            text="Asosiy menyu",
            reply_markup=main_menu(message.from_user.id),
        )
        return

    test_code = normalize_test_code(message.text or "")

    data = await state.get_data()
    full_name = data.get("full_name")

    if not full_name:
        await state.clear()
        await message.answer(
            "❌ Ism-familiya topilmadi. Testni qaytadan boshlang.",
            reply_markup=main_menu(message.from_user.id),
        )
        return

    async with AsyncSessionLocal() as session:
        test = await TestRepository.get_active_by_code(session, test_code)

        if not test:
            await message.answer(
                "❌ Bunday faol test topilmadi.\n\n"
                "Test kodini qayta tekshirib kiriting."
            )
            return

        existing_result = await ResultRepository.get_result_by_test_and_user(
            session=session,
            test_id=test.id,
            telegram_user_id=message.from_user.id,
        )

    if existing_result:
        await state.clear()
        await message.answer(
            "⛔ Siz bu testni avval ishlagansiz.\n\n"
            "Bitta test kodini faqat <b>1 marta</b> ishlash mumkin.",
            reply_markup=main_menu(message.from_user.id),
        )
        return

    await state.update_data(
        test_id=test.id,
        test_code=test.test_code,
        question_count=test.question_count,
        answer_key=test.answer_key,
        time_limit_seconds=test.time_limit_seconds,
        current_question=1,
        student_answers=[],
        timer_active=True,
    )

    await state.set_state(StudentTestState.waiting_for_answer)

    asyncio.create_task(
        test_timer_task(
            message=message,
            state=state,
            time_limit_seconds=test.time_limit_seconds,
        )
    )

    await message.answer(
        text=(
            "⏱ <b>Test vaqti boshlandi!</b>\n\n"
            f"👤 <b>O‘quvchi:</b> {escape_html(full_name)}\n"
            f"🧪 <b>Test kodi:</b> <code>{test.test_code}</code>\n"
            f"📌 <b>Savollar soni:</b> {test.question_count} ta\n"
            f"⏱ <b>Vaqt:</b> {test.time_limit_seconds} sekund\n\n"
            "Endi PDF savollar yuboriladi."
        )
    )

    if test.pdf_file_id:
        await message.answer_document(
            document=test.pdf_file_id,
            caption=(
                "📄 <b>Test savollari PDF varianti.</b>\n\n"
                "PDF bilan tanishib, javoblarni ketma-ket kiriting."
            ),
        )
    else:
        await message.answer(
            "⚠️ Bu test uchun PDF topilmadi, lekin test mavjud."
        )

    await message.answer(
        text=(
            "1-javobni kiriting:\n\n"
            "Masalan: <code>A</code>"
        )
    )


@router.message(StudentTestState.waiting_for_answer)
async def student_enter_answer(message: Message, state: FSMContext) -> None:
    if message.text == BTN_BACK:
        await message.answer(
            "⛔ Test jarayonida orqaga chiqib bo‘lmaydi.\n\n"
            "Testni yakunlash uchun javoblarni kiriting yoki vaqt tugashini kuting."
        )
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

    test_id = data["test_id"]
    test_code = data["test_code"]
    question_count = data["question_count"]
    answer_key = data["answer_key"]
    current_question = data["current_question"]
    student_answers = data["student_answers"]
    full_name = data["full_name"]

    async with AsyncSessionLocal() as session:
        existing_result = await ResultRepository.get_result_by_test_and_user(
            session=session,
            test_id=test_id,
            telegram_user_id=message.from_user.id,
        )

    if existing_result:
        await state.clear()
        await message.answer(
            "⛔ Bu test bo‘yicha natijangiz allaqachon saqlangan.",
            reply_markup=main_menu(message.from_user.id),
        )
        return

    student_answers.append(answer)

    if current_question < question_count:
        next_question = current_question + 1

        await state.update_data(
            current_question=next_question,
            student_answers=student_answers,
        )

        await message.answer(
            text=f"{next_question}-javobni kiriting:"
        )
        return

    student_answers_text = "".join(student_answers)
    result = check_test_answers(answer_key, student_answers_text)
    answers_detail_json = details_to_json(result["details"])

    async with AsyncSessionLocal() as session:
        existing_result = await ResultRepository.get_result_by_test_and_user(
            session=session,
            test_id=test_id,
            telegram_user_id=message.from_user.id,
        )

        if existing_result:
            await state.clear()
            await message.answer(
                "⛔ Bu test bo‘yicha natijangiz allaqachon saqlangan.",
                reply_markup=main_menu(message.from_user.id),
            )
            return

        await ResultRepository.create_result(
            session=session,
            test_id=test_id,
            telegram_user_id=message.from_user.id,
            telegram_username=message.from_user.username,
            full_name=full_name,
            student_answers=student_answers_text,
            correct_count=result["correct_count"],
            wrong_count=result["wrong_count"],
            percentage=result["percentage"],
            answers_detail=answers_detail_json,
        )

    await state.update_data(timer_active=False)
    await state.clear()

    safe_full_name = escape_html(full_name)

    result_text = build_student_result_text(
        full_name=safe_full_name,
        test_code=test_code,
        result=result,
        is_timeout=False,
    )

    await message.answer(
        text=result_text,
        reply_markup=main_menu(message.from_user.id),
    )