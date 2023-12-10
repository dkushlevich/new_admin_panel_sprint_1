

class BaseError(Exception):

    def __str__(self) -> str:
        return f"{self.MESSAGE}"


class SQLiteReadError(BaseError):
    MESSAGE = "Ошибка считывания данных из базы SQLite"


class DataClassConversionError(BaseError):
    MESSAGE = (
        "Ошибка прeобразования считанных данных в объекты классов данных. "
        "Пожалуйста, проверьте корректность названий полей."
    )

class PostgreSQLWriteError(BaseError):
    MESSAGE = "Ошибка записи данных в базу PostgreSQL"
