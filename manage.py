# manage.py
# Author: Indrajit Ghosh
# Created On: Feb 04, 2024
#

from flask import current_app
from flask.cli import FlaskGroup
from app.extensions import db
from app.models.user import User
from app.utils.database_helpers import update_page_content_hashes
import getpass

cli = FlaskGroup(current_app)

@cli.command("update_hashes")
def update_hashes():
    """
    Command-line utility to update the page_content_hash for MonitoredAd records.

    This command calculates and updates the page_content_hash for MonitoredAd records
    with a None value.

    Usage:
        python manage.py update_page_content_hashes

    Returns:
        None
    """
    with current_app.app_context():
        update_page_content_hashes()

@cli.command("all_users")
def all_users():
    """
    Command-line utility to retrieve and print all users' email addresses.

    This command queries the database and prints the email addresses of all registered users.

    Usage:
        python manage.py all_users

    Example:
        $ python manage.py all_users
        user1@example.com
        user2@example.com
        ...

    Returns:
        None
    """
    with current_app.app_context():
        users = User.query.all()
        for user in users:
            print(user.nickname, user.email, user.is_admin)


@cli.command("create_admin")
def create_admin():
    """Creates the admin user."""
    # TODO: Add some password protection here!
    fullname = input("Enter fullname: ")
    email = input("Enter email address: ")
    nickname = input("Enter a nickname (optional): ")
    telegram = input("Enter your telegram id (optional): ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Enter password again: ")
    if password != confirm_password:
        print("Passwords don't match")
    else:
        try:
            user = User(
                fullname=fullname,
                nickname=nickname,
                email=email,
                telegram=telegram,
                is_admin=True
            )
            user.set_hashed_password(password)
            user.set_nickname()

            db.session.add(user)
            db.session.commit()
            print(f"Admin with email {email} created successfully!")
        except Exception as e:
            print("Couldn't create admin user.")
            print(f"\nERROR: {e}")


if __name__ == '__main__':
    cli()
