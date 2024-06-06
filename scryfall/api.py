import time
from functools import lru_cache 

from .logger import logger
from .HttpClient import HttpClient
from .card import Card


class Api(HttpClient):

    BASE_URL = 'https://api.scryfall.com'

    def _fetchBulkData(self):
        max_age = 60
        __time_salt = int(time.time() / max_age)
        return self.getJSON(f'https://api.scryfall.com/bulk-data?_ts={__time_salt}')['data']

    def fetchDatasets(self):
        return self._fetchBulkData()

    def fetchDatasetByName(self, name):
        data = self.fetchDatasets()
        dataset = [ d for d in data if name == d['type'] ]
        for card in self.getJSON(dataset[0]['download_uri']):
            yield Card(card)

    def fetchAllCards(self):
        return self.fetchDatasetByName('all_cards')

    def fetchOracleCards(self):
        return self.fetchDatasetByName('oracle_cards')

    def fetchCardsByFormat(self, legality):
        cards = self.fetchOracleCards()
        if not legality:
            return cards
        return [ Card(card) for card in cards if 'legal' == card['legalities'].get(legality.lower())]

    def fetchCardByName(self, name):
        resp = self.get('https://api.scryfall.com/cards/search', params={'q': name.lower(), 'unique': 'prints'})
        if 200 != resp.status_code:
            return []
        cards = resp.json()['data']
        return [ Card(card) for card in cards if card['name'].lower() == name.lower() ]

    def fetchCardByScryFallId(scryfallId):
        url = 'https://api.scryfall.com/cards/{0}'.format(scryfallId)
        return utils.fetchJSON(url)
