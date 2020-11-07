from Setup import *


class Preflop:
    """Used to assess preflop strength

    Args:
        card1 (str): A two-character string that contains the rank and suit of the first card
        card2 (str): A two-character string that contains the rank and suit of the second card
        position (str): One of the following strings that denotes position
            E.g. with a 9-handed table
            - "small": 1
            - "big": 2
            - "early": 3, 4
            - "middle": 5, 6, 7
            - "late": 8, 9

    Ranges: http://www.pokerhandrange.com/hand/3ses9pq7wg0rj45r998ase7en
    """

    def __init__(self, card1, card2, position):
        self.card1 = card1
        self.card2 = card2
        self.rank1 = card1[0]
        self.rank2 = card2[0]
        self.suit1 = card1[1]
        self.suit2 = card2[1]
        self.position = position

    def suited(self):
        if self.suit1 == self.suit2:
            return True
        else:
            return False

    def pockets(self):
        if self.rank1 == self.rank2:
            return True
        else:
            return False

    def connector(self):
        return any((ranks[i], ranks[i + 1]) == (self.rank1, self.rank2)
                   or (ranks[i + 1], ranks[i]) == (self.rank1, self.rank2)
                   or (ranks[0], ranks[-1]) == (self.rank1, self.rank2)
                   or (ranks[-1], ranks[0]) == (self.rank1, self.rank2) for i in range(len(ranks) - 1))

    def one_gapper(self):
        return any((ranks[i], ranks[i + 2]) == (self.rank1, self.rank2)
                   or (ranks[i + 2], ranks[i]) == (self.rank1, self.rank2)
                   or (ranks[1], ranks[-1]) == (self.rank1, self.rank2)
                   or (ranks[-1], ranks[1]) == (self.rank1, self.rank2) for i in range(len(ranks) - 2))

    def broadways(self):
        if self.rank1 in premium and self.rank2 in premium:
            return True
        else:
            return False

    def playable(self):
        """Determines if a hand is playable, accounting for position

        Returns:
            A boolean value
        """
        if self.position == 'early' or self.position == 'small':
            # 77+
            if self.pockets() and ranks.index(self.rank1) >= 5:
                return True
            # Suited broadways
            elif self.broadways() and self.suited():
                return True
            # AKo, AQo, AJo, KQo
            elif ranks.index(self.rank1) + ranks.index(self.rank2) >= 21:
                return True
            #  A5s, T9s
            elif self.rank1 + self.rank2 in ['A5', '5A', 'T9', '9T'] and self.suited():
                if random.uniform(0, 1) >= 0.75:
                    return True
            # Set mining if small blind
            elif self.pockets() and self.position == 'small':
                return True
            else:
                return False

        elif self.position == 'middle' or self.position == 'big':
            # 55+
            if self.pockets() and ranks.index(self.rank1) >= 3:
                return True
            # K8s+, Q9s+
            elif ranks.index(self.rank1) + ranks.index(self.rank2) >= 17 and self.suited():
                return True
            # A2s+
            elif (ranks.index(self.rank1) == 12 or ranks.index(self.rank2) == 12) and self.suited():
                return True
            # TJs, 9Ts, 89s, 78s, 67s
            elif self.connector() and self.suited():
                if ranks.index(self.rank1) + ranks.index(self.rank2) >= 9:
                    return True
            # J9s, T8s
            elif self.one_gapper() and self.suited():
                if ranks.index(self.rank1) + ranks.index(self.rank2) >= 14:
                    return True
            # AKo, AQo, AJo, KQo, KJo
            elif ranks.index(self.rank1) + ranks.index(self.rank2) >= 20:
                if self.rank1 + self.rank2 not in ['AT', 'TA']:
                    return True
            # Set mining if big blind
            elif self.pockets() and self.position == 'big':
                return True
            else:
                return False

        elif self.position == 'late':
            # 22+
            if self.pockets():
                return True
            # K8s+, Q8s+, J8s+, T8s+
            elif self.rank1 in premium and self.suited:
                if ranks.index(self.rank2) >= 6:
                    return True
            elif self.rank2 in premium and self.suited:
                if ranks.index(self.rank1) >= 6:
                    return True
            # A2s+
            elif (ranks.index(self.rank1) == 12 or ranks.index(self.rank2) == 12) and self.suited():
                return True
            # 89s, 78s, 67s, 56s, 45s
            elif self.connector() and self.suited():
                if ranks.index(self.rank1) + ranks.index(self.rank2) >= 5:
                    return True
            # 68s, 79s
            elif self.one_gapper() and self.suited():
                if ranks.index(self.rank1) + ranks.index(self.rank2) >= 10:
                    return True
            else:
                return False

        else:
            raise NameError('Invalid position name')

    def facing_raise(self):
        """Suggests an action when facing a raise

        Returns:
            An integer that represents varying degrees of action
            - 0: Fold
            - 1: Flat the raise
            - 2: Three-bet if optimal, but flat if good odds (drawing hands)
            - 3: Three-bet no matter what
        """
        if self.rank1 + self.rank2 in ['AA', 'KK', 'QQ', 'AK', 'KA', 'JJ']:
            return 3
        elif self.rank1 + self.rank2 in ['TT', '99', 'AQ', 'QA', 'KQ', 'QK', 'AJ', 'JA']:
            if self.rank1 + self.rank2 in ['KQ', 'QK', 'AJ', 'JA']:
                if self.suited():
                    return 2
                else:
                    return 1
            else:
                return 2
        elif self.playable():
            return 1
        else:
            return 0

    def facing_three_bet(self):
        """Suggests an action when facing a three-bet

        Returns:
            An integer that represents varying degrees of action
            - 0: Fold
            - 1: Flat
            - 2: Four-bet
        """
        if self.rank1 + self.rank2 in ['AA', 'KK', 'QQ']:
            return 2
        elif self.rank1 + self.rank2 == 'AK':
            if self.suited():
                if random.uniform(0, 1) >= 0.9:
                    return 2
                else:
                    return 1
            else:
                if random.uniform(0, 1) >= 0.75:
                    return 2
                else:
                    return 1
        elif self.facing_raise() >= 2:
            return 1
        else:
            return False

    def facing_four_bet(self):
        """Suggests an action when facing a four-bet

        Returns:
            An integer that represents varying degrees of action
            - 0: Fold
            - 1: Flat and play cautiously (JJ/QQ/AK)
            - 2: Five-bet or flat/jam flop/three-barrel (AA/KK)
        """
        if self.rank1 + self.rank2 in ['QQ', 'AK', 'KA', 'JJ']:
            return 1
        elif self.rank1 + self.rank2 in ['AA', 'KK']:
            return 2
        else:
            return 0
