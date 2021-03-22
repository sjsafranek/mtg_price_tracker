
from concurrent.futures import ProcessPoolExecutor as PoolExecutor

# Fetch card price from scryfall
with PoolExecutor(max_workers=4) as executor:
    for card in executor.map(fetchCardByScryFallId, scryfallIds):
        # Write card prices to csv file
        writer.writerow([
            TIMESTAMP,
            card['name'],
            card['prices']['usd'],
            card['prices']['usd_foil']
        ])
        # fh.flush()
