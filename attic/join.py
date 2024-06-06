import pandas
import requests


df1 = pandas.read_csv('data/catalog.csv')
df2 = pandas.read_csv('data/modern.csv')


df = pandas.merge(df1, df2, how='outer', on='name')


SHOCK_LANDS = [
    'Blood Crypt', 
    'Breeding Pool', 
    'Godless Shrine', 
    'Hallowed Foutain',
    'Overgrown Tomb', 
    'Sacred Foundry',
    'Steam Vents',
    'Stomping Ground',
    'Temple Garden',
    'Watery Grave'
]

FETCH_LANDS = [
    'Arid Mesa',
    'Bloodstained Mire',
    'Fabled Passage',
    'Flooded Strand',
    'Marsh Flats',
    'Misty Rainforest',
    'Polluted Delta',
    'Prismatic Vista',
    'Scalding Tarn',
    'Verdant Catacombs',
    'Windswept Heath',
    'Wooded Foothils'
]


# Fetch Modern Staples
resp = requests.get('https://api.mtgstocks.com/lists/11')
MODERN_STAPLES = list(set([card['name'] for card in resp.json()['prints']]))


def shouldBuy(row):
    if 4 > row['owned']:
        if row['price'] and 5 > float(row['price']):
            if float(row['deck_percentage']) > 3:
                return True
        elif row['name'] in SHOCK_LANDS:
            return True
        elif row['name'] in FETCH_LANDS:
            return True
        elif row['name'] in MODERN_STAPLES:
            if row['price'] and 15 > float(row['price']):
                return True
    return False

def calculateMissing(row):
    if row['owned'] or 0 == row['owned']:
        return 4 - row['owned']

df['buy'] = df.apply(lambda row: shouldBuy(row), axis = 1)
df['missing'] = df.apply(lambda row: calculateMissing(row), axis = 1)

df.to_csv('cards.csv', index=False)
