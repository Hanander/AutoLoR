import os
import json

class Card:
    def __init__(self, id=None, params=None):
        self.id = id
        self.img = None
        self.info = {
            'title': None,

            'region': None,
            'type': None,
            'rarity': None,

            'mana cost': None,
            'attack': None,
            'health': None,
            'abilities': [],

            'associated': None,

            'img link': None
        }
        if not params is None:
            self._SetInfo(id, params)
    
    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    def _SetInfo(self, id, params):
        for fieldName in params:
            self.info[fieldName] = params[fieldName]

class CardManager:
    # ------------------------------------------------------------------------------------------------------------------
    # Public methods
    @staticmethod
    def LoadCards(cardsFolderPath):
        cardsInfoFilePath = os.path.join(cardsFolderPath, 'cards_info.json')
        with open(cardsInfoFilePath, 'r') as f:
            cardsJSON = json.load(f)
        cards = []
        for cardKey in cardsJSON.keys():
            newCard = Card(id=cardKey, params=cardsJSON[cardKey])
            cards.append(newCard)
        
        return cards

    
    @staticmethod
    def FilterCards(cards, fields, operator=any):
        # set None by default for every card
        filterResults = [None for _ in cards]
        # iterate over cards and apply filter by each field
        for i, card in enumerate(cards):
            for fieldName in fields.keys():
                currentRes = CardManager._FilterByField(card, fieldName, fields[fieldName])
                if filterResults[i] is None:
                    filterResults[i] = currentRes
                else:
                    filterResults[i] = operator([currentRes, filterResults[i]])
        filtredCards = [card for i, card in enumerate(cards) if filterResults[i]]

        return filtredCards

    @staticmethod
    def GetImages(cardsJSON, imgFolder):
        pass
    
    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    @staticmethod
    def _FilterByField(card, fieldName, fieldVals):
        # check field is not empty
        if fieldName == 'abilities':
            if len(card.info[fieldName]) == 0:
                return False
        else:
            if card.info[fieldName] is None:
                return False
        # check card has field val
        for val in fieldVals:
            if fieldName == 'abilities':
                if val in card.info[fieldName]:
                    return True
            else:
                if card.info[fieldName] == val:
                    return True
        return False

if __name__ == "__main__":
    cardsFolderPath = os.path.join('..', 'cards')
    cards = CardManager.LoadCards(cardsFolderPath)
    filtredCards = CardManager.FilterCards(cards, {'type': ['Spell'], 'mana cost': ['6', '7']}, operator=all)
    print('n filtred cards = {}'.format(len(filtredCards)))
    print('first 3 card:')
    for card in filtredCards:
        print(card.info)