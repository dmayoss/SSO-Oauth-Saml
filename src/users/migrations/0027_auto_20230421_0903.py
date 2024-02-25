# Generated by Django 3.2.18 on 2023-04-21 09:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0026_privacyagreement"),
    ]

    operations = [
        migrations.AddField(
            model_name="privacyagreement",
            name="verified",
            field=models.BooleanField(default=False, verbose_name="Agreement Verified"),
        ),
        migrations.AlterField(
            model_name="privacyagreement",
            name="agreement",
            field=models.BooleanField(default=False, verbose_name="Agreement Accepted"),
        ),
    ]
