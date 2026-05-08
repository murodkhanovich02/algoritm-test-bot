from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import StudentResult, Test


class TestRepository:
    @staticmethod
    async def create_test(
        session: AsyncSession,
        test_code: str,
        question_count: int,
        answer_key: str,
        created_by: int,
        time_limit_seconds: int,
        pdf_file_id: str | None = None,
        pdf_file_unique_id: str | None = None,
        pdf_file_name: str | None = None,
    ) -> Test:
        test = Test(
            test_code=test_code,
            question_count=question_count,
            answer_key=answer_key,
            created_by=created_by,
            time_limit_seconds=time_limit_seconds,
            pdf_file_id=pdf_file_id,
            pdf_file_unique_id=pdf_file_unique_id,
            pdf_file_name=pdf_file_name,
            is_active=True,
        )

        session.add(test)
        await session.commit()
        await session.refresh(test)

        return test

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        test_id: int,
    ) -> Test | None:
        stmt = select(Test).where(Test.id == test_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(
        session: AsyncSession,
        test_code: str,
    ) -> Test | None:
        stmt = select(Test).where(Test.test_code == test_code)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_by_code(
        session: AsyncSession,
        test_code: str,
    ) -> Test | None:
        stmt = select(Test).where(
            Test.test_code == test_code,
            Test.is_active.is_(True),
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        session: AsyncSession,
        limit: int = 50,
    ) -> list[Test]:
        stmt = (
            select(Test)
            .order_by(Test.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def close_test(
        session: AsyncSession,
        test: Test,
    ) -> Test:
        test.is_active = False
        await session.commit()
        await session.refresh(test)
        return test

    @staticmethod
    async def delete_test_by_id(
        session: AsyncSession,
        test_id: int,
    ) -> bool:
        test = await TestRepository.get_by_id(session, test_id)

        if not test:
            return False

        await session.execute(
            delete(StudentResult).where(StudentResult.test_id == test_id)
        )

        await session.execute(
            delete(Test).where(Test.id == test_id)
        )

        await session.commit()

        return True