import pandas

df1 = pandas.read_csv('data/catalog.csv')
df2 = pandas.read_csv('data/modern.csv')


df = pandas.merge(df1, df2, how='outer', on='name')

def shouldBuy(row):
    if 'PLAYSET' != row['state']:
        if row['price'] and 5 > float(row['price']):
            if float(row['deck_percentage']) > 3:
                return True
    return False

df['buy'] = df.apply(lambda row: shouldBuy(row), axis = 1)

df.to_csv('cards.csv', index=False)
