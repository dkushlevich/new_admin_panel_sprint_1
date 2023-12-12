import logging
import sqlite3
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import DictCursor


@contextmanager
def open_sqlite_db(file_name: str):
    conn = sqlite3.connect(file_name)
    try:
        logging.info("SQlite creating connection")
        yield conn
    finally:
        logging.info("SQlite closing connection")
        conn.commit()
        conn.close()


@contextmanager
def open_postgres_db(dsl: dict):
    conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    try:
        logging.info("PostgreSQL creating connection")
        yield conn
    finally:
        logging.info("PostgreSQL closing connection")
        conn.commit()
        conn.close()
