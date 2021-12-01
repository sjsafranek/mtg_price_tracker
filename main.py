
import requests
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
# from concurrent.futures import ProcessPoolExecutor as PoolExecutor
import multiprocessing
from bs4 import BeautifulSoup
from itertools import chain


FORMAT = 'Modern'
LOW = 1
HIGH = 2.5
MAX_WORKERS = int(multiprocessing.cpu_count()/2)



def execute(func, jobs=[], max_workers=MAX_WORKERS):
    ''' Runs function in a worker pool and returns a generator containing results.
        https://dev.to/rhymes/how-to-make-python-code-concurrent-with-3-lines-of-code-2fpe
    '''
    with PoolExecutor(max_workers=max_workers) as executor:
        for result in executor.map(func, jobs):
            yield result



def get(url):
    print(url)
    return requests.get(url)

def getHTML(url):
    return BeautifulSoup(get(url).text, 'html.parser')

def getJSON(url):
    return get(url).json()

def fetchBulkData():
    return getJSON('https://api.scryfall.com/bulk-data')['data']

def fetchOracleCards():
    data = fetchBulkData()
    all_cards = [ d for d in data if 'oracle_cards' == d['type'] ]
    return getJSON(all_cards[0]['download_uri'])

def fetchCardsForFormat(legalIn):
    cards = fetchOracleCards()
    if not legalIn:
        return cards
    return [ card for card in cards if 'legal' == card['legalities'].get(legalIn.lower())]

def fetchCards(legal_in=FORMAT):
    return fetchCardsForFormat(legal_in)

def fetchCard(name):
    resp = requests.get('https://api.scryfall.com/cards/search', params={'q': name.lower(), 'unique': 'prints'})
    if 200 != resp.status_code:
        return []
    cards = resp.json()['data']
    return [ card for card in cards if card['name'].lower() == name.lower() ]





def scrapeLinks(url):
    links = []
    html = getHTML(url)
    for a in html.find_all('a'):
        if a.get('href'):
            links.append(a.get('href'))
    return links


def fetchDeck(url):
    deck = {}
    html = getHTML(url)
    # Download links...
    # https://mtgtop8.com/mtgo
    # https://mtgtop8.com/dec
    for elem in html.find_all('div', {'class': 'deck_line'}):
        text = elem.get_text()
        if text:
            parts = text.split(' ', 1)
            if parts[1] not in deck:
                deck[parts[1]] = 0
            deck[parts[1]] += int(parts[0])
    return deck


def fetchDecks():
    archetypeLinks = execute(scrapeLinks, [
                    'https://mtgtop8.com/{0}'.format(link) 
                        for link in scrapeLinks('https://mtgtop8.com/format?f=MO&meta=54&a=')
                            if 'archetype' in link 
                ])
    deckLinks = chain.from_iterable([
        [
            link for link in links 
                if 'event' in link
        ] for links in archetypeLinks
    ])
    return execute(fetchDeck, ['https://mtgtop8.com/{0}'.format(link) for link in deckLinks])





playedCards = {}

decks = fetchDecks()
for deck in fetchDecks(): 
    for card in deck:
        if card not in playedCards:
            playedCards[card] = 0
        playedCards[card] += deck[card]











# Fetch Modern playable cards
cards = fetchCards()


# Filter by price
cards = [
    card for card in cards
        if card['prices']['usd'] and 
            LOW <= float(card['prices']['usd']) <= HIGH
]

# Filter by cmc
cards = [
    card for card in cards
        if 4 >= card['cmc'] 
]

# Ferch and print out amount the number of times card was printed
for printings in execute(fetchCard, [card['name'] for card in cards]):
    sets = list(set([card['set'] for card in printings]))
    if 2 >= len(printings):
        print(
            len(printings), 
            printings[0]['name']
        )


