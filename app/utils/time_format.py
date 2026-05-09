def format_time_limit(seconds: int) -> str:
    if seconds >= 60 and seconds % 60 == 0:
        return f"{seconds // 60} minut"

    return f"{seconds} sekund"
