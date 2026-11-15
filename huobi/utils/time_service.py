import time
import datetime


def get_current_timestamp():
    return int(round(time.time() * 1000))


def get_current_timestamp_in_second():
    return int(time.time())


def convert_cst_in_second_to_utc(time_in_second):
    if time_in_second is None:
        return 0
    try:
        time_in_second = int(time_in_second)
    except (ValueError, TypeError):
        return 0
    if 946656000 < time_in_second < 946656000000:
        return (time_in_second - 8 * 60 * 60) * 1000
    else:
        return 0


def convert_cst_in_millisecond_to_utc(time_in_ms):
    if time_in_ms is None:
        return 0
    try:
        time_in_ms = int(time_in_ms)
    except (ValueError, TypeError):
        return 0
    if time_in_ms > 946656000000:
        return time_in_ms - 8 * 60 * 60 * 1000
    else:
        return 0


def timestamp_to_date(ts_in_millisecond, fmt="%Y-%m-%d %H:%M:%S"):
    if ts_in_millisecond is None:
        return ""
    try:
        ts = int(ts_in_millisecond)
        return datetime.datetime.fromtimestamp(ts / 1000, tz=datetime.timezone.utc).strftime(fmt)
    except (ValueError, TypeError, OSError, OverflowError):
        return ""


def date_to_timestamp(date_str, fmt="%Y-%m-%d"):
    if date_str is None:
        return 0
    try:
        dt = datetime.datetime.strptime(date_str, fmt)
        return int(time.mktime(dt.timetuple()) * 1000)
    except (ValueError, TypeError):
        return 0
