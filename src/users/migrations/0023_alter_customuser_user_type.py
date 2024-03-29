# Generated by Django 3.2.18 on 2023-04-03 08:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0022_alter_customuser_user_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="user_type",
            field=models.CharField(
                choices=[
                    ("USER", "Normal User"),
                    ("HR", "HR User"),
                    ("HOSTING", "Hosting User"),
                    ("RETIRED", "Retired User"),
                    ("INTERNAL", "Internal (non-employee) User"),
                ],
                default="USER",
                max_length=16,
                verbose_name="User Type",
            ),
        ),
    ]
