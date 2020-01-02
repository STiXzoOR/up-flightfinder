import os
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
    "DB_HOST": args.database_host if args.database_host else "localhost",
    "DB_USER": args.database_user if args.database_user else "root",
    "DB_PASSWORD": args.database_password
    if args.database_password
    else "root"
    if OSX
    else "",
    "DEBUG_STATUS": "True",
    "SECRET_KEY": secrets.token_urlsafe(24),
}

with open(".env", "w") as dotenv:
    for key, value in VARS.items():
        dotenv.write('{key}="{value}"\n'.format(key=key, value=value))
