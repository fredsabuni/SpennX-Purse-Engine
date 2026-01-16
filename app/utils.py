from datetime import datetime, timedelta
from typing import Tuple

def parse_datetime(date_string: str) -> datetime:
    """
    Parse datetime string in multiple formats.
    Supports:
    - ISO 8601: 2025-12-31T21:00:00.000Z
    - ISO 8601 with timezone: 2025-12-31T21:00:00+00:00
    - Standard: YYYY-MM-DD HH:MM:SS
    - Date only: YYYY-MM-DD
    """
    # Try ISO 8601 format with Z (UTC)
    if 'T' in date_string:
        # Remove milliseconds and Z
        date_string = date_string.replace('Z', '').split('.')[0]
        # Remove timezone offset if present
        if '+' in date_string:
            date_string = date_string.split('+')[0]
        if date_string.count('-') > 2:  # Has timezone offset with minus
            date_string = date_string.rsplit('-', 1)[0]
        try:
            return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            pass
    
    # Try standard datetime format
    try:
        return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    
    # Try date only format
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"Invalid date format: {date_string}. "
            "Supported formats: YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, or ISO 8601 (2025-12-31T21:00:00.000Z)"
        )

def get_today_range() -> Tuple[datetime, datetime]:
    """Get today's date range (00:00 to 23:59:59)"""
    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end

def get_previous_day_range() -> Tuple[datetime, datetime]:
    """Get previous day's date range (00:00 to 23:59:59)"""
    yesterday = datetime.now() - timedelta(days=1)
    start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end

def get_current_week_range() -> Tuple[datetime, datetime]:
    """Get current week range (Monday 00:00 to Sunday 23:59:59)"""
    now = datetime.now()
    start = now - timedelta(days=now.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    return start, end

def get_previous_week_range() -> Tuple[datetime, datetime]:
    """Get previous week range (Monday 00:00 to Sunday 23:59:59)"""
    now = datetime.now()
    current_week_start = now - timedelta(days=now.weekday())
    start = current_week_start - timedelta(days=7)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    return start, end

def get_current_month_range() -> Tuple[datetime, datetime]:
    """Get current month range (1st 00:00 to last day 23:59:59)"""
    now = datetime.now()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        next_month = start.replace(year=now.year + 1, month=1)
    else:
        next_month = start.replace(month=now.month + 1)
    end = next_month - timedelta(microseconds=1)
    return start, end

def get_previous_month_range() -> Tuple[datetime, datetime]:
    """Get previous month range (1st 00:00 to last day 23:59:59)"""
    now = datetime.now()
    if now.month == 1:
        start = now.replace(year=now.year - 1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = now.replace(month=now.month - 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = current_month_start - timedelta(microseconds=1)
    return start, end

def get_year_to_date_range() -> Tuple[datetime, datetime]:
    """Get year to date range (January 1st 00:00 to current day 23:59:59)"""
    now = datetime.now()
    start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end

def get_date_range(interval: str) -> Tuple[datetime, datetime]:
    """Get date range based on interval name"""
    ranges = {
        "today": get_today_range,
        "previous_day": get_previous_day_range,
        "current_week": get_current_week_range,
        "previous_week": get_previous_week_range,
        "current_month": get_current_month_range,
        "previous_month": get_previous_month_range,
        "year_to_date": get_year_to_date_range,
    }
    return ranges[interval]()
