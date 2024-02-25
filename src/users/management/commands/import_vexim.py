import argparse
from csv import DictReader

# load extended user model
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils.crypto import (
    get_random_string,
)  # we'll use this one to set a random password (won't be used)

User = get_user_model()


"""
Create Table: CREATE TABLE `users_customuser` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` varchar(128) NOT NULL,
  `unixlogin` tinyint(1) NOT NULL,
  `unixname` varchar(64) DEFAULT NULL,
  `user_type` varchar(16) NOT NULL,
  `alt_email` varchar(254) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `unixname` (`unixname`),
  UNIQUE KEY `alt_email` (`alt_email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1
"""


class Command(BaseCommand):
    # Show this when the user types help
    help = "Mass creates users from Vexim CSV file."

    def add_arguments(self, parser):
        # parser.add_argument('csvfile', type=argparse.FileType('r'), help='CSV file with the users to be created')
        parser.add_argument("csvfile", type=str)

    def handle(self, *args, **kwargs):
        csvfile = kwargs["csvfile"]

        # Show this before loading the data into the database
        print("Loading User Data\n")

        """
        Code to load the user data into database
        CSV file should have the following structure:

            user_id;localpart;enabled;username;realname
            806;postmaster;1;postmaster@email.com;Domain Admin
 
        the headers are read from the CSV
        date_joined will be set by Django
        the password is a random string, but we'll throw that away because they'll be notified anyway
        phone number won't be set if I can avoid it...
        """
        try:
            with open(csvfile, encoding="utf-8-sig", errors="ignore") as f:
                for row in DictReader(f, delimiter=";"):
                    email = row["username"].strip()
                    full_name = row["realname"].strip()
                    is_active = row["enabled"].strip()
                    localpart = row["localpart"].strip()

                    """
                    if there is no dot, no @ or the email doesn't include email, skip.
                    """

                    if "." not in localpart:
                        print("skipping entry {}".format(email))
                        continue
                    elif "email" not in email:
                        print("skipping entry {}".format(email))
                        continue
                    else:
                        # print("processing potential user {}".format(email))
                        pass

                    first_name, last_name = localpart.split(".", 1)
                    first_name = first_name.capitalize()
                    last_name = last_name.replace(".", " ").title()

                    ssouser, created = User.objects.get_or_create(
                        email=email,
                        defaults={
                            "first_name": first_name,
                            "last_name": last_name,
                            "password": make_password(get_random_string()),
                            "user_type": "USER",
                            "is_superuser": False,
                            "is_staff": False,
                            "is_active": is_active,
                            "unixlogin": False,
                        },
                    )

                    if created:
                        print("User '{}' created.".format(ssouser))
                    else:
                        if (is_active != "1") and ("RET" not in ssouser.user_type):
                            ssouser.user_type = "RETIRED"
                            print("User '{}' inactive, set RETIRED.".format(ssouser))

                    ssouser.save()
        except Exception as e:
            print("error: {}".format(e))
