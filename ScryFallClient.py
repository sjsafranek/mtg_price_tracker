
from Deck import Deck
from HttpClient import HttpClient


class ScryFallClient(HttpClient):

    BASE_URL = 'https://api.scryfall.com'

    def fetchBulkData(self):
        return self.getJSON('https://api.scryfall.com/bulk-data')['data']

    def fetchOracleCards(self):
        data = self.fetchBulkData()
        all_cards = [ d for d in data if 'oracle_cards' == d['type'] ]
        return self.getJSON(all_cards[0]['download_uri'])

    def fetchCardsForFormat(self, legality):
        cards = self.fetchOracleCards()
        if not legality:
            return cards
        return [ card for card in cards if 'legal' == card['legalities'].get(legality.lower())]

    def fetchCard(self, name):
        resp = self.get('https://api.scryfall.com/cards/search', params={'q': name.lower(), 'unique': 'prints'})
        if 200 != resp.status_code:
            return []
        cards = resp.json()['data']
        return [ card for card in cards if card['name'].lower() == name.lower() ]
