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
    def FilterCards(cardsJSON, fields):
        # iterate over cards and apply filter by each field
        filtredKeys = []
        for cardKey in cardsJSON.keys():
            for fieldName in fields.keys():
                if CardManager._FilterByField(cardsJSON[cardKey], fieldName, fields[fieldName]):
                    filtredKeys.append(cardKey)
        
        return {cardKey: cardsJSON[cardKey] for cardKey in filtredKeys}
                

    @staticmethod
    def GetImages(cardsJSON, imgFolder):
        pass
    
    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    
    @staticmethod
    def _FilterByField(card, fieldName, fieldVals):
        # check field is not empty
        if fieldName == 'abilities':
            if len(card[fieldName]) == 0:
                return False
        else:
            if card[fieldName] is None:
                return False
        # check card has field val
        for val in fieldVals:
            if fieldName == 'abilities':
                if val in card[fieldName]:
                    return True
            else:
                if card[fieldName] == val:
                    return True
        return False