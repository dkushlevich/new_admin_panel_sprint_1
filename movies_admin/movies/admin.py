from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    verbose_name = _("genre")
    verbose_name_plural = _("genres")
    extra = 0

class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    autocomplete_fields = ("person", )
    verbose_name = _("person")
    verbose_name_plural = _("persons")
    extra = 0

@admin.register(FilmWork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)

    list_display = (
        "title",
        "type",
        "creation_date",
        "get_genres",
        "rating",
    )
    list_filter = ("type", "rating")
    search_fields = ("title", "description", "id")
    list_prefetch_related = ("genres",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[FilmWork]:
        return (
            super()
            .get_queryset(request)
            .prefetch_related(*self.list_prefetch_related)
        )

    def get_genres(self, obj: FilmWork):
        return list(obj.genres.values_list("name", flat=True))



@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
   list_display = ("name",)
   search_fields = ("name", "id")

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = ("full_name", "id")
