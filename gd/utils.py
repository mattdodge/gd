from collections import namedtuple
from datetime import date, datetime, time, timedelta
from logging.handlers import RotatingFileHandler
from urllib.parse import urljoin
import logging
import os

Boundary = namedtuple("Boundary", "date num_parts")

MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4,
          "May": 5, "June": 6, "July": 7, "August": 8, "September": 9,
          "October": 10, "November": 11, "December": 12}

WEB_ROOT = "http://gd2.mlb.com/components/game/mlb/"


def get_boundary(date):
    """Format a boundary date string and return the datetime and the number
    of parts the datetime object was constructed from.

    This could be a partial date consisting of a year;
    year and month; or year, month, and day."""
    parts = 0
    for fmt in ("%Y", "%Y-%m", "%Y-%m-%d"):
        try:
            parts += 1
            return Boundary(datetime.strptime(date, fmt), parts)
        except (TypeError, ValueError):
            continue
    else:
        return Boundary(None, 0)


def get_request_range(begin, end):
    if begin.date is None:
        start = WEB_ROOT
    else:
        start = urljoin(WEB_ROOT,
                        datetime_to_url(begin.date, begin.num_parts))

    if end.date is None:
        print(datetime_to_url)
        stop = urljoin(WEB_ROOT, datetime_to_url(
                       datetime.today() - timedelta(days=1)))
    else:
        stop = urljoin(WEB_ROOT,
                       datetime_to_url(end.date, end.num_parts))

    return start, stop


def get_inclusive_urls(urls, start, stop):
    """Yield URLs which are of the range [start, stop]"""
    in_range = False
    out_range = False
    for url in urls:
        # Check both that a URL contains or is contained within one of
        # the boundaries. This is necessary as deeper links come.
        if url in start or start in url:
            in_range = True
        if url in stop or stop in url:
            out_range = True
        if in_range:
            yield url
        if out_range:
            break


def datetime_to_url(dt, parts=3):
    """Convert a Python datetime into the date portion of a Gameday URL"""
    fragments = ["year_{0.year:04}", "month_{0.month:02}", "day_{0.day:02}"]
    return "/".join(fragments[:parts]).format(dt) + "/"


def create_date(string):
    """Given a string like 'July 2, 1984', turn it into a datetime.date."""
    if not string:
        return date.min
    parts = string.split()
    month = MONTHS[parts[0]]
    day = int(parts[1][:-1])
    year = int(parts[2])
    return date(year, month, day)


def create_datetime(string):
    """Given a string like 2014-07-19T23:12:35Z, return a datetime.datetime."""
    if not string:
        # There are times where pitches have had an empty string for
        # a timestamp, so return the minimum value.
        return datetime.min
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")


def create_time(string):
    """Given a string like 12:00 or 1200, return a datetime.time."""
    if not string:
        return time.min
    string = string.replace(":", "")
    hour = int(string[:2])
    minute = int(string[2:4])
    return time(hour, minute)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    return logger


def enable_logging():
    logger = get_logger("gd")

    level = logging.DEBUG if os.getenv("DEBUG", False) else logging.INFO
    logger.setLevel(level)
    fmt = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s")

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    fh = RotatingFileHandler("gd-util.log", maxBytes=100000, backupCount=5)
    fh.setLevel(level)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
