# Generated by Django 4.2.5 on 2023-12-06 13:31

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FilmWork',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modification time')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('creation_date', models.DateField(verbose_name='release date')),
                ('rating', models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='rating')),
                ('type', models.CharField(choices=[('movie', 'movie'), ('tv_show', 'tv_show')], default='movie', max_length=7, verbose_name='type')),
            ],
            options={
                'verbose_name': 'film work',
                'verbose_name_plural': 'film works',
                'db_table': 'content"."film_work',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modification time')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
            ],
            options={
                'verbose_name': 'genre',
                'verbose_name_plural': 'genres',
                'db_table': 'content"."genre',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modification time')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=255, verbose_name='full_name')),
            ],
            options={
                'verbose_name': 'person',
                'verbose_name_plural': 'persons',
                'db_table': 'content"."person',
            },
        ),
        migrations.CreateModel(
            name='PersonFilmWork',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('actor', 'actor'), ('director', 'director'), ('writer', 'writer')], default='actor', max_length=8, verbose_name='Роль')),
                ('film_work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='person_film_works', to='movies.filmwork', verbose_name='film work')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='person_film_works', to='movies.person', verbose_name='person')),
            ],
            options={
                'db_table': 'content"."person_film_work',
            },
        ),
        migrations.CreateModel(
            name='GenreFilmWork',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('film_work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genre_film_works', to='movies.filmwork', verbose_name='film work')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genre_film_works', to='movies.genre', verbose_name='genre')),
            ],
            options={
                'db_table': 'content"."genre_film_work',
            },
        ),
        migrations.AddField(
            model_name='filmwork',
            name='genres',
            field=models.ManyToManyField(related_name='film_works', through='movies.GenreFilmWork', to='movies.genre'),
        ),
        migrations.AddField(
            model_name='filmwork',
            name='persons',
            field=models.ManyToManyField(related_name='film_works', through='movies.PersonFilmWork', to='movies.person'),
        ),
    ]
