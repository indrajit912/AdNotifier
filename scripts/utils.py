# Some utility functions
#
# Author: Indrajit Ghosh
#
# Date: Feb 01, 2024
#

import random
import hashlib
import telegram
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup

def send_telegram_message_by_BOT(bot_token:str, user_id:str, message:str='Hello World!'):
    """
    Sends msg to a user from a bot
    Parameter:
    ----------
        `bot_token`: str; The token of the bot which sends the msg
        `user_id`: str; Telegram user_id of the receipent # use 'userinfobot' in 
                        telegram to know the user_id
        `message`: str
    """
    message = message.replace('&', 'and')
    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={user_id}&text={message}"
    try:
        requests.get(telegram_api_url)
    except Exception as err:
        print(f"\n\nERROR: Telegram message couldn't be sent to {user_id}. \n {err}.\n")


def generate_otp():
    """Generate a random 6-digit OTP (One-Time Password).

    Returns:
        str: A string representing the randomly generated OTP.

    Example:
        >>> generate_otp()
        '657432'
    """
    return str(random.randint(100000, 999999))

def sha256_hash(raw_text):
    """Hash the given text using SHA-256 algorithm.

    Args:
        raw_text (str): The input text to be hashed.

    Returns:
        str: The hexadecimal representation of the hashed value.

    Example:
        >>> sha256_hash('my_secret_password')
        'e5e9fa1ba31ecd1ae84f75caaa474f3a663f05f4'
    """
    hashed = hashlib.sha256(raw_text.encode()).hexdigest()
    return hashed


def convert_utc_to_ist(utc_datetime_str):
    """
    Convert a UTC datetime string to Indian Standard Time (IST) format.

    Args:
        utc_datetime_str (str): A string representing a UTC datetime in the format '%Y-%m-%d %H:%M:%S'.

    Returns:
        str: A string representing the datetime in IST format, e.g., 'Dec 13, 2023 07:06 AM IST'.

    Example:
        >>> convert_utc_to_ist('2023-12-13 07:06:16')
        'Dec 13, 2023 07:06 AM IST'
    """
    # Convert string to datetime object
    utc_datetime = datetime.strptime(utc_datetime_str, "%Y-%m-%d %H:%M:%S")

    # Define UTC and IST timezones
    utc_timezone = timezone.utc
    ist_timezone = timezone(timedelta(hours=5, minutes=30))

    # Convert UTC datetime to IST
    ist_datetime = utc_datetime.replace(tzinfo=utc_timezone).astimezone(ist_timezone)

    # Format datetime in the desired string format
    formatted_datetime = ist_datetime.strftime("%b %d, %Y %I:%M %p IST")

    return formatted_datetime

def count_query_occurance(url:str, query_str:str):
    """
    Count the number of occurrences of a given query_str on a web page.

    Parameters:
    - url (str): The URL of the web page to analyze.
    - query_str (str): The query to search for.

    Returns:
    - int: The number of occurrences of the query_str on the page.
           Returns -1 if there is an error fetching the website content.

    Example:
    ```python
    url = "https://example.com"
    query_str = "ABC123"
    occurrences = count_advertisement_numbers(url, query_str)
    print(f"The advertisement number '{query_str}' appears {query_str} times on the page.")
    ```
    """
    try:
        # Fetch HTML content of the website
        try:
            response = requests.get(url)
        except requests.exceptions.SSLError:
            response = requests.get(url, verify=False)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all occurrences of the advertisement number on the page
        occurrences = (
            soup.body.text.count(query_str)
            if soup.body
            else
            soup.text.count(query_str)
        )

        return occurrences


    except requests.RequestException as e:
        return -1  # Error indicator
    

def get_lines_in_reverse(file_path):
    """
    Reads a text file and returns its lines in reversed order as a string.

    Parameters:
    - file_path (str): The path to the text file.

    Returns:
    - str: Reversed lines of the text file joined by newline characters.
           If an error occurs, returns an error message.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            reversed_lines = [line.strip() for line in reversed(lines)]
            return '\n'.join(reversed_lines)
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except Exception as e:
        return f"An error occurred: {e}"