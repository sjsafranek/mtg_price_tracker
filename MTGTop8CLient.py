
from Deck import Deck
from HttpClient import HttpClient


class MTGTop8CLient(HttpClient):

    BASE_URL = 'https://mtgtop8.com'

    FORMATS = {
        'modern': 'MO'
    }

    def fetchDeckList(self, url):
        deck = Deck(url)
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
                deck.addCardToSideboard(name, int(number))
            else:
                deck.addCardToMainboard(name, int(number))
        return deck

    def fetchDeck(self, url):
        html = self.getHTML(url)
        for a in html.find_all('a'):
            if a.get('href') and 'mtgo' in a.get('href'):
                return self.fetchDeckList('https://mtgtop8.com/{0}'.format(a.get('href')))
        return Deck(url)

    def fetchDecks(self, legality):
        archetypeLinks = self.execute(self.scrapeLinksFromUrl, [
                        'https://mtgtop8.com/{0}'.format(link)
                            for link in self.scrapeLinksFromUrl('https://mtgtop8.com/format?f={0}&meta=51&a='.format(self.FORMATS[legality.lower]))
                                if 'archetype' in link
                    ])
        deck_links = chain.from_iterable([
            [
                link for link in links
                    if 'event' in link
            ] for links in archetypeLinks
        ])
        # remove duplicates
        deck_links = list(set(deck_links))
        return self.execute(self.fetchDeck, ['https://mtgtop8.com/{0}'.format(link) for link in deck_links])
