class Card:
    def __init__(self):
        self.id = None

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

class CardManager:
    # ------------------------------------------------------------------------------------------------------------------
    # Public methods
    @staticmethod
    def FilterCards(cards, fields):
        # iterate over cards and apply filter by each field
        filtredCards = []
        for card in cards:
            for fieldName in fields.keys():
                if CardManager._FilterByField(card, fieldName, fields[fieldName]):
                    filtredCards.append(card)
        
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