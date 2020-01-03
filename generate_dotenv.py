import os
import sys
import secrets
import platform
import argparse

OSX = platform.system() == "Darwin"
parser = argparse.ArgumentParser()

parser.add_argument(
    "--db-host",
    metavar="host",
    type=str,
    action="store",
    help="database host to connect (default: localhost)",
)
parser.add_argument(
    "--db-user",
    metavar="username",
    type=str,
    action="store",
    help="database user to connect (default: root)",
)
parser.add_argument(
    "--db-password",
    metavar="password",
    type=str,
    action="store",
    help="database password to connect (default: {password})".format(
        password="root" if OSX else "None"
    ),
)

args = parser.parse_args()

VARS = {
    "DB_NAME": "flightfinderdb",
    "DB_HOST": args.db_host if args.db_host else "localhost",
    "DB_USER": args.db_user if args.db_user else "root",
    "DB_PASSWORD": args.db_password if args.db_password else "root" if OSX else "",
    "DEBUG_STATUS": "True",
    "SECRET_KEY": secrets.token_urlsafe(24),
}

with open(".env", "w") as dotenv:
    print("Generating .env file... ", end="")
    sys.stdout.flush()

    for key, value in VARS.items():
        dotenv.write('{key}="{value}"\n'.format(key=key, value=value))
    print("Done!")

