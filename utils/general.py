from time import time
from datetime import datetime
from calendar import timegm


def get_time() -> int:
    return int(1000 * time())


def get_time_from_str(time_str: str) -> int:
    split = time_str.split(" ")
    dt = datetime(int(split[2]), int(split[1]), int(split[0]))
    return timegm(dt.timetuple()) * 1000


def get_time_str(time: int) -> str:
    dt = datetime.fromtimestamp(time / 1000)
    return dt.strftime("%d-%m-%Y")


def get_day(time: int) -> str:
    dt = datetime.fromtimestamp(time / 1000)
    return dt.strftime("%a")


def get_minute(time: int) -> str:
    dt = datetime.fromtimestamp(time / 1000)
    return dt.strftime("%M")


def get_time_frmt(frmt: str):
    dt = datetime.now()
    return dt.strftime(frmt)