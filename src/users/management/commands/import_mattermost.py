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


class Command(BaseCommand):
    # Show this when the user types help
    help = "Mass creates users from Mattermost CSV file, modifies ID if necessary."

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

            id;username
            1;user1.user@local.net
            2;user2.user@local.net
 
        the headers are read from the CSV
        date_joined will be set by Django
        the password is a random string, but we'll throw that away because they'll be notified anyway
        phone number won't be set if I can avoid it...
        """

        def create_sso_user(row):
            ssouser, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "id": row["id"],
                    "first_name": first_name,
                    "last_name": last_name,
                    "password": make_password(get_random_string()),
                    "user_type": "USER",
                    "is_superuser": False,
                    "is_staff": False,
                    "is_active": False,
                    "unixlogin": False,
                },
            )

            return ssouser, created

        for row in DictReader(csvfile, delimiter=";"):
            user_id = int(row["id"].strip())
            email = row["username"].strip()

            """
            if there is no dot, no @ or the email doesn't include emaildomain, skip.
            """
            if "." not in email:
                print("skipping potential user {}".format(email))
                continue
            elif "emaildomain" not in email:
                print("skipping potential user {}".format(email))
                continue
            elif "@" not in email:
                print("skipping potential user {}".format(email))
                continue
            else:
                pass

            try:
                whole_name, domain = email.split("@")
                first_name, last_name = whole_name.split(".", 1)  # only split once
            except Exception as e:
                print("error with {}: {} (skipping)".format(row["username"], e))
            else:
                ssouser, created = create_sso_user(row)

                if ssouser.pk != int(row["id"]):
                    print("recreating user, wrong ID: {}".format(ssouser))
                    ssouser.delete()
                    ssouser, created = create_sso_user(row)

                if ssouser.is_active:
                    if not ssouser.phone:
                        print(
                            "\tno phone number, setting inactive. {}".format(
                                ssouser.phone
                            )
                        )
                        ssouser.is_active = False
                else:
                    # print("\tuser inactive, resetting password")
                    # ssouser.password=make_password(get_random_string())
                    pass

                print("saving user {}".format(ssouser))
                ssouser.save()

        users = User.objects.all()
        for user in users:
            user.first_name = user.first_name.title()
            user.last_name = user.last_name.title()

            if user.is_active:
                if user.phone:
                    pass
                else:
                    user.is_active = False
                    print(
                        "deactivating user {}, has no phone: {}".format(
                            user, user.phone
                        )
                    )

            user.save()
