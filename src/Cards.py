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
