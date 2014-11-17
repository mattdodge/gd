import configparser
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def _get_engine_uri():
    path = os.getenv("GD_DATABASE_URI", False)
    if path:
        return path

    path = "config/db.conf"
    parser = configparser.ConfigParser()
    if parser.read(path):
        return parser.get("connection", "uri")

    raise Exception("No database engine available")


engine = create_engine(_get_engine_uri(), convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
Base = declarative_base()
Base.query = session.query_property()


def init():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import gd.models
    Base.metadata.create_all(bind=engine)
