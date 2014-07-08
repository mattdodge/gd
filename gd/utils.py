from datetime import datetime
import logging
import os


def get_boundary(date):
    """Format a boundary date string and return the datetime and the number
    of parts the datetime object was constructed from.

    This could be a partial date consisting of a year;
    year and month; or year, month, and day."""
    parts = 0
    for fmt in ("%Y", "%Y-%m", "%Y-%m-%d"):
        try:
            parts += 1
            return datetime.strptime(date, fmt), parts
        except (TypeError, ValueError):
            continue
    else:
        return None, 0


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


def setup_logging(filename=None):
    """Setup and return a logger"""
    level = logging.DEBUG if os.environ.get("DEBUG", False) else logging.INFO

    log = logging.getLogger("gd")
    log.setLevel(level)

    formatter = logging.Formatter("%(asctime)s | %(name)s | "
                                  "%(levelname)s | %(message)s")

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    log.addHandler(console)

    if filename is not None:
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

    return log
