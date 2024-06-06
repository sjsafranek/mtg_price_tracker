

class Deck(object):

    def __init__(self, name, archetype=None, legality=None):
        self.name = name
        self.archetype = archetype
        self.legality = legality
        self.mainboard = {}
        self.sideboard = {}

    def addCardToMainboard(self, name, amount=1):
        if name not in self.mainboard:
            self.mainboard[name] = 0
        self.mainboard[name] += amount

    def addCardToSideboard(self, name, amount=1):
        if name not in self.sideboard:
            self.sideboard[name] = 0
        self.sideboard[name] += amount

    def ToDict(self):
        return {
            'name': self.name,
            'archetype': self.archetype,
            'legality': self.legality,
            'mainboard': self.mainboard,
            'sideboard': self.sideboard
        }