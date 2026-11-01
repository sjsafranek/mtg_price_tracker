import os.path
import pandas
import datetime

import lib.scryfall as scryfall


# Initialize scryfall api client and fetch master dataset
api = scryfall.Api()
datasets = api.fetchDatasets()
dataset = list(filter(lambda d: 'all_cards' == d['type'], datasets))[0]
updated_at = dataset['updated_at']

# Check for archive file
dt = datetime.datetime.fromisoformat(updated_at)
now = int(dt.timestamp())
pricesFilename = f'data/prices_{now}.csv'
if os.path.exists(pricesFilename):
    exit(0)

# Build new card dataset
CARDS = {
    'scryfall_card_id': [],
    'name': []
}

PRICES = {
    'event_timestamp': [],
    'scryfall_card_id': [],
    'usd': [],
    'usd_foil': [],
    'usd_etched': []
}

# Fetch cards from scryfall
for card in api.fetchDatasetByName('all_cards'):
    
    # Collect card base data
    CARDS['scryfall_card_id'].append(card.id)
    CARDS['name'].append(card.name)

    # Collect pricing info
    if (card.prices.usd or card.prices.usd_foil or card.prices.usd_etched):    
        PRICES['event_timestamp'].append(updated_at)
        PRICES['scryfall_card_id'].append(card.id)
        PRICES['usd'].append(card.prices.usd)
        PRICES['usd_foil'].append(card.prices.usd_foil)
        PRICES['usd_etched'].append(card.prices.usd_etched)

# Convert dicts to pandas dataframes
prices_df = pandas.DataFrame.from_dict(PRICES)
cards_df = pandas.DataFrame.from_dict(CARDS)

# Copy to master files
cards_df.to_csv('data/cards.csv', index=False)
#prices_df.to_csv('data/prices.csv', index=False)

# Copy to historical archive files
prices_df.to_csv(pricesFilename, index=False)

print(pricesFilename)