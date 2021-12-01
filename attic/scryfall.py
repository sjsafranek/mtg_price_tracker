'''
    Api client for ScryFall
    docs: https://api.scryfall.com/
'''

import http_utils as utils


def fetchCardByScryFallId(scryfallId):
    url = 'https://api.scryfall.com/cards/{0}'.format(scryfallId)
    return utils.fetchJSON(url)


def fetchBulkDataTypes():
    return utils.fetchJSON('https://api.scryfall.com/bulk-data')['data']


def fetchBulkDataByType(bulk_type):
    for item in fetchBulkDataTypes():
        if bulk_type == item['type']:
            return utils.fetchJSON(item['download_uri'])
    return []


# def filterCards(cards, filters):
