import requests
from bs4 import BeautifulSoup
from functools import lru_cache

from .logger import logger


class HttpClient(object):

    def __init__(self):
        # Reuse tcp/http connections
        self.session = requests.Session()

    @lru_cache(maxsize=16)
    def get(self, url, params=None):
        return self.session.get(url, params=params)

    def getHTML(self, url, params=None):
        return BeautifulSoup(
                    self.get(url, params=params).text,
                    'html.parser')

    def getJSON(self, url, params=None):
        return self.get(url, params=params).json()