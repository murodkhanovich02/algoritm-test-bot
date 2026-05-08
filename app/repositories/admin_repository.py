from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Admin


class AdminRepository:
    @staticmethod
    async def is_admin(
        session: AsyncSession,
        telegram_user_id: int,
    ) -> bool:
        stmt = select(Admin).where(Admin.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def add_admin(
        session: AsyncSession,
        telegram_user_id: int,
        created_by: int | None = None,
    ) -> Admin:
        admin = Admin(
            telegram_user_id=telegram_user_id,
            created_by=created_by,
        )

        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        return admin

    @staticmethod
    async def get_all_admins(session: AsyncSession) -> list[Admin]:
        stmt = select(Admin).order_by(Admin.created_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def remove_admin(
        session: AsyncSession,
        telegram_user_id: int,
    ) -> bool:
        stmt = delete(Admin).where(Admin.telegram_user_id == telegram_user_id)
        result = await session.execute(stmt)
        await session.commit()

        return result.rowcount > 0