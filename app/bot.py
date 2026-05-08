from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.database.session import init_db
from app.handlers.start import router as start_router
from app.handlers.admin import router as admin_router
from app.handlers.student import router as student_router


async def start_bot() -> None:
    await init_db()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(student_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)