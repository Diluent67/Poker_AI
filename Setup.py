import random
import collections

# Possible hands
suits = ['h', 'd', 's', 'c']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
premium = ['T', 'J', 'Q', 'K', 'A']
four_betting_range = ['AA', 'KK', 'QQ', 'AKs']
three_betting_range = ['AA', 'KK', 'QQ', 'AKs', 'JJ', 'TT', 'AQs', 'AKo', 'KQs', 'AQo', 'AJs', '99']
hand_ranks = ['One pair', 'Two pair', 'Three of a kind', 'Straight', 'Flush', 'Full house',
              'Four of a kind', 'Straight flush']


class Card:
    """Defines a card given a rank and a suit"""

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def show(self):
        return self.rank + self.suit


class Deck:
    """Creates the deck of 52 playing cards"""

    def __init__(self):
        self.contents = []
        self.contents = [Card(rank, suit) for rank in ranks for suit in suits]
        random.shuffle(self.contents)

    def show(self):
        deck = []
        for card in self.contents:
            deck.append(card.show())
        return deck

    def update(self, hand, flop=None, turn=None, river=None):
        deck = self.show()
        updated_deck = set(deck) - set(hand)
        if flop is not None:
            updated_deck = updated_deck - set(flop)
            if turn is not None:
                updated_deck = updated_deck - set(list(turn))
                if river is not None:
                    updated_deck = updated_deck - set(list(river))
        return list(updated_deck)


class Dealer:
    """Deals out hands and the community cards"""

    def __init__(self):
        self.deck = Deck().show()
        self.num_dealt = 0
        self.flopped = False
        self.turned = False
        self.rivered = False

    def deal_hand(self):
        deck = self.deck
        hand_dealt = deck[self.num_dealt: self.num_dealt + 2]
        self.num_dealt = self.num_dealt + 2
        return hand_dealt

    def flop(self):
        deck = self.deck
        flop = deck[self.num_dealt + 1: self.num_dealt + 4]
        self.flopped = True
        return flop

    def turn(self):
        deck = self.deck
        turn = deck[self.num_dealt + 5]
        self.turned = True
        return turn

    def river(self):
        deck = self.deck
        river = deck[self.num_dealt + 7]
        self.rivered = True
        return river

    def cards_out(self):
        board = []
        if self.flopped:
            board += self.flop()
        if self.turned:
            board += [self.turn()]
        if self.rivered:
            board += [self.river()]
        return self.deal_hand() + board

    def run_out(self):
        flop = self.flop()
        turn = self.turn()
        river = self.river()
        return flop + [turn] + [river]


class PokerHand:
    """For use in classifying hand ranks

    Args:
        card_list (list): A list containing the hand dealt along with the cards on the board
    """

    def __init__(self, card_list):
        self.card_list = card_list
        self.num_cards = len(card_list)
        self.best_five = None

    def classify_hand(self):
        hand = []
        rank_dict = collections.defaultdict(int)
        suit_dict = collections.defaultdict(int)
        for card in self.card_list:
            rank_dict[card[0]] += 1
            suit_dict[card[1]] += 1

        # One pair
        if len(rank_dict) == self.num_cards - 1:
            hand.append('One pair')

        # Three of a kind or two pair
        if len(rank_dict) == self.num_cards - 2:
            if 3 in rank_dict.values():
                hand.append('Three of a kind')
            else:
                hand.append('Two pair')

        # Four of a kind or full house or two pair
        if len(rank_dict) == self.num_cards - 3:
            if 4 in rank_dict.values():
                hand.append('Four of a kind')
            elif 3 in rank_dict.values():
                hand.append('Full house')
            else:
                hand.append('Two pair')

        # Four of a kind or full house
        if len(rank_dict) == self.num_cards - 4:
            if 4 in rank_dict.values():
                hand.append('Four of a kind')
            else:
                hand.append('Full house')

        # Four of a kind
        if len(rank_dict) == self.num_cards - 5:
            hand.append('Four of a kind')

        # Flush or straight
        straight, flush, straight_flush = False, False, False
        if any(x in suit_dict.values() for x in [5, 6, 7]):
            flush = True
            flush_suit = max(suit_dict, key=suit_dict.get)

        straight_ranks = ['A'] + ranks
        for index, rank in enumerate(straight_ranks[0:9]):
            if all(straight_ranks[index + n] in rank_dict.keys() for n in range(0, 5)):
                straight = True
                straight_cards = [straight_ranks[index + n] for n in range(0, 5)]

        if straight and not flush:
            hand.append('Straight')
        elif flush and not straight:
            hand.append('Flush')
        elif flush and straight:
            if all(card + flush_suit in self.card_list for card in straight_cards):
                hand.append('Straight flush')
            else:
                hand.append('Flush')

        # Selection
        if len(hand) == 0:
            high_card = max([ranks.index(x) for x in rank_dict.keys()])
            hand = '{} high'.format(ranks[high_card])
        elif len(hand) > 1:
            strongest = max([hand_ranks.index(classified) for classified in hand])
            hand = hand_ranks[strongest]
        else:
            hand = hand[0]

        # Find the best five cards
        best_five = []
        if hand == 'One pair':
            pair = [card for card, count in rank_dict.items() if count == 2]
            # Add the pair
            for card in self.card_list:
                if card[0] == pair[0]:
                    best_five += [card]
            # Add the remaining cards by rank
            for i in range(3):
                high_card = ranks[0] + 'g'
                for card in self.card_list:
                    if ranks.index(card[0]) >= ranks.index(high_card[0]) and card[0] != pair[0] \
                            and card not in best_five:
                        high_card = card
                best_five += [high_card]

        elif hand == 'Two pair':
            pairs = [card for card, count in rank_dict.items() if count == 2]
            if ranks.index(pairs[1]) > ranks.index(pairs[0]):
                pairs[0], pairs[1] = pairs[1], pairs[0]
            # Add the pairs
            for card in self.card_list:
                if card[0] == pairs[0]:
                    best_five += [card]
            for card in self.card_list:
                if card[0] == pairs[1]:
                    best_five += [card]
            # Add the remaining card by rank
            high_card = ranks[0] + 'g'
            for card in self.card_list:
                if ranks.index(card[0]) >= ranks.index(high_card[0]) and card[0] != pairs[0] and card[0] != pairs[1]:
                    high_card = card
            best_five += [high_card]

        elif hand == 'Three of a kind':
            trips = [card for card, count in rank_dict.items() if count == 3]
            # Add the trips
            for card in self.card_list:
                if card[0] == trips[0]:
                    best_five += [card]
            # Add the remaining cards by rank
            for i in range(2):
                high_card = ranks[0] + 'g'
                for card in self.card_list:
                    if ranks.index(card[0]) >= ranks.index(high_card[0]) \
                            and card[0] != trips[0] and card not in best_five:
                        high_card = card
                best_five += [high_card]

        elif hand == 'Four of a kind':
            quads = [card for card, count in rank_dict.items() if count == 4]
            # Add the quads
            for card in self.card_list:
                if card[0] == quads[0]:
                    best_five += [card]
            # Add the remaining card by rank
            high_card = ranks[0] + 'g'
            for card in self.card_list:
                if ranks.index(card[0]) >= ranks.index(high_card[0]) and card[0] != quads[0]:
                    high_card = card
            best_five += [high_card]

        elif hand == 'Full house':
            trips = [card for card, count in rank_dict.items() if count == 3]
            pairs = [card for card, count in rank_dict.items() if count == 2]
            if len(trips) > 1:
                if ranks.index(trips[1]) > ranks.index(trips[0]):
                    trips[0], trips[1] = trips[1], trips[0]
                pairs = trips[1]
            if len(pairs) > 1:
                if ranks.index(pairs[1]) > ranks.index(pairs[0]):
                    pairs[0], pairs[1] = pairs[1], pairs[0]
            # Add the full house
            for card in self.card_list:
                if card[0] == trips[0]:
                    best_five += [card]
            for card in self.card_list:
                if card[0] == pairs[0]:
                    if len(best_five) < 5:
                        best_five += [card]

        elif hand == "Straight":
            for straight_card in straight_cards:
                for card in self.card_list:
                    if straight_card == card[0]:
                        best_five += [card]
                        break

        elif hand == 'Flush':
            flush_cards = []
            for card in self.card_list:
                if card[1] == flush_suit:
                    flush_cards.append(card)
            for i in range(5):
                high_card = ranks[0] + 'g'
                for card in flush_cards:
                    if ranks.index(card[0]) >= ranks.index(high_card[0]) and card not in best_five:
                        high_card = card
                best_five += [high_card]

        elif hand == 'Straight flush':
            for index, rank in enumerate(straight_ranks[0:9]):
                straight_flush_count = 0
                straight_flush_list = []
                if all(straight_ranks[index + n] in rank_dict.keys() for n in range(0, 5)):
                    straight_cards = [straight_ranks[index + n] for n in range(0, 5)]
                    for straight_card in straight_cards:
                        for card in self.card_list:
                            if straight_card == card[0]:
                                if flush_suit == card[1]:
                                    straight_flush_count += 1
                                    straight_flush_list += [card]
                    if straight_flush_count == 5:
                        best_five.clear()
                        best_five += straight_flush_list

        self.best_five = best_five

        return hand


class Draw:
    """Classifies straight or flush draws if they exist

    Args:
        card_list (list): A list containing the hand dealt along with the cards on the board
    """

    def __init__(self, card_list):
        self.card_list = card_list
        self.num_cards = len(card_list)

    def straight_draw(self):
        rank_dict = collections.defaultdict(int)
        for card in self.card_list:
            rank_dict[card[0]] += 1

        def one_vs_two_outs(cards, possibilities):
            missing_card = list(set(cards) - set(list(rank_dict.keys())))[0]
            if len(possibilities) >= 2:
                return 'Two'
            else:
                return 'One'

        straight_draw, straight_info = False, None
        straight_ranks = ['A'] + ranks
        possible_straights = []
        for index, rank in enumerate(straight_ranks[0:9]):
            card_num = 0
            for n in range(0, 5):
                one_of_five = straight_ranks[index + n]
                if one_of_five in rank_dict.keys():
                    card_num += 1
            if card_num == 4:
                straight_draw = True
                straight_cards = straight_ranks[index + 0:index + 5]
                possible_straights.append(straight_cards)
                straight_info = one_vs_two_outs(straight_cards, possible_straights)
        return straight_draw, straight_info

    def flush_draw(self):
        suit_dict = collections.defaultdict(int)
        for card in self.card_list:
            suit_dict[card[1]] += 1

        flush_draw, flush_draw_suit = False, None
        if 4 in suit_dict.values():
            flush_draw = True
            flush_draw_suit = max(suit_dict, key=suit_dict.get)
        return flush_draw, flush_draw_suit
