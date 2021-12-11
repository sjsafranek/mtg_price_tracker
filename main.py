
import json
from datetime import datetime
from itertools import chain

from logger import logger
from ScryFallClient import ScryFallClient
from MTGTop8CLient import MTGTop8CLient
from MTGGoldFish import MTGGoldFish



FORMAT = 'Modern'
START = datetime.now().isoformat()




# Create http clients
scry = ScryFallClient()
top8 = MTGTop8CLient()
fish = MTGGoldFish()


# Fetch decks for modern
number_of_decks = 0
playedCards = {}

for deck in fish.fetchDecks(FORMAT):
    data = deck.ToDict()
    number_of_decks += 1
    for section in ['mainboard', 'sideboard']:
        for card in data[section]:
            if card not in playedCards:
                playedCards[card] = {'decks': 0,'total_count': 0, 'price': -1, 'type_line': None, 'colors': []}
            playedCards[card]['total_count'] += data[section][card]
            playedCards[card]['decks'] += 1

for deck in top8.fetchDecks(FORMAT):
    data = deck.ToDict()
    number_of_decks += 1
    for section in ['mainboard', 'sideboard']:
        for card in data[section]:
            if card not in playedCards:
                playedCards[card] = {'decks': 0,'total_count': 0, 'price': -1, 'type_line': None, 'colors': []}
            playedCards[card]['total_count'] += data[section][card]
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
