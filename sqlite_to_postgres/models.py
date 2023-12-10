import datetime as dt
import uuid
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class AbstractDataclass:

    def __new__(cls, *args, **kwargs):  # noqa: ANN003, ANN002, ARG003
        if cls == AbstractDataclass or cls.__bases__[0] == AbstractDataclass:
            raise TypeError("Cannot instantiate abstract class.")
        return super().__new__(cls)


@dataclass
class TimeStampedMixin(AbstractDataclass):
    created_at: dt.datetime
    updated_at: dt.datetime


@dataclass
class UUIDMixin(AbstractDataclass):
    id: uuid


@dataclass
class FilmWork(UUIDMixin, TimeStampedMixin):
    title: str
    file_path: str
    creation_date: dt.datetime
    description: str
    type: Literal["movie", "tv_show"]
    rating: float = field(default=0.0)


@dataclass
class Genre(UUIDMixin, TimeStampedMixin):
    name: str
    description: str

@dataclass
class Person(UUIDMixin, TimeStampedMixin):
    full_name: str

@dataclass
class GenreFilmWork(UUIDMixin):
    film_work_id: uuid
    genre_id: uuid
    created_at: dt.datetime

@dataclass
class PersonFilmWork(UUIDMixin):
    film_work_id: uuid
    person_id: uuid
    role: Literal["actor", "director", "writer"]
    created_at: dt.datetime
