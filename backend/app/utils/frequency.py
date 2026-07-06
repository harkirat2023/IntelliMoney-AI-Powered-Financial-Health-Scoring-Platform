from datetime import date as Date, datetime, timedelta


def _calculate_next_date(start_date: Date, frequency: str) -> Date:
    today = Date.today()
    current = start_date

    if frequency == "weekly":
        while current < today:
            current += timedelta(weeks=1)
    elif frequency == "biweekly":
        while current < today:
            current += timedelta(weeks=2)
    elif frequency == "monthly":
        while current < today:
            month = current.month - 1 + 1
            year = current.year + (month // 12)
            month = month % 12 or 12
            day = min(current.day, [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
            current = Date(year, month, day)
    elif frequency == "yearly":
        while current < today:
            current = Date(current.year + 1, current.month, current.day)

    return current


def _detect_frequency(avg_interval: float) -> str | None:
    if 6 <= avg_interval <= 8:
        return "weekly"
    elif 13 <= avg_interval <= 15:
        return "biweekly"
    elif 28 <= avg_interval <= 31:
        return "monthly"
    elif 355 <= avg_interval <= 370:
        return "yearly"
    return None
