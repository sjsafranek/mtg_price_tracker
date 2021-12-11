import sys
import json
import time
import pandas
import requests
import multiprocessing
from datetime import datetime
from bs4 import BeautifulSoup
from itertools import chain

# if 'linux' == sys.platform:
#     from concurrent.futures import ProcessPoolExecutor as PoolExecutor
# else:
#     from concurrent.futures import ThreadPoolExecutor as PoolExecutor

# Using the ThreadPoolExecutor to support requests.Session
# for TCP connection reuse.
from concurrent.futures import ThreadPoolExecutor as PoolExecutor

from logger import logger



FORMAT = 'Modern'
MAX_WORKERS = int(multiprocessing.cpu_count()/2)
START = datetime.now().isoformat()



def execute(func, jobs=[], max_workers=MAX_WORKERS):
    ''' Runs function in a worker pool and returns a generator containing results.
        https://dev.to/rhymes/how-to-make-python-code-concurrent-with-3-lines-of-code-2fpe
    '''
    with PoolExecutor(max_workers=max_workers) as executor:
        for result in executor.map(func, jobs):
            yield result



class HttpClient(object):

    def __init__(self):
        # Reuse tcp/http connections
        self.session = requests.Session()
        pass

    def get(self, url, params=None):
        logger.debug(url)
        # return requests.get(url, params=params)
        return self.session.get(url, params=params)

    def getHTML(self, url, params=None):
        return BeautifulSoup(
                    self.get(url, params=params).text,
                    'html.parser')

    def getJSON(self, url, params=None):
        return self.get(url, params=params).json()



class ScryFallClient(HttpClient):

    def fetchBulkData(self):
        return self.getJSON('https://api.scryfall.com/bulk-data')['data']

    def fetchOracleCards(self):
        data = self.fetchBulkData()
        all_cards = [ d for d in data if 'oracle_cards' == d['type'] ]
        return self.getJSON(all_cards[0]['download_uri'])

    def fetchCardsForFormat(self, legalIn):
        cards = self.fetchOracleCards()
        if not legalIn:
            return cards
        return [ card for card in cards if 'legal' == card['legalities'].get(legalIn.lower())]

    def fetchCard(self, name):
        resp = self.get('https://api.scryfall.com/cards/search', params={'q': name.lower(), 'unique': 'prints'})
        if 200 != resp.status_code:
            return []
        cards = resp.json()['data']
        return [ card for card in cards if card['name'].lower() == name.lower() ]



class MTGTop8CLient(HttpClient):

    def scrapeLinks(self, url):
        links = []
        html = self.getHTML(url)
        for a in html.find_all('a'):
            if a.get('href'):
                links.append(a.get('href'))
        return links

    def fetchDeckList(self, url):
        deck = {'mainboard': {}, 'sideboard': {}}
        resp = self.get(url)
        if 200 != resp.status_code:
            return deck
        # Parse deck list
        lines = resp.text.replace('\r','').split('\n')
        sideboard = False
        for line in lines:
            if '' == line:
                continue
            if 'sideboard' in line.lower():
                sideboard = True
                continue
            parts = line.split(' ')
            number = parts[0]
            name = ' '.join(parts[1:])
            if sideboard:
                deck['sideboard'][name] = int(number)
            else:
                deck['mainboard'][name] = int(number)
        return deck

    def fetchDeck(self, url):
        deck = {}
        html = self.getHTML(url)
        for a in html.find_all('a'):
            if a.get('href') and 'mtgo' in a.get('href'):
                deck = self.fetchDeckList('https://mtgtop8.com/{0}'.format(a.get('href')))
                return deck
        return {'mainboard': {}, 'sideboard': {}}

    def fetchDecksForModern(self):
        archetypeLinks = execute(self.scrapeLinks, [
                        'https://mtgtop8.com/{0}'.format(link)
                            # for link in self.scrapeLinks('https://mtgtop8.com/format?f=MO&meta=54&a=')
                            for link in self.scrapeLinks('https://mtgtop8.com/format?f=MO&meta=51&a=')
                                if 'archetype' in link
                    ])
        deckLinks = chain.from_iterable([
            [
                link for link in links
                    if 'event' in link
            ] for links in archetypeLinks
        ])
        # remove duplicates
        deckLinks = list(set(deckLinks))
        return execute(self.fetchDeck, ['https://mtgtop8.com/{0}'.format(link) for link in deckLinks])



class MTGGoldFish(HttpClient):

    def scrapeLinks(self, url):
        links = []
        html = self.getHTML(url)
        for a in html.find_all('a'):
            if a.get('href'):
                links.append(a.get('href'))
        return links

    def fetchDeckList(self, url):
        deck = {'mainboard': {}, 'sideboard': {}}
        resp = self.get(url)
        if 200 != resp.status_code:
            return deck
        if 'Throttled' in resp.text:
            logger.info(resp.text)
            time.sleep(5)
            return self.fetchDeckList(url)
        lines = resp.text.replace('\r','').split('\n')
        sideboard = False
        for line in lines:
            if '' == line:
                sideboard = True
                continue
            parts = line.split(' ')
            number = parts[0]
            name = ' '.join(parts[1:])
            if sideboard:
                deck['sideboard'][name] = int(number)
            else:
                deck['mainboard'][name] = int(number)
        return deck

    def fetchDeck(self, url):
        deck = {}
        html = self.getHTML(url)
        for a in html.find_all('a'):
            if a.get('href') and '/deck/download' in a.get('href'):
                deck = self.fetchDeckList('https://www.mtggoldfish.com/{0}'.format(a.get('href')))
                return deck
        return {'mainboard': {}, 'sideboard': {}}

    def fetchDecksForModern(self):
        deckLinks = []
        for baseLink in ['https://www.mtggoldfish.com/metagame/modern/full?page=1#paper', 'https://www.mtggoldfish.com/metagame/modern/full?page=2#paper']:
            deckLinks += [ 'https://www.mtggoldfish.com/{0}'.format(link) for link in self.scrapeLinks(baseLink) if 'archetype' in link]
        deckLinks = list(set(deckLinks))
        return execute(self.fetchDeck, deckLinks)


'''

scry = ScryFallClient()

# Fetch Modern playable cards
cards = scry.fetchCardsForFormat('Modern')

client = HttpClient()

data = client.getJSON('https://api.mtgstocks.com/lists/11')
modernStaples = [
    card['name'] for card in data['prints']
]
modernStaples = list(set(modernStaples))

with open('cards.csv', 'w') as fh:
    fh.write('name,price,type_line,colors\n')
    for card in cards:
        if card['name'] in modernStaples:
            fh.write('"{0}",{1},{2},{3}\n'.format(
                card['name'],
                card.get('prices', {}).get('usd', -1),
                card['type_line'],
                ''.join(card['colors'])
            ))

exit()


'''










# Create http clients
scry = ScryFallClient()
top8 = MTGTop8CLient()
fish = MTGGoldFish()


# Fetch decks for modern
number_of_decks = 0
playedCards = {}

for deck in fish.fetchDecksForModern():
    number_of_decks += 1
    for section in ['mainboard', 'sideboard']:
        for card in deck[section]:
            if card not in playedCards:
                playedCards[card] = {'decks': 0,'total_count': 0, 'price': -1, 'type_line': None, 'colors': []}
            playedCards[card]['total_count'] += deck[section][card]
            playedCards[card]['decks'] += 1

for deck in top8.fetchDecksForModern():
    number_of_decks += 1
    for section in ['mainboard', 'sideboard']:
        for card in deck[section]:
            if card not in playedCards:
                playedCards[card] = {'decks': 0,'total_count': 0, 'price': -1, 'type_line': None, 'colors': []}
            playedCards[card]['total_count'] += deck[section][card]
            playedCards[card]['decks'] += 1


# Fetch Modern playable cards
cards = scry.fetchCardsForFormat('Modern')

# Lookup card price
for card in cards:
    name = card['name']
    if name in playedCards:
        if card['prices']['usd']:
            playedCards[name]['price'] = float(card['prices']['usd'])
        playedCards[name]['type_line'] = card['type_line']
        playedCards[name]['colors'] = card['colors']
        # image_uris


# # Lookup number of card printings
# for printings in execute(fetchCard, list(playedCards.keys())):
#     if len(printings):
#         name = printings[0]['name']
#         sets = list(set([card['set'] for card in printings]))
#         playedCards[name]['printings'] = len(sets)


# Write to file
with open('data/modern.csv', 'w') as fh:
    fh.write('decks,deck_percentage,total_count,name,price,type_line,colors\n')
    for name in playedCards:
        color = ''.join(playedCards[name]['colors'])
        fh.write('{0},{1},{2},"{3}",{4},{5},{6}\n'.format(
            playedCards[name]['decks'],
            round(playedCards[name]['decks'] / number_of_decks * 100, 2),
            playedCards[name]['total_count'],
            name,
            playedCards[name]['price'],
            playedCards[name]['type_line'],
            color
        ))





#
