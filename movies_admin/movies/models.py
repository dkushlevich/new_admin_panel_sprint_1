import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class FilmWorkType(models.TextChoices):
    MOVIE = "movie", _("movie")
    TV_SHOW = "tv_show", _("tv_show")


class PersonRole(models.TextChoices):
    ACTOR = "actor", _("actor")
    DIRECTOR = "director", _("director")
    WRITER = "writer", _("writer")


class TimeStampedMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(_("creation time"), auto_now_add=True)
    modified = models.DateTimeField(_("modification time"), auto_now=True)

    class Meta:
        abstract=True

class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        db_table = "content\".\"genre"  # noqa: Q003
        verbose_name = _("genre")
        verbose_name_plural = _("genres")

    def __str__(self):
        return self.name

class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_("full_name"), max_length=255)

    class Meta:
        db_table = "content\".\"person"  # noqa: Q003
        verbose_name = _("person")
        verbose_name_plural = _("persons")

    def __str__(self):
        return self.full_name


class FilmWork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    creation_date = models.DateField(_("release date"))
    rating = models.FloatField(
        _("rating"),
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    type = models.CharField(
        _("type"),
        max_length=max(len(role) for role, _ in FilmWorkType.choices),
        choices=FilmWorkType.choices,
        default=FilmWorkType.MOVIE,
    )
    genres = models.ManyToManyField(
        Genre,
        through="GenreFilmWork",
        related_name="film_works",
    )
    persons = models.ManyToManyField(
        Person,
        through="PersonFilmWork",
        related_name="film_works",
    )

    class Meta:
        db_table = "content\".\"film_work"  # noqa: Q003
        verbose_name = _("film work")
        verbose_name_plural = _("film works")

    def __str__(self):
        return self.title


class GenreFilmWork(UUIDMixin, TimeStampedMixin):
    film_work = models.ForeignKey(
        FilmWork,
        on_delete=models.CASCADE,
        related_name="genre_film_works",
        verbose_name=_("film work"),
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name="genre_film_works",
        verbose_name=_("genre"),
    )

    modified = None

    class Meta:
        db_table = "content\".\"genre_film_work" # noqa: Q003


class PersonFilmWork(UUIDMixin, TimeStampedMixin):

    film_work = models.ForeignKey(
        FilmWork,
        on_delete=models.CASCADE,
        related_name="person_film_works",
        verbose_name=_("film work"),
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="person_film_works",
        verbose_name=_("person"),
    )
    role = models.CharField(
        "Роль",
        max_length=max(len(role) for role, _ in PersonRole.choices),
        choices=PersonRole.choices,
        default=PersonRole.ACTOR,
    )

    modified = None

    class Meta:
        db_table = "content\".\"person_film_work" # noqa: Q003
