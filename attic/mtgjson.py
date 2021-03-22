'''
    Api client for MTG JSON
    docs: https://mtgjson.com/
'''

import http_utils as utils


def fetchCardListByLegality(legality):
    url = 'https://mtgjson.com/api/v5/{0}.json'.format(legality.title())
    results = utils.fetchJSON(url)
    cards = []
    expansions = results['data']
    for expansion in expansions:
        cards += expansions[expansion]['cards']
    return cards
