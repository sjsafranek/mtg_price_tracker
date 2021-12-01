import os
import csv
import logging
import argparse

import scryfall


# Setup logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(processName)s:%(process)d] %(module)s:%(funcName)s:%(lineno)d %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():

    # Fetch cards in bulk
    cards = []
    filename = ''
    updated_at = ''

    # Fetch cards in bulk
    for item in scryfall.fetchBulkDataTypes():
        if 'default_cards' == item['type']:
            # Get timestamp
            updated_at = item['updated_at']
            # Check if file exists
            filename = 'data/{0}.csv'.format(updated_at)
            if os.path.exists(filename):
                exit(0)
            # Fetch cards
            cards = scryfall.fetchBulkDataByType('default_cards')

    # Open file handler
    with open(filename, 'w') as fh:
        # create csv writer and write fieldnames
        writer = csv.writer(fh)
        writer.writerow([
            'updated_at',
            'name',
            'set',
            'set_name',
            'price_base',
            'price_foil',
            'standard',
            'pioneer',
            'modern',
            'legacy',
            'commander'
        ])

        # Write card prices to csv file
        for card in cards:
            writer.writerow([
                updated_at,
                card['name'],
                card['set'],
                card['set_name'],
                card['prices']['usd'],
                card['prices']['usd_foil'],
                'legal' == card['legalities']['standard'],
                'legal' == card['legalities']['pioneer'],
                'legal' == card['legalities']['modern'],
                'legal' == card['legalities']['legacy'],
                'legal' == card['legalities']['commander']
            ])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Magic the Gathering price tracker')
    args, unknown = parser.parse_known_args()

    main()



#
