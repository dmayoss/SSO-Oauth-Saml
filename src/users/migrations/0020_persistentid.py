# Generated by Django 3.2.17 on 2023-02-16 13:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0019_remove_customuser_unixname"),
    ]

    operations = [
        migrations.CreateModel(
            name="PersistentId",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "persistent_id",
                    models.CharField(
                        blank=True,
                        max_length=254,
                        null=True,
                        verbose_name="SAML Persistent Stored ID",
                    ),
                ),
                (
                    "recipient_id",
                    models.CharField(
                        blank=True,
                        max_length=254,
                        null=True,
                        verbose_name="SAML ServiceProvider entityID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Persistent Id",
                "verbose_name_plural": "Persistent Id",
            },
        ),
    ]
