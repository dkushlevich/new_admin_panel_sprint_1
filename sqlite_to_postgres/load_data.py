import logging  # noqa: I001
import os
import sqlite3
import sys
from dataclasses import astuple, fields
from pathlib import Path

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

from exceptions import (
    DataClassConversionError,
    PostgreSQLWriteError,
    SQLiteReadError,
)
from models import (
    FilmWork,
    Genre,
    GenreFilmWork,
    Person,
    PersonFilmWork,
)
from tests import TestLoadData


load_dotenv()

ROW_COUNT_RESRICT: str | None = os.getenv("ROW_COUNT_RESTRICT")

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
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        sql_query = f"SELECT * FROM {table_name};"  # noqa: S608
        try:
            cursor.execute(sql_query)
        except sqlite3.Error as exc:
            raise SQLiteReadError() from exc  # noqa: RSE102
        data = cursor.fetchall()
        dataclass = TABLE_NAMES_DATACLASSES.get(table_name)
        try:
            return [dataclass(**dict(row_data)) for row_data in data]
        except TypeError as exc:
            raise DataClassConversionError() from exc  # noqa: RSE102


class PostgresSaver:

    def __init__(self, pg_connection: _connection):
       self.pg_connection = pg_connection

    def save_all_data(self, data: dict, row_count_restrict: int | None=None):
        """Сохраняет данные в базу PostgreSQL."""
        for table_name in TABLE_NAMES_DATACLASSES:
            table_data = data.get(table_name)

            if not table_data:
                continue

            column_names = [field.name for field in fields(table_data[0])]
            column_names_str = ",".join(column_names)
            col_count = ", ".join(["%s"] * len(column_names))

            if not row_count_restrict:
                row_count_restrict = len(table_data)

            pg_cursor = self.pg_connection.cursor()

            for i in range(0, len(table_data), row_count_restrict):
                split_data = table_data[i:i + row_count_restrict]
                bind_values = ",".join(pg_cursor.mogrify(
                    f"({col_count})",
                    astuple(row)).decode("utf-8") for row in split_data
                )
                query = (
                    f"INSERT INTO {table_name} ({column_names_str}) VALUES "  # noqa: S608
                    f"{bind_values} ON CONFLICT (id) DO NOTHING"
                )
                try:
                    pg_cursor.execute(query)
                except sqlite3.Error as exc:
                    raise PostgreSQLWriteError() from exc  # noqa: RSE102


def load_from_sqlite_to_postgresql(
        connection: sqlite3.Connection,
        pg_connection: _connection,
):
    """Загружает данные из SQLite в Postgres."""
    postgres_saver = PostgresSaver(pg_connection)
    sqlite_extractor = SQLiteExtractor(connection)

    data_to_write = {}
    for table_name in TABLE_NAMES_DATACLASSES:
        data_to_write[table_name] = sqlite_extractor.extract_data(table_name)

    logger.info("Данные успешно извлечены из базы данных SQLite")
    row_count_restrict = int(ROW_COUNT_RESRICT)
    postgres_saver.save_all_data(data_to_write, row_count_restrict)

    logger.info("Данные успешно записаны в базу данных PostgreSQL")


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


def check_row_count_restrict_type():
    """Проверяет корректность типа переменной окружения
    ROW_COUNT_RESTRICT.
    """
    if ROW_COUNT_RESRICT:
        try:
            int(ROW_COUNT_RESRICT)
        except ValueError as exc:
            raise ValueError(
                "Неверный тип переменной ROW_COUNT_RESRICT. "
                f"Невозможно преобразовать {ROW_COUNT_RESRICT} в int",
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

    logger.info("Скрипт запущен")

    db_path = (Path(__file__).resolve().parent / SQLITE_DB_NAME)

    try:
        check_db_file_exists(db_path)
        check_variables()
        check_row_count_restrict_type()
    except FileNotFoundError:
        logger.exception("Файл с базой данных SQLite не найден")
    except ValueError:
        logger.exception("Ошибка переменной окружения")
    else:
        try:
            with sqlite3.connect(db_path) as sqlite_conn, psycopg2.connect(
                **DSL, cursor_factory=DictCursor,
            ) as pg_conn:
                logger.info(
                    "Соединение с SQLite и PostgreSQL установлено",
                )

                try:
                    pg_conn.autocommit = False

                    load_from_sqlite_to_postgresql(sqlite_conn, pg_conn)

                    table_names = TABLE_NAMES_DATACLASSES.keys()
                    test_load_data = TestLoadData(
                        sqlite_conn,
                        pg_conn,
                        table_names,
                    )
                    test_load_data()
                    logger.info("Тесты прошли успешно")

                    pg_conn.commit()

                except SQLiteReadError as exc:
                    raise SQLiteReadError from exc
                except DataClassConversionError as exc:
                    raise DataClassConversionError from exc
                except PostgreSQLWriteError as exc:
                    pg_conn.rollback()
                    raise PostgreSQLWriteError from exc
                except AssertionError as exc:
                    pg_conn.rollback()
                    raise AssertionError from exc
                finally:
                    pg_conn.autocommit = True

            logger.info("Соединение с SQLite и PostgreSQL закрыто")

        except psycopg2.Error:
            logger.exception("Ошибка подключения к базе данных PostgreSQL")

        except sqlite3.Error:
            logger.exception("Ошибка подключения к базе данных SQLite")

        except SQLiteReadError:
            logger.exception("Ошибка считывания данных из базы SQLite")

        except DataClassConversionError:
            logger.exception(
                "Ошибка преобразования считанных данных в "
                "объекты классов данных",
            )

        except PostgreSQLWriteError:
            logger.exception("Ошибка записи данных в базу PostgreSQL")

        except AssertionError:
            logger.exception(
                "Тесты выявили несоответствие, база PostgreSQL "
                "возвращена в исходный вид",
            )

    finally:
        logger.info("Скрипт завершил работу")
