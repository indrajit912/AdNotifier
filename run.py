# Adnotifier
#
# Author: Indrajit Ghosh
# Created on: Jan 31, 2024
#

"""
This script starts the Flask development server to run the web application.

Usage:
    python3 run.py
"""

from app import create_app
from config import DevelopmentConfig

app = create_app(DevelopmentConfig) # Change the config before deploying


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)