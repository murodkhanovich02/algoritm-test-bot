from app.config import settings
from app.database.session import AsyncSessionLocal
from app.repositories.admin_repository import AdminRepository


async def is_admin_user(user_id: int) -> bool:
    """
    Admin tekshiruvi:
    1. .env ichidagi ADMIN_IDS
    2. Database ichidagi admins jadvali
    """

    if user_id in settings.admin_ids:
        return True

    async with AsyncSessionLocal() as session:
        return await AdminRepository.is_admin(
            session=session,
            telegram_user_id=user_id,
        )