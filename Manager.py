"""
========================================================================================================================
Package
========================================================================================================================
"""
import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))

from Shoe import Shoe
from Hand import Hand
from Simulator import Simulator
from Game import *
from Utils import *


"""
========================================================================================================================
Game Manager
========================================================================================================================
"""
class Manager():

    """
    ====================================================================================================================
    Initialization
    ====================================================================================================================
    """
    def __init__(self, num_decks: int = 6, num_sim: int = 10000, threshold_ratio: float = 0.30) -> None:

        # Base Shoe
        self.base = Shoe(num_decks = num_decks)

        # Shoe & Simulator
        self.shoe = self.base.clone()
        self.simu = Simulator(self.shoe, num_sim)

        # Reshuffle Threshold
        self.threshold = int(self.base.remaining() * threshold_ratio)

        return

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def _maybe_reshuffle(self) -> None:

        print(self.shoe.counts)
        
        if self.shoe.remaining() < self.threshold:
            # Reshuffle Shoe with Base Shoe
            self.shoe = self.base.clone()
            self.simu.base_shoe = self.shoe

        return

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def start_round(self) -> None:

        # Check Wether Shuffle
        self._maybe_reshuffle()

        # Cards
        self.player_hand = Hand([])
        self.dealer_hand = Hand([])

        # States
        self.finish = False
        self.result = None

        # Values
        self.final_player_value = None
        self.final_dealer_value = None

        return

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def deal_initial(self):

        # Player Initial Hand
        self.player_hand.add_card(self.shoe.draw_one())
        self.player_hand.add_card(self.shoe.draw_one())

        # Dealer Initial Hand
        self.dealer_hand.add_card(self.shoe.draw_one())

        return {
            'player': [card_str(card) for card in self.player_hand.cards],
            'dealer': [card_str(card) for card in self.dealer_hand.cards]
        }

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def get_recommendation(self) -> dict:

        return self.simu.evaluate_all(player_cards = self.player_hand.cards, dealer_cards = self.dealer_hand.cards)

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def player_hit(self) -> None:
        
        # Hit
        self.player_hand.add_card(self.shoe.draw_one())

        # Check Validatity
        if self.player_hand.is_bust() or self.player_hand.best_value() >= 21 or len(self.player_hand) >= 5:
            # Settle
            self.finish_round()

        return

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def player_stand(self) -> None:

        # Settle
        self.finish_round()

        return

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def player_double(self) -> None:

        # Hit
        self.player_hand.add_card(self.shoe.draw_one())

        # Set Double State
        self.player_hand.doubled = True

        # Settle
        self.finish_round()

        return

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def finish_round(self) -> None:
        
        # Check Validatity
        if self.finish:
            return
        self.finish = True

        # Dealer Game Play Rule
        dealer_play(self.shoe, self.dealer_hand)

        # Sattle
        self.result = settle_hand(self.player_hand, self.dealer_hand, blackjack_payout = self.simu.blackjack_payout)
        
        # Compute Best Value
        self.final_player_value = self.player_hand.best_value()
        self.final_dealer_value = self.dealer_hand.best_value()

        return

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def get_result(self):
        
        # Check Validatity
        if not self.finish:
            return None
        
        return {
            'player_cards': [card_str(card) for card in self.player_hand.cards],
            'dealer_cards': [card_str(card) for card in self.dealer_hand.cards],
            'player_value': self.final_player_value,
            'dealer_value': self.final_dealer_value,
            'result': self.result
        }


"""
========================================================================================================================
Main Function
========================================================================================================================
"""
if __name__ == "__main__":

    gm = Manager(num_decks = 3, num_sim = 5000)

    count = 0
    total = 0
    while True:

        gm.start_round()

        init = gm.deal_initial()
        print("Player:", init["player"])
        print("Dealer:", init["dealer"])

        while not gm.finish:
            rec = gm.get_recommendation()
            print("Best action:", rec["best_action"])
            
            action = rec["best_action"]

            if action == "HIT":
                gm.player_hit()
            elif action == "DOUBLE":
                gm.player_double()
            else:
                gm.player_stand()

        result = gm.get_result()
        print("Final result:", result)
        print()

        total += result['result']

        count += 1
        if count > 10:
            break


    print()
    print(total)
    print()