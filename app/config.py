import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    bot_token: str
    admin_ids: list[int]
    database_url: str


def parse_admin_ids(value: str | None) -> list[int]:
    if not value:
        return []

    admin_ids = []

    for item in value.split(","):
        item = item.strip()

        if item.isdigit():
            admin_ids.append(int(item))

    return admin_ids


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN")
    admin_ids_raw = os.getenv("ADMIN_IDS")
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///test_checker.db")

    if not bot_token:
        raise ValueError("BOT_TOKEN .env faylda topilmadi.")

    return Settings(
        bot_token=bot_token,
        admin_ids=parse_admin_ids(admin_ids_raw),
        database_url=database_url
    )


settings = get_settings()