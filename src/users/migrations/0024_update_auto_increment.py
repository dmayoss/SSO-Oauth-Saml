# Generated by Django 3.2.18 on 2023-04-03 09:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0023_alter_customuser_user_type"),
    ]

    operations = [
        migrations.RunSQL(
            " alter table users_customuser auto_increment=1001",
        )
    ]
