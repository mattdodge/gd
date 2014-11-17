import configparser
import io

from libcloud.storage.providers import get_driver as get_storage_driver
from libcloud.storage.types import ContainerDoesNotExistError


def get_driver(config="/usr/local/etc/gd/storage.conf"):
    parser = configparser.ConfigParser()
    if parser.read(config):
        provider = parser.get("storage", "provider")
        username = parser.get("storage", "username")
        api_key = parser.get("storage", "api_key")
        region = parser.get("storage", "region")
    else:
        raise Exception("Unable to read storage configuration")

    Driver = get_storage_driver(provider)
    return Driver(username, api_key, region=region)


def get_container(driver, container_name):
    """Get or create a container."""
    try:
        return driver.get_container(container_name)
    except ContainerDoesNotExistError:
        return driver.create_container(container_name)


def upload_object(driver, container, object_name, data):
    """Upload an object through libcloud.storage's upload_object_via_stream."""

    if not getattr(data, "__next__", False):
        data = io.BytesIO(data)

    return driver.upload_object_via_stream(data, container, object_name)
