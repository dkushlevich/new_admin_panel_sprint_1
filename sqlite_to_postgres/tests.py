import datetime as dt
import sqlite3

from psycopg2.extensions import connection as _connection


class TestLoadData:

    def __init__(
            self,
            sqlite_conn: sqlite3.Connection,
            pg_conn: _connection,
            table_names: list[str],
    ):
        self.sqlite_conn = sqlite_conn
        self.pg_conn = pg_conn
        self.table_names = table_names

    def __test_count_rows(self):
        """Проверяет равенство количества строк в таблицах
        баз данных SQLite и PostgreSQL.
        """
        sqlite_cursor = self.sqlite_conn.cursor()
        pg_cursor = self.pg_conn.cursor()
        for table_name in self.table_names:
            query = f"SELECT COUNT(id) FROM {table_name};"  # noqa: S608
            sqlite_cursor.execute(query)
            pg_cursor.execute(query)
            assert sqlite_cursor.fetchone()[0] == pg_cursor.fetchone()[0], (
                f"Количество данных в таблице {table_name} различается для "
                "баз данных SQLite и PostgreSQL"
            )

    def __test_equivalent_data(self):
        """Проверяет идентичность строк в таблицах
        баз данных SQLite и PostgreSQL.
        """
        sqlite_cursor = self.sqlite_conn.cursor()
        pg_cursor = self.pg_conn.cursor()

        for table_name in self.table_names:
            query = f"SELECT * FROM {table_name};" # noqa: S608

            sqlite_cursor.execute(query)
            sqlite_execute_result = sqlite_cursor.fetchall()
            time_fields = ("created_at", "updated_at")
            sqlite_data = {
                  row["id"]: {
                    key: dt.datetime.strptime(
                        value + "00", "%Y-%m-%d %H:%M:%S.%f%z",
                    )
                    if key in  time_fields else value
                    for key, value in dict(row).items()
                }
                for row in sqlite_execute_result
            }

            pg_cursor.execute(query)
            pg_execute_result = pg_cursor.fetchall()
            pg_data = {row["id"]: dict(row) for row in pg_execute_result}

            assert sqlite_data == pg_data, (
                f"Данные в таблицах {table_name} баз PostgreSQL и SQLite "
                "не совпадают"
            )

    def __call__(self):
        self.__test_count_rows()
        self.__test_equivalent_data()
