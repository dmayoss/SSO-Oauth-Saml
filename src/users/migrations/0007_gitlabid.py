# Generated by Django 3.0.14 on 2022-05-27 09:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_remove_customuser_nickname"),
    ]

    operations = [
        migrations.CreateModel(
            name="GitlabId",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("gitlab_id", models.IntegerField(default="10000", unique=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Gitlab ID's",
            },
        ),
    ]