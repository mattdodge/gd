from datetime import datetime
import imp
import importlib
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


class Test_setup_logging(unittest.TestCase):

    def setUp(self):
        self.utils = importlib.import_module("gd.utils")

    def tearDown(self):
        del self.utils
        imp.reload(logging)

    def test_default(self):
        log = self.utils.setup_logging()

        self.assertEqual(log.name, "gd")
        self.assertEqual(len(log.handlers), 1)
        self.assertEqual(type(log.handlers[0]), logging.StreamHandler)
        self.assertFalse(log.isEnabledFor(logging.DEBUG))
        self.assertTrue(log.isEnabledFor(logging.INFO))

    def test_with_file(self):
        file_name = "test.log"
        log = self.utils.setup_logging(file_name)

        self.assertEqual(log.name, "gd")
        self.assertEqual(len(log.handlers), 2)
        self.assertCountEqual([type(x) for x in log.handlers],
                              [logging.StreamHandler, logging.FileHandler])
        self.assertFalse(log.isEnabledFor(logging.DEBUG))
        self.assertTrue(log.isEnabledFor(logging.INFO))


class Test_datetime_to_url(unittest.TestCase):
    """Test gd.scrape.datetime_to_url"""

    def test_dt(self):
        expected = "year_1984/month_07/day_02/"
        dt = stub(year=1984, month=7, day=2)
        actual = utils.datetime_to_url(dt)
        self.assertEqual(actual, expected)
