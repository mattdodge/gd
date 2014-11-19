#! /usr/bin/env python

from setuptools import setup

setup(name="gameday",
      version="0.0.0",
      description="Tools for working with MLB's Gameday data",
      author="Brian Curtin",
      author_email="brian@python.org",
      packages=["gd",
                "gd.scripts"],
      scripts=["bin/gd-util"],
      data_files=[("/usr/local/etc/gd", ["config/db.conf.example",
                                         "config/storage.conf.example"])],
      install_requires=["requests",
                        "sqlalchemy",
                        "apache-libcloud"],
      test_suite="gd.tests",
      classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3 :: Only"]
     )
