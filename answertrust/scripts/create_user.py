"""Create a reviewer or administrator account."""

import argparse
from getpass import getpass

from src.auth import create_user
from src.db import create_database_engine, create_session_factory, session_scope


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--role", choices=["REVIEWER", "ADMIN"], required=True)
    args = parser.parse_args()
    password = getpass("Password (10+ characters): ")
    factory = create_session_factory(create_database_engine())
    with session_scope(factory) as session:
        user = create_user(session, args.email, password, args.role)
    print(f"Created {user.role.lower()} account for {user.email}.")


if __name__ == "__main__":
    main()
