from Setup import *
import numpy as np


class Postflop:
    """Used to assess postflop hand strength

    Args:
        card_list (array): A list containing the hand dealt along with the cards on the board
    """

    def __init__(self, card_list):
        self.card_list = card_list
        self.num_cards = len(card_list)
        self.hand_dealt = card_list[0:2]
        self.flop = card_list[2:5]
        self.turn = card_list[5]
        self.river = card_list[6]

    def flop_scenario(self):
        """Determines hand strength on the flop

        Returns:
            A number that represents any postflop scenario
            HIGH CARDS
            - 1.1: Ace high to the board
            - 1.2: Paired/tripped board with Ace high
            BACKDOOR DRAWS
            - 2.1: Backdoor straight draw
            - 2.2: Backdoor flush draw
            DRAWS
            - 3.1: Gutshot with one card
            - 3.2: Gutshot with two cards
            - 3.3: Open-ender with one card
            - 3.4: Open-ender with two cards
            - 3.5: Flush draw with one card (A, K, Q)
            - 3.6: Flush draw with two cards
            - 3.7: Flush and straight draw with two cards
            SHOWDOWN HANDS
            - 4.1: Third pair and lower
            - 4.2: Pocket pair between third and second pair
            - 4.3: Second pair
            - 4.4: Pocket pair between second and top pair
            VALUE HANDS
            - 5.1: Top pair (T and below)
            - 5.2: Top pair (J and above)
            - 5.3: Overpair (T and below)
            - 5.4: Overpair (J and above)
            - 5.5: Two pair
            - 5.6: Trips
            - 5.7: Straight with one card
            - 5.8: Straight with two cards
            - 5.9: Flush on a paired board with two cards
            - 5.10: Flush on an paired board with one card
            - 5.11: Q-high flush and below on an unpaired board with one card
            - 5.12: K-high flush on an unpaired board with one card
            - 5.13: Full house with one card (lower)
            NUTTED HANDS
            - 6.1: Set on a dry, unconnected board
            - 6.2: Straight on an unpaired, non-flushy board
            - 6.3: A-high flush on an unpaired board with one card
            - 6.3: Flush on an unpaired board with two cards
            - 6.4: Full house with one card (higher)
            - 6.5: Full house with both cards
            - 6.6: Quads/straight flush
        """
        # Extract flop and sort
        for i in range(3):
            already_sorted = True
            for j in range(2 - i):
                if self.flop[j] > self.flop[j + 1]:
                    self.flop[j], self.flop[j + 1] = self.flop[j + 1], self.flop[j]
                already_sorted = False
            if already_sorted:
                break
        current_hand = PokerHand(self.card_list)
        hand_rank = current_hand.classify_hand()
        best_five = current_hand.best_five
        s_draw, s_outs = Draw(self.card_list).straight_draw()
        f_draw, f_suit = Draw(self.card_list).flush_draw()

        def using_both_cards():
            """Determines if both hole cards are utilized in the best five cards"""
            return set(self.hand_dealt).issubset(set(best_five))

        flop_card_ranks = [self.flop[0][0], self.flop[1][0], self.flop[2][0]]
        hand_card_ranks = [self.hand_dealt[0][0], self.hand_dealt[1][0]]

        # List of all applicable scenarios
        scenario = []

        # Full house, quads, straight flush
        if hand_rank in hand_ranks[5:]:
            scenario.append(20)
        # Three of a kind situations
        elif hand_rank == 'Three of a kind':
            # Set
            if using_both_cards():
                scenario.append(19)
            # Trips
            if not using_both_cards():
                scenario.append(17)
            # Ace high on a tripped board
            if len(np.unique(flop_card_ranks)) == 1:
                for hand_rank in hand_card_ranks:
                    if hand_rank == 'A':
                        scenario.append(4)
        # Two pair
        elif hand_rank == 'Two pair':
            scenario.append(18)
        # Flush or straight
        elif hand_rank in ['Straight', 'Flush']:
            scenario.append(18)
        # Open-ender with two cards
        elif s_draw and s_outs == 'Two' and using_both_cards():
            scenario.append(8)
        # Open-ender with one card
        elif s_draw and not using_both_cards():
            scenario.append(7)
        # Gutshot
        elif s_draw and s_outs == 'One':
            scenario.append(2)
        # Flush draw with two cards
        elif f_draw and using_both_cards():
            scenario.append(11)
        # Flush draw with one card
        elif s_draw and s_outs == 'Two' and not using_both_cards() and max(hand_card_ranks) in ['Q', 'K', 'A']:
            scenario.append(12)
        # Flush and straight draw
        elif s_draw and f_draw:
            scenario.append(13)
        # One pair situations
        elif hand_rank == 'One pair':
            if len(np.unique(hand_card_ranks)) == 1:
                # Overpair
                if ranks.index(hand_card_ranks[0]) > ranks.index(flop_card_ranks[0]):
                    scenario.append(15)
                # In between top and middle pair
                if ranks.index(flop_card_ranks[0]) > ranks.index(hand_card_ranks[0]) > ranks.index(flop_card_ranks[1]):
                    scenario.append(15)
                # In between middle and bottom pair
                if ranks.index(flop_card_ranks[1]) > ranks.index(hand_card_ranks[0]) > ranks.index(flop_card_ranks[2]):
                    scenario.append(15)
                # Below bottom pair
                if ranks.index(flop_card_ranks[1]) < ranks.index(flop_card_ranks[2]):
                    scenario.append(15)
            elif len(np.unique(flop_card_ranks)) == 3:
                for card_num, card in enumerate(self.hand_dealt):
                    # Top pair
                    if card[0] == flop_card_ranks[0]:
                        if card_num == 0:
                            kicker_card = 1
                        else:
                            kicker_card = 0
                        # Good kicker
                        if ranks.index(hand_card_ranks[kicker_card]) >= ranks.index('T'):
                            scenario.append(3)
                        # Meh kicker
                        else:
                            scenario.append(12)
                    # Middle pair
                    if card[0] == flop_card_ranks[1]:
                        if card_num == 0:
                            kicker_card = 1
                        else:
                            kicker_card = 0
                        # Good kicker
                        if ranks.index(hand_card_ranks[kicker_card]) >= ranks.index('T'):
                            scenario.append(3)
                        # Meh kicker
                        else:
                            scenario.append(12)
                    # Bottom pair
                    if card[0] == flop_card_ranks[2]:
                        scenario.append(1)
                # Pair and straight draw
                if s_draw:
                    scenario.append(9)
                # Pair and flush draw
                if f_draw:
                    scenario.append(8)
            elif len(np.unique(flop_card_ranks)) == 2:
                for hand_rank in hand_card_ranks:
                    # Ace high on a paired board
                    if hand_rank == 'A':
                        scenario.append(4)
            else:
                # Paired board but nothing else
                scenario.append(0)
        # Flopped nothing
        else:
            scenario.append(0)
        return max(scenario)

    def good_turn(self):
        """Determines hand strength on the turn

        Returns:
            An integer that represents a turn scenario
            - 1: Bottom pair and lower, two overcards with King high, bottom pair + bfd or high kicker (J+)
            - 2: Gutshot, gutshot + bfd
            - 3: Paired/tripped board and Ace high
            - 4: Ace high to the board low cards
            - 5: Middle pair (eh kicker 10 below), Middle pair + bfd
            - 6: Middle pair, good kicker (J+)
            - 7: Open-ender with one card
            - 8: Open-ender with two cards
            - 9: Combo draw - pair and open-ender
            - 10: Combo draw - pair and flush draw
            - 11: Flush draw with two cards
            - 12: A-high, K-high, or Q-high flush draw with one card
            - 13: Top pair (9 and below)
            - 14: Top pair (T and above) (call, XR 20%),
            - okhkjhkjkjh open-ender + flush draw (call, XR 25%), between middle pair and top pair
            - 15: Overpair (9 and below)
            - 16: Overpair (T and above)
            - 17: Trips
            - 18: Straight, flush, two pair, set on a wet, connected flop
            - 19: Set on a dry, unconnected flop
            - 20: Full house, quads, straight flush
        """
        current_hand = PokerHand(self.card_list)
        # Extract board and sort it
        board = self.card_list[2:]
        for i in range(4):
            already_sorted = True
            for j in range(3 - i):
                if board[j] > board[j + 1]:
                    board[j], board[j + 1] = board[j + 1], board[j]
                already_sorted = False
            if already_sorted:
                break
        hand_rank = current_hand.classify_hand()
        best_five = current_hand.best_five
        s_draw, s_outs = Draw(self.card_list).straight_draw()
        f_draw, f_suit = Draw(self.card_list).flush_draw()
        if hand_rank in hand_ranks[1:]:
            return 4
        elif f_draw:
            return 3
        elif hand_rank == 'One pair':
            if len(np.unique([self.flop[0][0], self.flop[1][0], self.flop[2][0]])) == 3:
                for card in self.hand_dealt:
                    # Top, middle, or bottom pair
                    if card[0] == self.flop[0][0]:
                        return 3
                    if card[0] == self.flop[1][0]:
                        return 2
                    if card[0] == self.flop[2][0]:
                        return 1
            else:
                return 0
        elif s_draw and s_outs == 'Two':
            return 2
        elif s_draw and s_outs == 'One':
            return 1
        else:
            return 0

    def good_river(self):
        current_hand = PokerHand(self.card_list)
        # Extract board and sort it
        board = self.card_list[2:]
        for i in range(5):
            already_sorted = True
            for j in range(4 - i):
                if board[j] > board[j + 1]:
                    board[j], board[j + 1] = board[j + 1], board[j]
                already_sorted = False
            if already_sorted:
                break
        hand_rank = current_hand.classify_hand()
        best_five = current_hand.best_five
        if hand_rank in hand_ranks[1:]:
            return 4
        else:
            return 0