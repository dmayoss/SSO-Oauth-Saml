# Generated by Django 3.2.17 on 2023-02-21 14:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0020_persistentid"),
    ]

    operations = [
        migrations.RenameField(
            model_name="apppasswords",
            old_name="cert",
            new_name="pvt_crt",
        ),
        migrations.RemoveField(
            model_name="apppasswords",
            name="iter",
        ),
        migrations.RemoveField(
            model_name="apppasswords",
            name="salt",
        ),
        migrations.AddField(
            model_name="apppasswords",
            name="pvt_key",
            field=models.TextField(blank=True),
        ),
    ]
