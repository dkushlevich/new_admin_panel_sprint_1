import logging  # noqa: I001
import os
import sqlite3
import sys
from dataclasses import astuple, fields
from pathlib import Path

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

from exceptions import (
    DataClassConversionError,
    PostgreSQLWriteError,
    SQLiteReadError,
)
from managers import open_sqlite_db, open_postgres_db
from models import (
    FilmWork,
    Genre,
    GenreFilmWork,
    Person,
    PersonFilmWork,
)
from tests import TestLoadData


load_dotenv()

BATCH_SIZE: str | None = os.getenv("BATCH_SIZE")

SQLITE_DB_NAME: str = os.getenv("SQLITE_DB_NAME")

DSL: dict = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

TABLE_NAMES_DATACLASSES: dict = {
        "film_work": FilmWork,
        "genre": Genre,
        "person": Person,
        "genre_film_work": GenreFilmWork,
        "person_film_work": PersonFilmWork,
}


class SQLiteExtractor:

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def extract_data(self, table_name: str):
        """Считывает данные из базы SQLite."""
        dataclass = TABLE_NAMES_DATACLASSES.get(table_name)
        current_position = 0

        while True:
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            sql_query = f"""
                SELECT * FROM {table_name}
                LIMIT {BATCH_SIZE}
                OFFSET {current_position};
            """  # noqa: S608

            try:
                cursor.execute(sql_query)
            except sqlite3.Error as exc:
                raise SQLiteReadError() from exc  # noqa: RSE102
            data = cursor.fetchall()

            if not data:
                break

            try:
                yield [dataclass(**dict(row_data)) for row_data in data]
            except TypeError as exc:
                raise DataClassConversionError() from exc  # noqa: RSE102

            current_position += int(BATCH_SIZE)


class PostgresSaver:

    def __init__(self, pg_connection: _connection):
       self.pg_connection = pg_connection

    def save_all_data(self, data: dict, table_name: str):
        """Сохраняет данные в базу PostgreSQL."""

        column_names = [field.name for field in fields(data[0])]
        column_names_str = ",".join(column_names)
        col_count = ", ".join(["%s"] * len(column_names))

        pg_cursor = self.pg_connection.cursor()

        bind_values = ",".join(pg_cursor.mogrify(
            f"({col_count})",
            astuple(row)).decode("utf-8") for row in data
        )
        query = (
            f"INSERT INTO {table_name} ({column_names_str}) VALUES "  # noqa: S608
            f"{bind_values} ON CONFLICT (id) DO NOTHING"
        )

        try:
            execute_batch(pg_cursor, query, [])
        except sqlite3.Error as exc:
            raise PostgreSQLWriteError() from exc  # noqa: RSE102


def load_from_sqlite_to_postgresql(
        connection: sqlite3.Connection,
        pg_connection: _connection,
):
    """Загружает данные из SQLite в Postgres."""
    postgres_saver = PostgresSaver(pg_connection)
    sqlite_extractor = SQLiteExtractor(connection)

    for table_name in TABLE_NAMES_DATACLASSES:

        for data in sqlite_extractor.extract_data(table_name):
            postgres_saver.save_all_data(data, table_name)

        logger.info(f"Transfer data for table {table_name} success")

    logger.info("PostgeSQL write data success")


def check_db_file_exists(db_path: str):
    """Проверяет существование файла c исходной базой данных."""
    if not Path.exists(db_path):
        raise FileNotFoundError(
            "Неверно указан путь к файлу с базой данных SQLite",
        )


def check_variables():
    """Проверяет доступность необходимых переменных окружения."""
    variables = {
        "SQLITE_DB_NAME": SQLITE_DB_NAME,
        "BATCH_SIZE": BATCH_SIZE,
        "DB_NAME": DSL.get("dbname"),
        "DB_USER": DSL.get("user"),
        "DB_PASSWORD": DSL.get("password"),
        "DB_HOST": DSL.get("host"),
        "DB_PORT": DSL.get("port"),
    }
    missing_variables = list(
        filter(lambda variable: not variables[variable], variables),
    )
    if missing_variables:
        missing_variables_str = ", ".join(missing_variables)
        raise ValueError(
            f"Не найдены переменные окружения: {missing_variables_str}",
        )


def check_batch_size_type():
    """Проверяет корректность типа переменной окружения
    BATCH_SIZE.
    """
    try:
        int(BATCH_SIZE)
    except ValueError as exc:
        raise ValueError(
            "Неверный тип переменной BATCH_SIZE. "
            f"Невозможно преобразовать {BATCH_SIZE} в int",
        ) from exc


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s, %(levelname)s, %(message)s, "
            "%(lineno)s"
        ),
        stream=sys.stdout,
    )

    logger = logging.getLogger(__name__)

    file_handler = logging.FileHandler(
        Path(__file__).resolve().parent / "load_data.log",
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
    )
    file_handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    logger.info("Script running")

    db_path = (Path(__file__).resolve().parent / SQLITE_DB_NAME)

    try:
        check_db_file_exists(db_path)
        check_variables()
        check_batch_size_type()
    except FileNotFoundError:
        logger.exception("SQLite database file not found")
    except ValueError:
        logger.exception("Environment variable error")
    else:
        try:
            with (
                open_sqlite_db(db_path) as sqlite_conn,
                open_postgres_db(DSL) as pg_conn,
            ):
                logger.info(
                    "SQLite and PostgreSQL connect success",
                )

                try:

                    load_from_sqlite_to_postgresql(sqlite_conn, pg_conn)

                    table_names = TABLE_NAMES_DATACLASSES.keys()
                    test_load_data = TestLoadData(
                        sqlite_conn,
                        pg_conn,
                        table_names,
                    )
                    test_load_data()
                    logger.info("Tests passed")


                except SQLiteReadError as exc:
                    raise SQLiteReadError from exc
                except DataClassConversionError as exc:
                    raise DataClassConversionError from exc
                except PostgreSQLWriteError as exc:
                    raise PostgreSQLWriteError from exc
                except AssertionError as exc:
                    raise AssertionError from exc

            logger.info("Databases connection closed")

        except psycopg2.Error:
            logger.exception("PostgreSQL connection error")

        except sqlite3.Error:
            logger.exception("SQLite connection error")

        except SQLiteReadError:
            logger.exception("SQLite reading error")

        except DataClassConversionError:
            logger.exception("Readed data dataclass conversion failed")

        except PostgreSQLWriteError:
            logger.exception("PostgreSQL write data error")

        except AssertionError:
            logger.exception("Tests failed")

    finally:
        logger.info("Script completed")
