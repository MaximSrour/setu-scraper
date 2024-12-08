import os
import csv
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

from config import DIR_FILTERED_LINKS, DIR_OUTPUT

def get_html(url: str) -> BeautifulSoup:
    """
    Makes a request to the specified URL and returns the response.

    @param {str} url - The URL to make the request to
    @returns {BeautifulSoup} - The response from the request
    """

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup