from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    test_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    question_count: Mapped[int] = mapped_column(Integer, nullable=False)

    answer_key: Mapped[str] = mapped_column(Text, nullable=False)

    time_limit_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=60,
    )

    pdf_file_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_file_unique_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pdf_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    results: Mapped[list["StudentResult"]] = relationship(
        back_populates="test",
        cascade="all, delete-orphan",
    )


class StudentResult(Base):
    __tablename__ = "student_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    test_id: Mapped[int] = mapped_column(
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False,
    )

    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    telegram_username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    student_answers: Mapped[str] = mapped_column(Text, nullable=False)

    correct_count: Mapped[int] = mapped_column(Integer, nullable=False)

    wrong_count: Mapped[int] = mapped_column(Integer, nullable=False)

    percentage: Mapped[float] = mapped_column(Float, nullable=False)

    answers_detail: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    test: Mapped["Test"] = relationship(back_populates="results")


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )

    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )