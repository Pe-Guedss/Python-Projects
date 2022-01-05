import random

cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

class Dealer ():
    def __init__(self) -> None:
        self.hand = []

    def new_round (self):
        self.hand = [self.new_card(), self.new_card()]
    
    def new_card(self):
        return random.choice(cards)