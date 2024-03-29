# Generated by Django 3.2.15 on 2022-09-09 14:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0013_alter_apppasswords_app"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="apppasswords",
            options={"verbose_name_plural": "Application Passwords"},
        ),
        migrations.RenameField(
            model_name="apppasswords",
            old_name="itr",
            new_name="iter",
        ),
        migrations.AddField(
            model_name="apppasswords",
            name="application",
            field=models.CharField(
                blank=True,
                choices=[
                    ("NEXTCLOUD", "Nextcloud"),
                    ("EMAIL", "Email"),
                    ("GITLAB", "Gitlab"),
                ],
                max_length=64,
                verbose_name="Application",
            ),
        ),
        migrations.AlterField(
            model_name="apppasswords",
            name="username",
            field=models.CharField(
                blank=True, max_length=64, verbose_name="Application Username"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="apppasswords",
            unique_together={("user", "application")},
        ),
        migrations.DeleteModel(
            name="GitlabId",
        ),
        migrations.RemoveField(
            model_name="apppasswords",
            name="app",
        ),
        migrations.RemoveField(
            model_name="apppasswords",
            name="key",
        ),
    ]
