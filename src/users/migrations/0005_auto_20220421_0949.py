# Generated by Django 3.0.14 on 2022-04-21 09:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_auto_20220413_0735"),
    ]

    operations = [
        migrations.RenameField(
            model_name="apppasswords",
            old_name="userid",
            new_name="username",
        ),
        migrations.AddField(
            model_name="apppasswords",
            name="itr",
            field=models.IntegerField(default="10000"),
        ),
    ]
