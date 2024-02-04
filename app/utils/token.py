# app/auth/token.py
# 
# Author: Indrajit Ghosh
# Created On: Feb 04, 2024
#

from flask import current_app
from itsdangerous import URLSafeTimedSerializer

def get_token_for_email_registration(fullname:str, email: str):
    """
    Generate a URL-safe token for the given email using Flask's current app configuration.

    Parameters:
    - email (str): The email for which the token is generated.

    Returns:
    - str: The generated URL-safe token.
    """
    serializer = URLSafeTimedSerializer(
        secret_key=current_app.config['SECRET_KEY'], salt=current_app.config['SECURITY_PASSWORD_SALT']
    )
    return serializer.dumps(
        {'fullname': fullname, 'email': email}
    )


def confirm_email_registration_token(token: str, expiration: int = 3600):
    """
    Confirm the validity of a token and retrieve the associated email within the specified expiration time.

    Parameters:
    - token (str): The token to be confirmed.
    - expiration (int, optional): The expiration time for the token in seconds (default is 3600 seconds).

    Returns:
    - str: The email associated with the token if the token is valid and within the expiration time,
      otherwise returns False.
    """
    serializer = URLSafeTimedSerializer(
        secret_key=current_app.config['SECRET_KEY'], salt=current_app.config['SECURITY_PASSWORD_SALT']
    )

    try:
        data = serializer.loads(token, max_age=expiration)

        fullname = data.get('fullname')
        email = data.get('email')

        if fullname is not None and email is not None:
            return {'fullname': fullname, 'email': email}
        else:
            return None # Invalid token structure

    except Exception:
        return None # Invalid Token
