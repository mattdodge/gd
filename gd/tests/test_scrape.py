from unittest.mock import MagicMock, mock_open, patch
from urllib.parse import urljoin
import os
import unittest

from pretend import stub
from requests import HTTPError

from gd import scrape


class Test_web_scraper(unittest.TestCase):
    """Test gd.scrape.web_scraper"""

    @patch("requests.get")
    def test_get_exception(self, mock_get):
        mock_get.side_effect = Exception
        rv = scrape.web_scraper(["lol"])
        self.assertRaises(Exception, next, rv)

    @patch("requests.get")
    def test_get_raises_status(self, mock_get):
        response = MagicMock()
        response.raise_for_status.side_effect = HTTPError
        mock_get.return_value = response
        rv = scrape.web_scraper(["lol"])
        self.assertEqual(list(rv), [])

    @patch("requests.get")
    @patch("gd.scrape.ElementTree.fromstring")
    def test_bs_raises(self, mock_fromstring, mock_get):
        mock_fromstring.side_effect = Exception
        rv = scrape.web_scraper(["lol"])
        self.assertRaises(Exception, next, rv)

    @patch("requests.get")
    @patch("gd.scrape.ElementTree.fromstring")
    def test_no_links(self, mock_fromstring, mock_get):
        source = MagicMock()
        source.findall.return_value = []
        mock_fromstring.return_value = source
        rv = scrape.web_scraper(["lol"])
        self.assertEqual(list(rv), [])

    @patch("requests.get")
    @patch("gd.scrape.ElementTree.fromstring")
    def test_matches(self, mock_fromstring, mock_get):
        root = "http://www.example.com"
        link1, link2 = MagicMock(), MagicMock()
        link1.attrib = {"href": "foo123"}
        link2.attrib = {"href": "bar456"}

        source = MagicMock()
        source.findall.return_value = [link1, link2]
        mock_fromstring.return_value = source

        for match, expected in ((None, [urljoin(root, "foo123"),
                                        urljoin(root, "bar456")]),
                                ("foo", [urljoin(root, "foo123")]),
                                ("lol", [])):
            with self.subTest(match=match):
                rv = scrape.web_scraper([root], match)
                self.assertEqual(list(rv), expected)

    def test_no_roots(self):
        expected = []
        actual = list(scrape.web_scraper([]))
        self.assertEqual(actual, expected)

    @patch("gd.scrape.ElementTree.fromstring")
    def test_requests_session(self, mock_fromstring):
        response = stub(raise_for_status=lambda: None, content="content")
        session = stub(get=lambda arg: response)

        root = "http://www.example.com"
        source = MagicMock()
        link1 = MagicMock()
        link1.attrib = {"href": "foo123"}
        source.findall.return_value = [link1]
        mock_fromstring.return_value = source

        expected = [urljoin(root, "foo123")]
        rv = scrape.web_scraper([root], session=session)
        self.assertEqual(list(rv), expected)


class Test_filesystem_scraper(unittest.TestCase):
    """Test gd.scrape.filesystem_scraper"""

    @patch("os.listdir")
    def test_scraper(self, mock_listdir):
        root = "rootdir"
        file1, file2 = "foo123", "bar456"
        mock_listdir.return_value = [file1, file2]

        for match, expected in ((None, [os.path.join(root, file1),
                                        os.path.join(root, file2)]),
                                ("foo", [os.path.join(root, file1)]),
                                ("lol", [])):
            with self.subTest(match=match):
                rv = scrape.filesystem_scraper([root], match)
                self.assertEqual(list(rv), expected)

    def test_no_roots(self):
        expected = []
        actual = list(scrape.filesystem_scraper([]))
        self.assertEqual(actual, expected)


class Test_get_urls(unittest.TestCase):
    """Test all gd.scrape.get_* functions"""

    def test_get(self):
        expected = "abcdefg"

        def fake_scraper(*args):
            yield from expected

        for fn in (scrape.get_years, scrape.get_months, scrape.get_days,
                   scrape.get_games):
            with self.subTest(function=fn):
                actual = fn(["root"], source=fake_scraper)
                self.assertEqual(list(actual), list(expected))

    def test_get_files(self):
        expected = ["players.xml",
                    "game.xml",
                    "inning_all.xml"]

        def fake_scraper(root, match, session):
            """Just yield back the match, make sure we end up with
            the same amount of items."""
            yield from [match]

        actual = scrape.get_files(["root"], source=fake_scraper)
        self.assertEqual(list(actual), list(expected))


class Test_download(unittest.TestCase):
    """Test gd.scrape.download"""

    @patch("requests.Session.get")
    @patch("os.makedirs")
    def test_file(self, mock_makedirs, mock_get):
        urls = ["http://gd.mlb.com/test1.xml", "http://gd.mlb.com/test2.xml"]
        targets = ["gd.mlb.com/test1.xml", "gd.mlb.com/test1.xml"]
        content = "content"

        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.content.side_effect = content
        mock_get.return_value = response

        mo = mock_open()
        # Need to patch `open` within the gd.scrape namespace.
        with patch("%s.open" % scrape.__name__, mo, create=True):
            scrape.download(urls)

        mo.assert_any_call(targets[0], "w")
        mo.assert_any_call(targets[1], "w")

    @patch("requests.Session.get")
    @patch("os.makedirs")
    def test_directory(self, mock_makedirs, mock_get):
        url = "http://gd.mlb.com/inning/"

        response = MagicMock()
        response.raise_for_status = MagicMock()
        mock_get.return_value = response

        mo = mock_open()
        # Need to patch `open` within the gd.scrape namespace.
        with patch("%s.open" % scrape.__name__, mo, create=True):
            scrape.download([url])

    @patch("requests.Session.get")
    def test_HTTPError(self, mock_get):
        url = "http://gd.mlb.com/inning/inning_all.xml"

        response = MagicMock()
        response.raise_for_status = MagicMock(side_effect=HTTPError)
        mock_get.return_value = response

        scrape.download([url])
