from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree
import os

import requests

from gd import storage
from gd import utils

logger = utils.get_logger(__name__)

WEB_ROOT = "http://gd2.mlb.com/components/game/mlb/"

# ElementTree chokes on the doctype in these files so just skip over it.
# We're using an XML parser to parse HTML. Whatever, the rest of it works.
WITHOUT_DOCTYPE = slice(56, -1)


def upload(urls):
    session = requests.Session()

    driver = storage.get_driver()
    container = None
    uploads = 0
    for url in urls:
        parts = urlsplit(url)
        filename = os.path.split(parts.path)[1]
        # Skip directory pages.
        if not filename:
            continue

        if container is None:
            container = storage.get_container(driver, parts.netloc)

        object_name = parts.path

        response = session.get(url)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            logger.error("%s upload failed: %s", url, exc)
            continue

        storage.upload_object(driver, container, object_name, response.content)
        uploads += 1
    logger.info("Uploaded %d objects", uploads)


def download(urls):
    """Download `urls` into `root`. Return the count of files downloaded.
    Each URL is stored as its full URL (minus the scheme)."""
    session = requests.Session()
    downloads = 0
    for url in urls:
        parts = urlsplit(url)
        directory, filename = os.path.split(parts.path)
        # Skip directory pages.
        if not filename:
            continue

        target = parts.netloc + directory
        # Ignore if the target directory already existed.
        os.makedirs(target, exist_ok=True)

        response = session.get(url)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            logger.error("download error: %s raised %s", url, str(exc))
            continue

        with open(os.path.join(target, filename), "w") as fh:
            fh.write(response.content.decode("utf8"))
            loger.debug("downloaded %s", url)
            downloads += 1

    logger.info("Downloaded %d files" % downloads)


def web_scraper(roots, match=None, session=None):
    """Yield URLs in a directory which start with `match`.
    If `match` is None, all links are yielded."""
    for root in roots:
        if session is not None:
            response = session.get(root)
        else:
            response = requests.get(root)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            logger.error("scraping %s raised %s", root, str(exc))
            continue

        # Parse the directory listing, but ignore the DOCTYPE.
        source = ElementTree.fromstring(response.content[WITHOUT_DOCTYPE])
        a_tags = source.findall(".//a")
        for a in a_tags:
            url = a.attrib["href"]
            if match is None or url[slice(0, len(match))] == match:
                yield urljoin(root, url)


def filesystem_scraper(roots, match=None, **kwargs):
    """Yield paths in a directory which start with `match`.
    If `match` is None, all files are yielded."""
    for root in roots:
        for name in os.listdir(root):
            if match is None or name.startswith(match):
                yield os.path.join(root, name)


def get_years(root=WEB_ROOT, source=web_scraper, session=None):
    """From the root URL, yield URLs to the available years."""
    yield from source([root], "year", session)


def get_months(years, source=web_scraper, session=None):
    """Yield URLs to the available months for every year."""
    yield from source(years, "month", session)


def get_days(months, source=web_scraper, session=None):
    """Yield URLs to the available days for every month."""
    yield from source(months, "day", session)


def get_games(days, source=web_scraper, session=None):
    """Yield URLs to the available games for every day."""
    yield from source(days, "gid", session)


def get_files(games, source=web_scraper, session=None):
    """Yield URLs to the relevant files for every game."""
    for game in games:
        yield from source([game], "players.xml", session)
        yield from source([game], "game.xml", session)
        yield from source([urljoin(game, "inning/")],
                          "inning_all.xml", session)
