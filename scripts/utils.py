# Some utility functions
#
# Author: Indrajit Ghosh
#
# Date: Feb 01, 2024
#

import random
import hashlib
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import logging

logger = logging.getLogger(__name__)

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
        logger.info(f"TELEGRAM_SENT: Telegram message sent to `{user_id}`.")
    except Exception as err:
        logger.error(f"TELEGRAM_ERR: Telegram message couldn't be sent to `{user_id}`. \t {err}.\n")

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

def get_webpage_sha256(url):
    """
    TODO: Delete it
    Retrieve the content of a webpage at the specified URL, compute its SHA-256 hash, and return the hash.

    Author: Indrajit Ghosh
    Created On: Feb 11, 2024

    :param url: The URL of the webpage.
    :type url: str

    :return: The SHA-256 hash of the webpage content.
             If an error occurs during the request or parsing, returns -1.
    :rtype: str or int
    """
    try:
        try:
            res = requests.get(url)
        except requests.exceptions.SSLError:
            res = requests.get(url, verify=False)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        return sha256_hash(soup.text)

    except requests.RequestException as e:
        # If an error occurs during the request or parsing, return -1
        return -1
    
def get_webpage_sha256_selenium(url):
    """
    TODO: Delete it!
    Retrieve the content of a webpage at the specified URL, compute its SHA-256 hash, and return the hash using Selenium.

    :param url: The URL of the webpage.
    :type url: str

    :return: The SHA-256 hash of the webpage content.
             If an error occurs during the request or parsing, returns -1.
    :rtype: str or int
    """
    try:
        # Set up a headless Chrome browser
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)

        # Fetch the webpage
        driver.get(url)

        # Wait for some time to ensure dynamic content is loaded (you may need to adjust this)
        driver.implicitly_wait(5)

        # Get the webpage content
        webpage_content = driver.page_source

        # Compute the SHA-256 hash
        hash_object = hashlib.sha256(webpage_content.encode())
        sha256_hash = hash_object.hexdigest()

        # Close the browser
        driver.quit()

        return sha256_hash

    except Exception as e:
        # If an error occurs during the request or parsing, return -1
        return -1


def count_query_occurance(url:str, query_str:str):
    """
    TODO: Delete it
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

        minimal_tag = find_minimal_tag(soup=soup, query_str=query_str)

        # TODO: Return the hash of these minimal_tag

        return occurrences, minimal_tag


    except requests.RequestException as e:
        return -1  # Error indicator
    

def find_minimal_tag(soup: BeautifulSoup, query_str: str):
    """
    Finds the minimal HTML tag containing all occurrences of the specified query string.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.
    - query_str (str): The query string to search for.

    Returns:
    str: The minimal HTML tag containing all occurrences of the query string.
    """
    # Find all occurrences of the query string
    occurrences = soup.find_all(string=lambda text: query_str in text)

    # Find the minimal HTML tag containing all occurrences
    minimal_tag = None
    for occurrence in occurrences:
        # Traverse the tree upwards to find the common ancestor
        ancestor = occurrence.find_parent().find_parent().find_parent()
        if minimal_tag is None or ancestor.find(minimal_tag):
            minimal_tag = ancestor

    return minimal_tag

def count_query_occurrences_and_hash(url: str, query_str: str):
    """
    Counts the occurrences of a query string on a webpage using Selenium and returns a hash of the minimal HTML tag.

    Parameters:
    - url (str): The URL of the webpage to analyze.
    - query_str (str): The query string to search for.

    Returns:
    tuple: A tuple containing the number of occurrences of the query string and the hash of the minimal HTML tag.
    """
    try:
        # Set up a headless Chrome browser
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)

        # Fetch the webpage
        driver.get(url)

        # Wait for some time to ensure dynamic content is loaded (you may need to adjust this)
        driver.implicitly_wait(5)

        # # Find all occurrences of the query string on the page
        # elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{query_str}')]")
        # occurrences = len(elements)

        # Extract HTML content from the current page
        html_content = driver.page_source
        occurrence_count = html_content.count(query_str)

        # Parse the HTML content with Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the minimal HTML tag containing the query_str
        minimal_tag = find_minimal_tag(soup=soup, query_str=query_str)
        webpage_hash = sha256_hash(minimal_tag)

        # Close the browser
        driver.quit()

        return occurrence_count, webpage_hash

    except Exception as e:
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