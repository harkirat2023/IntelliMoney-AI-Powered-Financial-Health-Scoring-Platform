from datetime import UTC, date, datetime, time


def utc_now() -> datetime:
    return datetime.now(UTC)


def month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    start = datetime(year, month, 1, tzinfo=UTC)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=UTC)
    else:
        end = datetime(year, month + 1, 1, tzinfo=UTC)
    return start, end


def date_to_datetime(value: date) -> datetime:
    return datetime.combine(value, time.min, tzinfo=UTC)
