#! /usr/bin/env python

from setuptools import setup

setup(name="gameday",
      version="0.0.0",
      description="Tools for working with MLB's Gameday data",
      author="Brian Curtin",
      author_email="brian@python.org",
      packages=["gd",
                "gd.scripts"],
      install_requires=["requests"],
      test_suite="gd.tests",
     )
