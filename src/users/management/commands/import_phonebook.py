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
    help = "creates SSO users from the phonebook csv export, updates entries where possible (e.g. phone number)."

    def add_arguments(self, parser):
        parser.add_argument(
            "csvfile",
            type=argparse.FileType("r"),
            help="CSV file with the users to be created",
        )

    def handle(self, *args, **kwargs):
        csvfile = kwargs["csvfile"]

        # Show this before loading the data into the database
        print("Loading User Data")

        """
        Code to load the user data into database
        CSV file should have the following structure:

            first_name;last_name;email;phone
            user1 ; user ; user1.user@local.net ; +123456789
            user2 ; user ; user2.user@local.net ; +123456789
 
        the headers are read from the CSV
        date_joined will be set by Django
        the password is a random string, but we'll throw that away because they'll be notified anyway
        """

        for row in DictReader(csvfile, delimiter=";"):
            try:
                full_name = row["Name"].strip()
                first_name, last_name = full_name.split(" ", 1)
                first_name = first_name.capitalize()
                last_name = last_name.replace(".", " ").title()

                if "/" in row["GSM"]:
                    phone_list = row["GSM"].strip().split("/")
                    phone = phone_list[1].strip()
                else:
                    phone = row["GSM"].strip()

                ssouser, created = User.objects.get_or_create(
                    email=row["email"].strip(),
                    defaults={
                        "first_name": first_name,
                        "last_name": last_name,
                        "phone": phone,
                        "password": make_password(get_random_string()),
                        "user_type": "USER",
                        "is_superuser": False,
                        "is_staff": False,
                        "is_active": False,
                        "unixlogin": False,
                    },
                )
            except Exception as e:
                print("error creating user: {}".format(e))
            else:
                if created:
                    print("User '{}' created.".format(ssouser))
                else:
                    if ssouser.phone != phone:
                        ssouser.phone = phone
                        print(
                            "\tupdated phone number for {} to {}".format(ssouser, phone)
                        )
                    if ssouser.first_name != first_name:
                        ssouser.first_name = first_name
                        print(
                            "\tupdated first_name for {} to {}".format(
                                ssouser, first_name
                            )
                        )
                    if ssouser.last_name != last_name:
                        ssouser.last_name = last_name
                        print(
                            "\tupdated last_name for {} to {}".format(
                                ssouser, last_name
                            )
                        )

                    ssouser.save()
