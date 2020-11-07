from Setup import *
from Preflop import *
from Postflop import *


class Action:
    """Main class used to suggest an action (call/check/raise/fold)
    Utilizes information from the table and previous actions

    Args:
        card_list (list): A list containing the hand dealt along with the cards on the board
        position (int): Seat number, using the small blind as 1 and incrementing by 1 after each player
        num_players (int): Number of players at the table
        stack (int): Chip count
        small_blind (float): Value of small blind
        big_blind (float): Value of big blind
        pot (int): Total chips in the pot
        action (Log): An instance of the Log class
    """

    def __init__(self, card_list, position, num_players, stack, small_blind, big_blind, pot, action):
        self.card_list = card_list
        self.hand_dealt = card_list[0:2]
        self.position = position
        self.num_players = num_players
        self.stack = stack
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.pot = pot
        self.action = action

    def stage(self):
        if len(self.card_list) == 2:
            return "Preflop"
        if len(self.card_list) == 5:
            return "Flop"
        if len(self.card_list) == 6:
            return "Turn"
        if len(self.card_list) == 7:
            return "River"

    def spr(self):
        return self.stack / self.pot

    def pot_odds(self, player):
        numerator = self.pot
        denominator = self.current_bet() - self.action.log[player]['Bet']
        return numerator / denominator

    def num_raises(self):
        """Determines the number of raises that have transpired

        Returns:
            An integer value (e.g. 1 if only one raise has occurred, 2 if a three-bet occurred, etc.)
        """
        return len(self.action.all_raises)

    def num_players_in_hand(self):
        """Determines the number of players in the hand"""
        num_players = 0
        for player in self.action.log:
            if self.action.log[player]['In hand']:
                num_players += 1
        return num_players

    def num_players_behind(self):
        """Determines the number of players still waiting their turn after you"""
        num_players = 0
        for player in self.action.log:
            if self.action.log[player]['Waiting']:
                num_players += 1
        return num_players

    def num_callers(self):
        """Determines the number of players in the hand that have called a bet or raise"""
        callers = 0
        for player in self.action.log:
            if self.action.log[player]['Bet'] == self.current_bet():
                callers += 1
        return callers - 1

    def current_bet(self):
        """Returns the previous bet if one exists"""
        ind_bets = []
        for player in self.action.log:
            ind_bets.append(self.action.log[player]['Current bet'])
        return max(ind_bets)

    def aggressor(self, preflop=False, flop=False, turn=False):
        """Returns the preflop aggressor"""
        if preflop:
            for player in self.action.log:
                if "Preflop aggressor" in self.log[player]["Notes"]:
                    return player
        if flop:
            for player in self.action.log:
                if "Flop aggressor" in self.log[player]["Notes"]:
                    return player
        if turn:
            for player in self.action.log:
                if "Flop aggressor" in self.log[player]["Notes"]:
                    return player
        return None

    def bet_sizing(self, value=False, semi_bluff=False):
        if value:
            frequency = random.uniform(0, 1)
            if frequency >= 0.5:
                return 0.5 * self.pot
            elif 0.5 < frequency <= 0.75:
                return 0.75 * self.pot
            else:
                return 0
        if semi_bluff:
            frequency = random.uniform(0, 1)
            if frequency >= 0.5:
                return 0.5 * self.pot
            elif 0.5 < frequency <= 0.75:
                return 0.75 * self.pot
            else:
                return 0
        return

    def check_raise_sizing(self, value=False, semi_bluff=False):
        if value:
            frequency = random.uniform(0, 1)
            if frequency >= 0.5:
                return 0.5 * self.pot
            elif 0.5 < frequency <= 0.75:
                return 0.75 * self.pot
            else:
                return 0
        if semi_bluff:
            frequency = random.uniform(0, 1)
            if frequency >= 0.5:
                return 0.5 * self.pot
            elif 0.5 < frequency <= 0.75:
                return 0.75 * self.pot
            else:
                return 0
        return

    def in_position(self):
        """Determines if you have position on the last aggressor"""
        if self.stage() == "Flop":
            return self.position > self.aggressor(preflop=True)
        if self.stage() == "Turn":
            return self.position > self.aggressor(flop=True)
        if self.stage() == "River":
            return self.position > self.aggressor(turn=True)

    def preflop_action(self):
        """Suggests a preflop action

        Returns:
            One of the following strings - call, check, raise, or fold
        """
        # Uses the position number to determine the relative position (small/big/early/middle/late)
        position = None
        if self.position == 1:
            position = 'small'
        if self.position == 2:
            position = 'big'
        if self.num_players == 9:
            if self.position == 3 or self.position == 4:
                position = 'early'
            if 5 <= self.position <= 7:
                position = 'middle'
            if self.position == 8 or self.position == 9:
                position = 'late'
        if self.num_players == 8:
            if self.position == 3 or self.position == 4:
                position = 'early'
            if self.position == 5 or self.position == 6:
                position = 'middle'
            if self.position == 7 or self.position == 8:
                position = 'late'
        if self.num_players == 6 or self.num_players == 7:
            if self.position == 3:
                position = 'early'
            if self.position == 4 or self.position == 5:
                position = 'middle'
            if self.position == 6 or self.position == 7:
                position = 'late'
        if self.num_players == 4 or self.position == 5:
            if self.position == 3:
                position = 'early'
            if self.position == 4:
                position = 'middle'
            if self.position == 5:
                position = 'late'
        if self.num_players <= 3:
            return "Sit out"

        # Returns suggested action by the number of previous raises
        if self.num_raises() == 0:
            preflop_assessment = Preflop(self.hand_dealt[0], self.hand_dealt[1], position)
            if preflop_assessment.playable():
                return "Raise " + str((3 * self.current_bet()) + self.num_callers() * self.big_blind)
            else:
                return "Fold"

        if self.num_raises() == 1:
            preflop_assessment = Preflop(self.hand_dealt[0], self.hand_dealt[1], position)
            suggested_action = preflop_assessment.facing_raise()
            if suggested_action == 0:
                return "Fold"
            if suggested_action == 1:
                if self.pot_odds(self.position) < 1.25:
                    return "Fold"
                else:
                    return "Call"
            if suggested_action == 2:
                # Raise if less than two-thirds of the table have flatted the raise
                if self.num_callers() / self.num_players <= 0.65:
                    return "Raise " + str((3 * self.current_bet()) + self.num_callers() * self.big_blind)
                # Call otherwise given the odds
                else:
                    return "Call"
            if suggested_action == 3:
                return "Raise " + str((3 * self.current_bet()) + self.num_callers() * self.big_blind)

        if self.num_raises() == 2:
            preflop_assessment = Preflop(self.hand_dealt[0], self.hand_dealt[1], position)
            suggested_action = preflop_assessment.facing_three_bet()
            if suggested_action == 0:
                return "Fold"
            elif suggested_action == 1:
                return "Call"
            elif suggested_action == 2:
                return "Raise " + str((3 * self.current_bet()) + self.num_callers() * self.big_blind * 3)

        if self.num_raises() >= 3:
            preflop_assessment = Preflop(self.hand_dealt[0], self.hand_dealt[1], position)
            suggested_action = preflop_assessment.facing_four_bet()
            if suggested_action == 0:
                return "Fold"
            elif suggested_action == 1:
                return "Call"
            elif suggested_action == 2:
                return "Call or five-bet"

    def flop_action(self):
        flop_assessment = Postflop(self.card_list)
        suggested_action = flop_assessment.flop_scenario()

        # Committed to the pot
        if self.spr() <= 3:
            # Stack off with top pair or better
            return

        # When action checks to you
        if self.current_bet() == 0:
            # Preflop aggressor
            if self.aggressor(preflop=True) == self.position:
                # Slow-play monsters
                if suggested_action >= 7:
                    return "Check"
                # C-bet for value
                elif 5 <= suggested_action < 7:
                    return "Bet " + str(self.bet_sizing(value=True))
                # C-bet as a semi-bluff
                elif 3 <= suggested_action < 4:
                    return "Bet " + str(self.bet_sizing(semi_bluff=True))
                # C-bet with range advantage (bluff)
                elif 0 <= suggested_action < 2:
                    return "Bet " + str(self.bet_sizing(c_bet=True))
                # Check with showdown value
                elif 4 <= suggested_action < 5:
                    return "Check"
                # C-bet with Ace high
                elif 1 <= suggested_action < 2:
                    return "Bet " + str(self.bet_sizing(c_bet=True))
                # Check rest of range
                else:
                    return "Check"
            # Out of position to the preflop aggressor
            if not self.in_position():
                return "Check"
            # In position to the preflop aggressor
            if self.in_position():
                # C-bet for value
                if 5 <= suggested_action < 7:
                    return "Bet " + str(self.bet_sizing(value=True))
                # Check otherwise
                else:
                    return "Check"

        # When facing a bet
        if self.current_bet() != 0 and self.num_raises() == 0:
            # No callers so far and 2+ players behind
            if self.num_callers() == 0 and self.num_players_behind() >= 2:
                if suggested_action >= 5:
                    return "Call"
                elif 4 <= suggested_action < 5:
                    return "Call"
                elif 3 <= suggested_action < 4:
                    return "Call"
                else:
                    return "Fold"
            # No callers so far and 0-1 players behind
            if self.num_callers() == 0 and self.num_players_behind() <= 1:
                if suggested_action >= 5:
                    return "Call"
                elif 4 <= suggested_action < 5:
                    return "Call"
                elif 3 <= suggested_action < 4:
                    return "Call"
                else:
                    return "Fold"
            # 1 caller so far
            if self.num_callers() == 1:
                if suggested_action >= 5:
                    return "Call"
                elif 3 <= suggested_action < 4:
                    return "Call"
                else:
                    return "Fold"
            # 2+ callers so far
            if self.num_callers() >= 2:
                if suggested_action >= 5:
                    return "Call"
                elif 3 <= suggested_action < 4:
                    if self.pot_odds() >= 0.35:
                        return "Call"

                else:
                    return "Fold"

        # When facing a raise
        if self.current_bet() != 0 and self.num_raises() == 1:
            # No callers so far
            if self.num_callers() == 0:
                if suggested_action >= 5:
                    return "Call"
                elif 3 <= suggested_action < 4:
                    if suggested_action == 3.7:
                        return "Call"
                    if suggested_action == 3.6:
                        return "Call"
                    if suggested_action == 3.5:
                        return "Call"
                    if suggested_action == 3.4 or suggested_action == 3.3:
                        if self.pot_odds(self.position) >= 5:
                            return "Call"
                        else:
                            return "Fold"
                    if suggested_action == 3.1 or suggested_action == 3.2:
                        if self.pot_odds(self.position) >= 11:
                            return "Call"
                        else:
                            return "Fold"
                else:
                    return "Fold"
            # 1+ callers so far
            if self.num_callers() >= 1:
                if suggested_action >= 5:
                    if suggested_action == 5.1:
                        return "Fold"
                    else:
                        return "Call"
                elif 3 <= suggested_action < 4:
                    if suggested_action == 3.7:
                        return "Call"
                    if suggested_action == 3.6:
                        return "Call"
                    if suggested_action == 3.5:
                        return "Call"
                    if suggested_action == 3.4 or suggested_action == 3.3:
                        if self.pot_odds(self.position) >= 5:
                            return "Call"
                        else:
                            return "Fold"
                    if suggested_action == 3.1 or suggested_action == 3.2:
                        if self.pot_odds(self.position) >= 11:
                            return "Call"
                        else:
                            return "Fold"
                else:
                    return "Fold"

        # When facing a three-bet and above
        if self.current_bet() != 0 and self.num_raises() >= 2:
            if suggested_action >= 6:
                return "Call"
            elif 5 <= suggested_action < 6:
                if suggested_action >= 5.5:
                    return "Call"
            else:
                return "Check"

    def turn_action(self):
        return

    def river_action(self):
        return


class Log:
    """Keeps track of actions at the table

    Args:
        num_players (int): The number of players at the table

    Attributes:
        log (dict): A dictionary of dictionaries representing all previous players' actions. Keys are position
            numbers on the table, while each inner dictionary contains information from that player.
    """

    def __init__(self, num_players):
        self.num_players = num_players
        self.log = {}
        for i in range(1, num_players + 1):
            self.log[i] = {"Action": None, "Bet": 0, "Waiting": True, "In hand": True,
                           "Current bet": 0, "Stack": None, "Notes": []}
        self.all_raises = []
        self.preflop_log = None
        self.flop_log = None
        self.turn_log = None

    def add(self, position, action=None, bet=None, waiting=None, in_hand=None, current_bet=None,
            note=None):
        if action is not None:
            self.log[position]["Action"] = action
        if bet is not None:
            previous_bet = self.log[position]["Bet"]
            if action == "CALL" and previous_bet != 0:
                difference = bet - previous_bet
                self.log[position]["Stack"] -= difference
            elif action == "RAISE" and previous_bet != 0:
                difference = bet - previous_bet
                self.log[position]["Stack"] -= difference
            elif action == "ALL IN":
                if previous_bet != 0:
                    difference = bet - previous_bet
                    self.log[position]["Stack"] -= difference
                else:
                    self.log[position]["Stack"] -= bet
            else:
                self.log[position]["Stack"] -= bet
            if self.current_bet() < bet:
                if self.preflop_log is None:
                    self.log[position]["Notes"].append("Preflop aggressor")
                    self.clear_aggressors(position)
                elif self.flop_log is None:
                    self.log[position]["Notes"].append("Flop aggressor")
                    self.clear_aggressors(position)
                elif self.turn_log is None:
                    self.log[position]["Notes"].append("Turn aggressor")
                    self.clear_aggressors(position)
            self.log[position]["Bet"] = bet
        if waiting is not None:
            self.log[position]['Waiting'] = waiting
        if in_hand is not None:
            self.log[position]['In hand'] = in_hand
        if current_bet is not None:
            self.log[position]["Current bet"] = current_bet
        if note is not None:
            self.log[position]["Notes"].append(note)

    def renew(self):
        if self.preflop_log is None:
            self.preflop_log = self.log.copy()
        elif self.flop_log is None:
            self.flop_log = self.log.copy()
        elif self.turn_log is None:
            self.turn_log = self.log.copy()
        for player, player_dict in self.log.items():
            self.log[player]["Action"] = None
            self.log[player]["Bet"] = 0
            self.log[player]["Waiting"] = True
            self.log[player]["In hand"] = True
            self.log[player]["Total raises"] = 0
            self.log[player]["Current bet"] = 0

    def clear_aggressors(self, aggressor):
        for player in self.log:
            if "Preflop aggressor" in self.log[player]["Notes"] and player != aggressor:
                self.log[player]["Notes"].remove("Preflop aggressor")

    def add_stacks(self, stacks):
        for player in self.log:
            self.log[player]["Stack"] = stacks[player - 1]

    def current_bet(self):
        ind_bets = []
        for player in self.log:
            ind_bets.append(self.log[player]['Current bet'])
        return max(ind_bets)

    def num_raises(self):
        return len(self.all_raises)

    def new_raise(self, position, raise_amt):
        for player in self.log:
            if player != position and self.log[player]["In hand"]:
                self.log[player]["Waiting"] = True
        self.all_raises.append(raise_amt)

    def new_bet(self, position):
        for player in self.log:
            if player != position and self.log[player]["In hand"]:
                self.log[player]["Waiting"] = True

    def remove_player(self, position):
        del self.log[position]
        self.num_players -= 1
