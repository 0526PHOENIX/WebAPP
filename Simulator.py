"""
========================================================================================================================
Package
========================================================================================================================
"""
import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))

import random
import math
from typing import List, Dict

from Shoe import Shoe
from Hand import Hand
from Game import *
from Utils import *


"""
========================================================================================================================
Monte Carlo Simulator
========================================================================================================================
"""
class Simulator():

    """
    ====================================================================================================================
    Initialization
    ====================================================================================================================
    """
    def __init__(self, base_shoe: Shoe, blackjack_payout: float = 1.5, rng_seed: int = None) -> None:

        self.base_shoe = base_shoe
        self.blackjack_payout = blackjack_payout
        self.rng = random.Random(rng_seed)

        return

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def _prepare_shoe_from_state(self, player_cards: List[Rank], dealer_cards: List[Rank]) -> Shoe:

        # Clone Shoe
        shoe = self.base_shoe.clone()

        # Remove Player's Cards
        for card in player_cards[:]:
            if shoe.counts.get(card, 0) <= 0:
                raise ValueError("Not enough cards in shoe to remove player card")
            shoe.remove_card(card)

        # Remove Dealer's Cards
        for card in dealer_cards[:]:
            if shoe.counts.get(card, 0) <= 0:
                raise ValueError("Not enough cards in shoe to remove dealer card")
            shoe.remove_card(card)

        return shoe

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def simulate_action(self, player_cards: List[Rank], dealer_cards: List[Rank], action: str, n_sim: int = 5000) -> Dict:

        payoffs = []
        for _ in range(n_sim):

            # 
            shoe = self._prepare_shoe_from_state(player_cards[:], dealer_cards[:])

            # 
            player_hand = Hand(player_cards[:])
            dealer_hand = Hand(dealer_cards[:] + [shoe.draw_one()])

            # 
            if action == 'STAND':
                final_player_hand = player_hand

            elif action == 'HIT':
                player_hand.add_card(shoe.draw_one())
                final_player_hand = player_hand

            elif action == 'DOUBLE':
                player_hand.doubled = True
                player_hand.add_card(shoe.draw_one())
                final_player_hand = player_hand

            elif action == 'SPLIT':
                #
                h1 = Hand([player_cards[0]], bet = 1.0, is_split_hand = True)
                h2 = Hand([player_cards[1]], bet = 1.0, is_split_hand = True)
                #
                h1.add_card(shoe.draw_one())
                h2.add_card(shoe.draw_one())
                #
                dealer_play(shoe, dealer_hand)
                #
                payoff1 = settle_hand(h1, dealer_hand, blackjack_payout = self.blackjack_payout)
                payoff2 = settle_hand(h2, dealer_hand, blackjack_payout = self.blackjack_payout)
                payoffs.append(payoff1 + payoff2)
                continue

            # 
            dealer_play(shoe, dealer_hand)

            # 
            payoff = settle_hand(final_player_hand, dealer_hand, blackjack_payout = self.blackjack_payout)
            payoffs.append(payoff)

        # 
        n = len(payoffs)
        mean = sum(payoffs) / n if n else 0.0
        wins = sum(1 for p in payoffs if p > 0)
        losses = sum(1 for p in payoffs if p < 0)
        pushes = n - wins - losses
        var = sum((p - mean) ** 2 for p in payoffs) / n if n else 0.0

        return {
            'action': action,
            'n': n,
            'ev': mean,
            'win_rate': wins / n,
            'loss_rate': losses / n,
            'push_rate': pushes / n,
            'stddev': math.sqrt(var)
        }

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def evaluate_all(self, player_cards: List[Rank], dealer_cards: List[Rank], n_sim: int = 5000, allow_split: bool = True) -> Dict:

        actions = ['HIT', 'STAND']

        if len(player_cards) == 2:
            actions.append('DOUBLE')

        if allow_split and len(player_cards) == 2 and player_cards[0] == player_cards[1]:
            actions.append('SPLIT')

        results = {}
        for action in actions:
            results[action] = self.simulate_action(player_cards[:], dealer_cards[:], action, n_sim = n_sim)

        # 
        best = max(results.items(), key = lambda kv: kv[1]['ev'])
        return {
            'player_hand': [card_str(r) for r in player_cards[:]],
            'dealer_hand': [card_str(r) for r in dealer_cards[:]],
            'results': results,
            'best_action': best[0],
            'best_ev': best[1]['ev']
        }
    

"""
========================================================================================================================
Main Function
========================================================================================================================
"""
if __name__ == "__main__":

    base_shoe = Shoe(num_decks = 6, rng = random.Random(12345))
    simulator = Simulator(base_shoe, blackjack_payout = 1.5, rng_seed = 42)

    # Example states
    examples = [
        ([10, 10], [6]),
    ]

    for player, dealer in examples:

        print("=== State:", [card_str(x) for x in player], "vs", [card_str(x) for x in dealer])

        res = simulator.evaluate_all(player, dealer, n_sim = 20000, allow_split = True)
        for a, stats in res['results'].items():
            print(f"  {a}: ev={stats['ev']:.4f}, win={stats['win_rate']:.3f}, loss={stats['loss_rate']:.3f}, push={stats['push_rate']:.3f}")
        print("  Best:", res['best_action'], "EV=", res['best_ev'])
        print()