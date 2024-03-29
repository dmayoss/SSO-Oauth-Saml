# Generated by Django 3.2.15 on 2022-09-08 06:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0011_auto_20220908_0554"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="userrolemap",
            options={"verbose_name_plural": "User Departments and Roles"},
        ),
        migrations.AddField(
            model_name="customuser",
            name="user_type",
            field=models.CharField(
                choices=[
                    ("USER", "Normal User"),
                    ("HR", "HR User"),
                    ("HOSTING", "Hosting User"),
                ],
                default="USER",
                max_length=16,
                verbose_name="User Type",
            ),
        ),
    ]
