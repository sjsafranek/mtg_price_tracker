import json
import glob
import os.path
import pandas
import datetime
from datetime import datetime
import difflib

import lib.mtggoldfish as mtggoldfish
import lib.scryfall as scryfall


today = datetime.utcnow().strftime('%Y%m%d')

fish = mtggoldfish.Api()
scry = scryfall.Api()

decks = {
    #'EsperHumans': 6372478,
    'EsperGriefBlade': 6131565,
    'MarduWinota': 5778007,
    'Niv2Light': 5453973
}

for name, fishId in decks.items():
    deck = fish.fetchDeck(fishId)
    current_file = f'decks/{name}_{today}.txt'
    current_hash = mtggoldfish.hash(deck)
    if not os.path.exists(current_file):
        all_files =  glob.glob(f'decks/{name}_*.txt')
        latest_file = max(all_files, key=os.path.getmtime)
        latest_hash = mtggoldfish.hash(mtggoldfish.load(latest_file))
        print(latest_file, current_hash, latest_hash)
        if current_hash == latest_hash:
            continue
    # else:
    #     latest_hash = mtggoldfish.hash(mtggoldfish.load(current_file))
    #     print(current_file, current_hash, latest_hash)
    #     print(mtggoldfish.to_string(deck) == mtggoldfish.to_string(mtggoldfish.load(current_file)))
    #     case_a = mtggoldfish.to_string(deck)
    #     case_b = mtggoldfish.to_string(mtggoldfish.load(current_file))
    #     output_list = [li for li in difflib.ndiff(case_a, case_b) if li[0] != ' ']
    #     print(output_list)
    mtggoldfish.dump(current_file, deck)




'''


mainboard = []
for cardname in deck.mainboard:
    count = deck.mainboard[cardname]
    cards = scry.fetchCardByName(cardname)
    if 0 == len(cards):
        raise ValueError(f'{cardname} not found')
    for card in cards:
        mainboard += [ card.id ] * count
        break
mainboard.sort()
print(mainboard)
print(len(mainboard))



sideboard = []
for cardname in deck.sideboard:
    count = deck.sideboard[cardname]
    cards = scry.fetchCardByName(cardname)
    if 0 == len(cards):
        raise ValueError(f'{cardname} not found')
    for card in cards:
        sideboard += [ card.id ] * count
        break
sideboard.sort()
print(sideboard)
print(len(sideboard))




print("""INSERT INTO decks (mgf_id, name, description) VALUES (5453973, 'niv2light', 'greedy nonsense');""")
print("""INSERT INTO history__deck_list (deck_id, section, cards) VALUES (1, 'mainboard', '{""" + ','.join(sideboard) +"""}');""")
print("""INSERT INTO history__deck_list (deck_id, section, cards) VALUES (1, 'sideboard', '{""" + ','.join(sideboard) +"""}');""")


'''
