# Some utility functions
#
# Author: Indrajit Ghosh
#
# Date: Feb 01, 2024
#

import hashlib
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup

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

def count_advertisement_numbers(url:str, advertisement_number:str):
    """
    Count the number of occurrences of a given advertisement number on a web page.

    Parameters:
    - url (str): The URL of the web page to analyze.
    - advertisement_number (str): The advertisement number to search for.

    Returns:
    - int: The number of occurrences of the advertisement number on the page.
           Returns -1 if there is an error fetching the website content.

    Example:
    ```python
    url = "https://example.com"
    advertisement_number = "ABC123"
    occurrences = count_advertisement_numbers(url, advertisement_number)
    print(f"The advertisement number '{advertisement_number}' appears {occurrences} times on the page.")
    ```
    """
    try:
        # Fetch HTML content of the website
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all occurrences of the advertisement number on the page
        occurrences = soup.body.text.count(advertisement_number)

        return occurrences

    except requests.RequestException as e:
        return -1  # Error indicator
    
