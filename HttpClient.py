
import requests
import multiprocessing
from bs4 import BeautifulSoup
from functools import lru_cache

# Using the ThreadPoolExecutor to support requests.Session
# for TCP connection reuse.
from concurrent.futures import ThreadPoolExecutor as PoolExecutor

from logger import logger


MAX_WORKERS = int(multiprocessing.cpu_count()/2)



class HttpClient(object):

    def __init__(self):
        # Reuse tcp/http connections
        self.session = requests.Session()

    # @staticmethod
    @lru_cache(maxsize=120)
    def get(self, url, params=None):
        logger.debug(url)
        return self.session.get(url, params=params)

    def getHTML(self, url, params=None):
        return BeautifulSoup(
                    self.get(url, params=params).text,
                    'html.parser')

    def getJSON(self, url, params=None):
        return self.get(url, params=params).json()

    def scrapeLinksFromUrl(self, url):
        links = []
        html = self.getHTML(url)
        for a in html.find_all('a'):
            if a.get('href'):
                links.append(a.get('href'))
        return links        

    def execute(self, func, jobs=[], max_workers=MAX_WORKERS):
        ''' Runs function in a worker pool and returns a generator containing results.
            https://dev.to/rhymes/how-to-make-python-code-concurrent-with-3-lines-of-code-2fpe
        '''
        with PoolExecutor(max_workers=max_workers) as executor:
            for result in executor.map(func, jobs):
                yield result

