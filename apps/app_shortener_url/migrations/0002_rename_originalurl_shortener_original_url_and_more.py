# Generated by Django 4.2.4 on 2023-08-25 11:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app_shortener_url", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="shortener",
            old_name="originalUrl",
            new_name="original_url",
        ),
        migrations.RemoveField(
            model_name="shortener",
            name="shortUrl",
        ),
        migrations.AddField(
            model_name="shortener",
            name="short_url",
            field=models.URLField(
                db_column="short_url", default="", max_length=100, null=True
            ),
        ),
    ]
