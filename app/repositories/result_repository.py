from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import StudentResult, Test


class ResultRepository:
    @staticmethod
    async def create_result(
        session: AsyncSession,
        test_id: int,
        telegram_user_id: int,
        telegram_username: str | None,
        full_name: str,
        student_answers: str,
        correct_count: int,
        wrong_count: int,
        percentage: float,
        answers_detail: str,
    ) -> StudentResult:
        result = StudentResult(
            test_id=test_id,
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
            full_name=full_name,
            student_answers=student_answers,
            correct_count=correct_count,
            wrong_count=wrong_count,
            percentage=percentage,
            answers_detail=answers_detail,
        )

        session.add(result)
        await session.commit()
        await session.refresh(result)

        return result

    @staticmethod
    async def get_result_by_test_and_user(
        session: AsyncSession,
        test_id: int,
        telegram_user_id: int,
    ) -> StudentResult | None:
        stmt = select(StudentResult).where(
            StudentResult.test_id == test_id,
            StudentResult.telegram_user_id == telegram_user_id,
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_result_by_id(
        session: AsyncSession,
        result_id: int,
    ) -> StudentResult | None:
        stmt = select(StudentResult).where(StudentResult.id == result_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_results_by_test_code(
        session: AsyncSession,
        test_code: str,
    ) -> list[StudentResult]:
        stmt = (
            select(StudentResult)
            .join(Test, Test.id == StudentResult.test_id)
            .where(Test.test_code == test_code)
            .order_by(StudentResult.correct_count.desc())
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_results_by_test_id(
        session: AsyncSession,
        test_id: int,
    ) -> list[StudentResult]:
        stmt = (
            select(StudentResult)
            .where(StudentResult.test_id == test_id)
            .order_by(StudentResult.correct_count.desc())
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())