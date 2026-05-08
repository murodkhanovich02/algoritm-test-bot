import re


ALLOWED_ANSWERS = {"A", "B", "C", "D"}


def normalize_text(value: str) -> str:
    return value.strip()


def normalize_test_code(value: str) -> str:
    return value.strip().upper()


def normalize_answer(value: str) -> str:
    return value.strip().upper()


def is_valid_answer(value: str) -> bool:
    answer = normalize_answer(value)
    return answer in ALLOWED_ANSWERS


def is_valid_question_count(value: str) -> bool:
    value = value.strip()

    if not value.isdigit():
        return False

    count = int(value)

    return 1 <= count <= 500


def is_valid_test_code(value: str) -> bool:
    value = value.strip()

    if not value:
        return False

    if len(value) < 5:
        return False

    return True


def format_percentage(value: float) -> str:
    if value.is_integer():
        return f"{int(value)}%"

    return f"{value:.1f}%"


def escape_html(text: str | None) -> str:
    if not text:
        return ""

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def is_likely_date_test_code(value: str) -> bool:
    """
    Masalan:
    02052026TEST01#
    Buni majburiy qilmaymiz, faqat kerak bo‘lsa ishlatamiz.
    """
    value = value.strip().upper()
    pattern = r"^\d{8}TEST\d+#$"
    return bool(re.match(pattern, value))