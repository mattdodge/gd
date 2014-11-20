from unittest.mock import patch
import io
import unittest

from pretend import stub, raiser
from libcloud.storage.types import ContainerDoesNotExistError

from gd import storage


class Test_get_driver(unittest.TestCase):
    """Test gd.storage.get_driver"""

    @patch("configparser.ConfigParser.read")
    def test_bad_config(self, mock_read):
        mock_read.return_value = []

        with self.assertRaises(Exception):
            storage.get_driver()

    @patch("gd.storage.get_storage_driver")
    @patch("configparser.ConfigParser.get")
    @patch("configparser.ConfigParser.read")
    def test_good_config(self, mock_read, mock_get, mock_gsd):
        mock_read.return_value = True

        storage.get_driver()

        mock_get.assert_any_call("storage", "provider")
        mock_get.assert_any_call("storage", "username")
        mock_get.assert_any_call("storage", "api_key")
        mock_get.assert_any_call("storage", "region")


class Test_get_container(unittest.TestCase):
    """Test gd.storage.get_container"""

    def test_existing_container(self):
        driver = stub(get_container=lambda arg: arg)

        expected = "my_container"
        actual = storage.get_container(driver, expected)
        self.assertEqual(actual, expected)

    def test_new_container(self):
        exc = ContainerDoesNotExistError(1, 2, 3)
        driver = stub(get_container=raiser(exc),
                      create_container=lambda arg: arg)

        expected = "my_container"
        actual = storage.get_container(driver, expected)
        self.assertEqual(actual, expected)


class Test_upload_object(unittest.TestCase):
    """Test gd.storage.upload_object"""

    def _do_test(self, expected_data):
        driver = stub(upload_object_via_stream=lambda *args: args)

        actual = storage.upload_object(driver, "my_container",
                                       "my_object", expected_data)

        self.assertEqual(type(actual[0]), io.StringIO)
        self.assertEqual(actual[1], "my_container")
        self.assertEqual(actual[2], "my_object")

    def test_non_iterable(self):
        self._do_test("testing")

    def test_iterable(self):
        self._do_test(io.StringIO("testing"))
