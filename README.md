[![Build Status](https://travis-ci.org/briancurtin/gd.svg?branch=master)](https://travis-ci.org/briancurtin/gd)

# About gd

Tools for working with http://gd2.mlb.com/components/game/mlb/

This is definitely a work in progress. Right now it consists of a scraper,
parser, and database storage. Building a REST API and analysis tools on
top of that is an end goal.

# Development

## Requirements

* [Python 3.4](https://www.python.org/download/releases/3.4.0)
* [tox](http://tox.readthedocs.org/en/latest/)

## Getting Setup

Development is easiest when you use
[virtualenv](http://www.virtualenv.org/en/latest/)

```
git clone git@github.com:yourusername/gd.git && cd gd/
virtualenv -p python3.4 ../envs/gd
source ../envs/gd/bin/activate
pip install tox
tox
...
Ran 51 tests in 0.038s
...
```
