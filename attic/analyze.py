import json
import os.path
import pandas
import datetime

import lib.mtggoldfish as mtggoldfish
import lib.scryfall as scryfall


fish = mtggoldfish.Api()
scry = scryfall.Api()


deck = fish.fetchDeck(5453973)

supertypes = []
subtypes = []
colors = []
cmc = []

for cardname in deck.mainboard:
    count = deck.mainboard[cardname]
    for card in scry.fetchCardByName(cardname):
        # print(card.name)
        print(card.supertypes)
        print(card.subtypes)
        print(card.colors)
        
        # dont include lands in cmc stats
        if 'Land' not in card.supertypes and 0 != cmc:
            cmc += [card.cmc] * count

        if 2 == len(card.colors):
            colors += [card.colors] * count


        break

cmc.sort()
print(cmc)
print(colors)