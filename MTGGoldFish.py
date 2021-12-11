import time

from Deck import Deck
from HttpClient import HttpClient


class MTGGoldFish(HttpClient):

    BASE_URL = 'https://www.mtggoldfish.com'

    def fetchDeckList(self, url):
        deck = Deck(url)
        resp = self.get(url)
        if 200 != resp.status_code:
            return deck
        #.BEGIN handle throttling
        if 'Throttled' in resp.text:
            logger.info(resp.text)
            time.sleep(15)
            return self.fetchDeckList(url)
        #.END
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
                deck.addCardToSideboard(name, int(number))
            else:
                deck.addCardToMainboard(name, int(number))
        return deck

    def fetchDeck(self, url):
        html = self.getHTML(url)
        for a in html.find_all('a'):
            if a.get('href') and '/deck/download' in a.get('href'):
                return self.fetchDeckList('https://www.mtggoldfish.com/{0}'.format(a.get('href')))
        return Deck(url)

    def fetchDecks(self, legality):
        urls = [
            'https://www.mtggoldfish.com/metagame/{0}/full?page=1#paper'.format(legality.lower()), 
            'https://www.mtggoldfish.com/metagame/{0}/full?page=2#paper'.format(legality.lower())
        ]
        deck_links = []
        for url in urls:
            deck_links += [ 'https://www.mtggoldfish.com/{0}'.format(link) for link in self.scrapeLinksFromUrl(url) if 'archetype' in link]
        deck_links = list(set(deck_links))
        return self.execute(self.fetchDeck, deck_links)




