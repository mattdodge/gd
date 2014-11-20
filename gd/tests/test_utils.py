from datetime import datetime, date, time
from unittest.mock import patch
import logging
import unittest

from pretend import stub

from gd import utils


class Test_get_boundary(unittest.TestCase):

    def test_with_namedtuple(self):
        actual = utils.get_boundary("")
        self.assertIsNone(actual.date)
        self.assertEqual(actual.num_parts, 0)

    def test_None(self):
        actual_dt, actual_parts = utils.get_boundary(None)
        self.assertIsNone(actual_dt)
        self.assertEqual(actual_parts, 0)

    def test_empty(self):
        actual_dt, actual_parts = utils.get_boundary("")
        self.assertIsNone(actual_dt)
        self.assertEqual(actual_parts, 0)

    def test_bad_data(self):
        actual_dt, actual_parts = utils.get_boundary("lololololol")
        self.assertIsNone(actual_dt)
        self.assertEqual(actual_parts, 0)

    def test_year(self):
        year = "2014"
        expected_parts = 1
        expected_dt = datetime.strptime(year, "%Y")
        actual_dt, actual_parts = utils.get_boundary(year)
        self.assertEqual(actual_dt, expected_dt)
        self.assertEqual(actual_parts, expected_parts)

    def test_year_month(self):
        year = "2014-07"
        expected_parts = 2
        expected_dt = datetime.strptime(year, "%Y-%m")
        actual_dt, actual_parts = utils.get_boundary(year)
        self.assertEqual(actual_dt, expected_dt)
        self.assertEqual(actual_parts, expected_parts)

    def test_year_month_day(self):
        year = "2014-07-02"
        expected_parts = 3
        expected_dt = datetime.strptime(year, "%Y-%m-%d")
        actual_dt, actual_parts = utils.get_boundary(year)
        self.assertEqual(actual_dt, expected_dt)
        self.assertEqual(actual_parts, expected_parts)


class Test_get_inclusive_urls(unittest.TestCase):

    def _test_range(self, start, stop, expected):
        urls = ["a/a/a", "a/b/a", "a/c/a", "a/d/a", "a/e/a"]
        actual = utils.get_inclusive_urls(urls, start, stop)
        self.assertEqual(list(actual), expected)

    def test_early_range(self):
        start = "a/a"
        stop = "a/c"
        expected = ["a/a/a", "a/b/a", "a/c/a"]
        self._test_range(start, stop, expected)

    def test_middle_range(self):
        start = "a/b"
        stop = "a/d"
        expected = ["a/b/a", "a/c/a", "a/d/a"]
        self._test_range(start, stop, expected)

    def test_late_range(self):
        start = "a/c"
        stop = "a/e"
        expected = ["a/c/a", "a/d/a", "a/e/a"]
        self._test_range(start, stop, expected)

    def test_no_matcing_range(self):
        start = "a/f"
        stop = "a/g"
        expected = []
        self._test_range(start, stop, expected)


class Test_datetime_to_url(unittest.TestCase):
    """Test gd.utils.datetime_to_url"""

    def test_dt(self):
        expected = "year_1984/month_07/day_02/"
        dt = stub(year=1984, month=7, day=2)
        actual = utils.datetime_to_url(dt)
        self.assertEqual(actual, expected)


class Test_create_date(unittest.TestCase):
    """Test gd.utils.create_date"""

    def test_create(self):
        actual = utils.create_date("July 2, 1984")
        self.assertEqual(actual, date(1984, 7, 2))

    def test_create_empty(self):
        actual = utils.create_date("")
        self.assertEqual(actual, date.min)


class Test_create_datetime(unittest.TestCase):
    """Test gd.utils.create_datetime"""

    def test_create_datetime(self):
        actual = utils.create_datetime("1984-07-02T12:34:56Z")
        self.assertEqual(actual, datetime(1984, 7, 2, 12, 34, 56))

    def test_create_datetime_empty(self):
        actual = utils.create_datetime("")
        self.assertEqual(actual, datetime.min)


class Test_create_time(unittest.TestCase):
    """Test gd.utils.create_time"""

    def test_create_time1(self):
        actual = utils.create_time("123456")
        self.assertEqual(actual, time(12, 34))

    def test_create_time2(self):
        actual = utils.create_time("12:34")
        self.assertEqual(actual, time(12, 34))

    def test_create_time3(self):
        actual = utils.create_time("1234")
        self.assertEqual(actual, time(12, 34))

    def test_create_time_empty(self):
        actual = utils.create_time("")
        self.assertEqual(actual, time.min)


@patch("logging.StreamHandler")
@patch("gd.utils.RotatingFileHandler")
class Test_enable_logging(unittest.TestCase):
    """Test gd.utils.enable_logging"""

    @patch("os.getenv")
    def test_debug(self, mock_getenv, mock_RFH, mock_SH):
        mock_getenv.return_value = "DEBUG"
        logger = utils.enable_logging()
        self.assertEqual(logger.level, logging.DEBUG)

    @patch("os.getenv")
    def test_regular(self, mock_getenv, mock_RFH, mock_SH):
        mock_getenv.return_value = False
        logger = utils.enable_logging()
        self.assertEqual(logger.level, logging.INFO)
