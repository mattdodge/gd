from datetime import datetime, timedelta
from urllib.parse import urljoin
import argparse
import asyncio
import functools
import os
import requests
import signal

from gd import scrape
from gd import utils

log = utils.setup_logging("scraper.log")


def do_input():
    pass


def do_parse():
    pass


def _get_request_range(begin, end):
    if begin.date is None:
        start = scrape.WEB_ROOT
    else:
        start = urljoin(scrape.WEB_ROOT,
                        utils.datetime_to_url(begin.date, begin.num_parts))

    if end.date is None:
        stop = urljoin(scrape.WEB_ROOT, utils.datetime_to_url(
                       datetime.today() - timedelta(days=1)))
    else:
        stop = urljoin(scrape.WEB_ROOT,
                       utils.datetime_to_url(end.date, end.num_parts))

    return start, stop


def _get_file_list(session, begin, end):
    all_years = scrape.get_years(session=session)
    inc_years = utils.get_inclusive_urls(all_years, begin, end)

    all_months = scrape.get_months(inc_years, session=session)
    inc_months = utils.get_inclusive_urls(all_months, begin, end)

    all_days = scrape.get_days(inc_months, session=session)
    inc_days = utils.get_inclusive_urls(all_days, begin, end)

    games = scrape.get_games(inc_days, session=session)
    files = scrape.get_files(games, session=session)

    return files


def do_scrape(cache, begin=None, end=None):
    """Run the scraper over the range [begin, end]

    If no beginning is given, scraping starts from the root.
    If no ending is given, scraping ends at the yesterday's date.
    Note: end=yesterday because the schedule is pre-loaded, so scraping
    for today would mean having to account for a game existing but no files
    available."""
    start_scrape = datetime.now()
    begin = utils.get_boundary(begin)
    end = utils.get_boundary(end)

    session = requests.Session()

    start, stop = _get_request_range(begin, end)
    files = _get_file_list(session, start, stop)
    print(list(files)[0])

    count, fails = scrape.download(files, cache)
    end_scrape = datetime.now()
    log.info("%d files downloaded in %s", count,
             str(end_scrape - start_scrape))
    if fails:
        for url in fails:
            log.error("failed to download %s", url)

    return count


def get_args():
    """Return command line arguments as parsed by argparse."""
    parser = argparse.ArgumentParser(description="blah blah blah")
    parser.add_argument("-b", "--begin", dest="begin", type=str,
                        help="Beginning date in %Y-%m-%d format")
    parser.add_argument("-e", "--end", dest="end", type=str,
                        help="Ending date in %Y-%m-%d format")
    parser.add_argument("-c", "--cache", dest="cache", type=str,
                        help="Local cache directory", default=None)
    parser.add_argument("-d", "--daemon", dest="daemon", action="store_true",
                        default=False, help="Run %(prog)s as a daemon.")

    return parser.parse_args()


def main():
    args = get_args()
    do_scrape(args.cache, args.begin, args.end)

    if args.daemon:
        run_daemon()


def run_daemon():
    def exiting(signal):
        print("Got signal %s: exiting" % signal)
        loop.stop()

    loop = asyncio.get_event_loop()
    for sig in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(getattr(signal, sig),
                                functools.partial(exiting, sig))

    print("Event loop running forever, press CTRL+c to interrupt.")
    print("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())
    loop.run_forever()
