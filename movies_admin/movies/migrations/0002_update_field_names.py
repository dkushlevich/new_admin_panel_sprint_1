# Generated by Django 4.2.5 on 2023-12-09 16:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=('''
                ALTER TABLE "content"."film_work"
                ADD COLUMN file_path VARCHAR;

                ALTER TABLE "content"."film_work"
                RENAME COLUMN modified TO updated_at;
                
                ALTER TABLE "content"."film_work"
                RENAME COLUMN created TO created_at;

                ALTER TABLE "content"."genre"
                RENAME COLUMN created TO created_at;
                
                ALTER TABLE "content"."genre"
                RENAME COLUMN modified TO updated_at;

                ALTER TABLE "content"."person"
                RENAME COLUMN created TO created_at;
                
                ALTER TABLE "content"."person"
                RENAME COLUMN modified TO updated_at;

                ALTER TABLE "content"."genre_film_work"
                RENAME COLUMN created TO created_at;
                
                ALTER TABLE "content"."person_film_work"
                RENAME COLUMN created TO created_at;
                
                DROP INDEX IF EXISTS film_work_person_idx;
            '''
            ),
            reverse_sql=('''
                ALTER TABLE "content"."film_work"
                RENAME COLUMN created_at TO created;

                ALTER TABLE "content"."film_work"
                RENAME COLUMN updated_at TO modified;

                ALTER TABLE "content"."genre"
                RENAME COLUMN created_at TO created;

                ALTER TABLE "content"."genre"
                RENAME COLUMN updated_at TO modified;
                
                ALTER TABLE "content"."person"
                RENAME COLUMN created_at TO created;
                
                ALTER TABLE "content"."person"
                RENAME COLUMN updated_at TO modified;

                ALTER TABLE "content"."genre_film_work"
                RENAME COLUMN created_at TO created;
                
                ALTER TABLE "content"."person_film_work"
                RENAME COLUMN created_at TO created;

                CREATE UNIQUE INDEX film_work_person_idx ON content.person_film_work (film_work_id, person_id);
            '''
            )
        )
    ]
