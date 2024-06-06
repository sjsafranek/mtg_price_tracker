from .converters import to_float



class CardPrices(object):

    def __init__(self, data):
        self._data = data

    @property
    def usd(self):
        return to_float(self._data.get('usd'))

    @property
    def usd_foil(self):
        return to_float(self._data.get('usd_foil'))

    @property
    def usd_etched(self):
        return to_float(self._data.get('usd_etched'))



class Card(object):

    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return self._data.get('id')
    
    @property
    def name(self):
        return self._data.get('name')

    @property
    def prices(self):
        return CardPrices(self._data.get('prices', {}))