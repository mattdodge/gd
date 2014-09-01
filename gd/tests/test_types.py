from datetime import datetime
import unittest

from gd import types


class Test_transform(unittest.TestCase):
    """Test the gd.types.transform function."""

    def test_transform(self):
        actual = {"test1": "lol", "test2": "123", "test3": "0.1"}
        expected = {"test1": "lol", "test2": 123, "test3": 0.1}
        actual_types = {"test1": str, "test2": int, "test3": float}
        types.transform(actual, actual_types)
        self.assertEqual(actual, expected)

    def test_transform_bad_type(self):
        actual = {"test1": "lol"}
        actual_types = {"test1": int}
        self.assertRaises(ValueError, types.transform, actual, actual_types)


class Test_to_datetime(unittest.TestCase):
    """Test the gd.types._to_datetime function."""

    def test__to_datetime(self):
        args = 2013, 5, 1, 19, 38, 3
        # Build the format stored in MLB's XML.
        timestamp = "%04d-%02d-%02dT%02d:%02d:%02dZ" % args
        expected = datetime(*args)
        actual = types._to_datetime(timestamp)
        self.assertEqual(actual, expected)

    def test__to_datetime_no_Z(self):
        args = 2013, 5, 1, 19, 38, 3
        # If we don't get the expected timestamp, we'll end up cutting short.
        # Note that there is no `Z` at the end of this.
        timestamp = "%04d-%02d-%02dT%02d:%02d:%02d" % args
        self.assertRaises(ValueError, types._to_datetime, timestamp)
