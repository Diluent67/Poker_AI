from Setup import *
from Action import *


class Game:
    """Plays out a round of poker starting with preflop action.

    Args:
        num_players (int): Number of players at the table
        starting_stacks (list): Chip counts for each player at the table
        small_blind (float): Value of small blind
        big_blind (float): Value of big blind

    Attributes:
        action (Log): An instance of the Log class. This keeps track of all actions at the table
        temp_card_holder (dict): Contains the dealt hand for each player
        dealer (Dealer): An instance of the Dealer class
    """

    def __init__(self, num_players, small_blind, big_blind, starting_stacks):
        self.num_players = num_players
        self.action = Log(num_players)
        self.stacks = starting_stacks
        self.action.add_stacks(starting_stacks)
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.flop_cards = None
        self.turn_cards = None
        self.river_cards = None
        self.temp_card_holder = {}
        for i in range(num_players):
            self.temp_card_holder[i + 1] = 0
        self.total_pot = 0
        self.dealer = Dealer()

    def display_log(self, on_flop=False, on_turn=False, on_river=False):
        print("=" * 40)
        if on_flop:
            print("Board: " + str(self.flop_cards).strip("[]'").replace("', '", " "))
        if on_turn:
            print("Board: " + str(self.flop_cards).replace('[', '').replace(']', '') + " " + str(self.turn_cards))
        if on_river:
            print("Board: " + str(self.flop_cards).replace('[', '').replace(']', '') + " " + str(self.turn_cards)
                  + " " + str(self.river_cards))

        pot = self.get_pot()
        print("Pot: " + "{:.2f}".format(pot))

        for player_number in self.action.log:
            if not self.action.log[player_number]["In hand"] and not self.action.log[player_number]["Waiting"]:
                player_action = "Player " + str(player_number) + ": Folded"
                player_stack = "Stack: " + "{:.2f}".format(self.action.log[player_number]["Stack"])
                print('%-27s %s' % (player_action, player_stack))
            elif self.action.log[player_number]["Action"] == "ALL IN":
                player_action = "Player " + str(player_number) + ": All in " \
                                + "{:.2f}".format(self.action.log[player_number]["Bet"])
                player_stack = "Stack: " + "{:.2f}".format(self.action.log[player_number]["Stack"])
                print('%-27s %s' % (player_action, player_stack))
            else:
                player_action = "Player " + str(player_number) + ": " + "{:.2f}".format(
                    self.action.log[player_number]["Bet"])
                player_stack = "Stack: " + "{:.2f}".format(self.action.log[player_number]["Stack"])
                print('%-27s %s' % (player_action, player_stack))
        print("=" * 40)

    def get_pot(self):
        pot = 0
        for player_number in self.action.log:
            pot += self.action.log[player_number]["Bet"]
        if pot == 0:
            return self.total_pot
        elif pot < self.total_pot:
            self.total_pot = pot + self.total_pot
            return self.total_pot
        else:
            self.total_pot = pot
            return self.total_pot

    def options(self, position_num):
        if self.action.log[position_num]["Bet"] != self.action.current_bet():
            return "CALL/RAISE/FOLD: "
        else:
            return "CHECK/BET/FOLD: "

    def check_for_all_in(self, bet, position_num, action):
        previous_bet = self.action.log[position_num]["Bet"]
        if action == "CALL" and previous_bet != 0:
            difference = bet - previous_bet
            if self.action.log[position_num]["Stack"] <= difference:
                return True
        elif action == "RAISE" and previous_bet != 0:
            difference = bet - previous_bet
            if self.action.log[position_num]["Stack"] <= difference:
                return True
        else:
            if self.action.log[position_num]["Stack"] <= bet:
                return True
        return False

    def preflop(self):
        # Setting up poker game
        flop_exists = False
        end_of_round = False
        current_position = 1

        # Deal cards to the table
        for i in range(self.num_players):
            dealt = self.dealer.deal_hand()
            self.temp_card_holder[current_position] = dealt
            if current_position == 8:
                self.temp_card_holder[current_position] = ['8h', '9h']
            current_position += 1
            if current_position == self.num_players + 1:
                current_position = 3
                break

        # Preflop action all around
        end_preflop = False
        display_blinds = True
        while not end_preflop:
            # Handle the small and big blinds to start preflop play
            if display_blinds:
                self.action.add(1, action='SB', bet=self.small_blind, waiting=True, in_hand=True,
                                current_bet=self.small_blind)
                self.action.add(2, action='BB', bet=self.big_blind, waiting=True, in_hand=True,
                                current_bet=self.big_blind)
                self.display_log()
                print("\n")
                display_blinds = False

            # Stop round if everyone's turn is finished or if everyone's folded except for one player
            flag_done = True
            active_players = []
            for i in range(1, self.num_players + 1):
                if self.action.log[i]["Waiting"] and self.action.log[i]["In hand"]:
                    flag_done = False
                if self.action.log[i]["In hand"]:
                    active_players.append(i)
            if flag_done:
                end_preflop = True
            if len(active_players) == 1:
                end_of_round = True
                end_preflop = True
                self.action.log[active_players[0]]['Stack'] += self.get_pot()
                print("Player {} won {}".format(active_players[0], "{:.2f}".format(self.get_pot())))

            # Model playing
            # if current_position == position and action.log[current_position]["In hand"] \
            #         and action.log[current_position]["Waiting"]:
            if self.action.log[current_position]["In hand"] and self.action.log[current_position]["Waiting"] \
                    and not end_preflop:
                print("Player " + str(current_position) + " Hand: " + str(self.temp_card_holder[current_position])
                      .strip("[]'").replace("', '", " "))
                # game = Action(temp_card_holder[position], position, num_players, stack, small_blind, big_blind,
                #               get_pot(), action)
                game = Action(self.temp_card_holder[current_position], current_position, self.num_players,
                              self.action.log[current_position]['Stack'], self.small_blind, self.big_blind,
                              self.get_pot(), self.action)
                to_do = game.preflop_action()
                if len(to_do.split()) == 2:
                    if len(to_do.split()[1]) >= 10:
                        rounded = float(to_do.split()[1])
                        print(to_do.split()[0] + ' ' + "{:.2f}".format(rounded))
                    else:
                        print(to_do)
                else:
                    print(to_do)
                if to_do.split()[0].upper() == "FOLD":
                    self.action.add(current_position, action="FOLD", waiting=False, in_hand=False)
                if to_do.split()[0].upper() == "RAISE":
                    raise_amt = round(float(to_do.split()[1]), 2)
                    if self.check_for_all_in(raise_amt, current_position, "RAISE"):
                        self.action.add(current_position, action="ALL IN",
                                        bet=self.action.log[current_position]['Stack']
                                        + self.action.log[current_position]['Bet'], waiting=False, in_hand=True,
                                        current_bet=self.action.log[current_position]['Stack'] +
                                        self.action.log[current_position]['Bet'], note="ALL IN")
                    else:
                        self.action.add(current_position, action="RAISE", bet=float(raise_amt), waiting=False,
                                        in_hand=True, current_bet=raise_amt)
                    self.action.new_raise(current_position, raise_amt)
                if to_do.split()[0].upper() == "CALL":
                    current_bet = self.action.current_bet()
                    self.action.add(current_position, action="CALL", bet=current_bet, waiting=False, in_hand=True,
                                    current_bet=current_bet)
                self.display_log()
                print("\n")

            # # If a turn needs to be made
            # elif action.log[current_position]["Waiting"] or action.log[current_position]["In hand"]:
            #     print("Player " + str(current_position) + " Hand: " + str(temp_card_holder[current_position]).strip("[]'")
            #           .replace("', '", " "))
            #     valid_option_chosen = False
            #     while not valid_option_chosen:
            #         button = input(options(current_position))
            #         if button.upper() == "FOLD":
            #             action.add(current_position, action="FOLD", waiting=False, in_hand=False)
            #             valid_option_chosen = True
            #         elif button.upper() == "CALL":
            #             current_bet = action.current_bet()
            #             if check_for_all_in(current_bet, current_position):
            #                 action.add(current_position, action="ALL IN", bet=action.log[current_position]['Stack']
            #                                                                   + action.log[current_position]['Bet'],
            #                            waiting=False, in_hand=True,
            #                            current_bet=action.log[current_position]['Stack']
            #                                        + action.log[current_position]['Bet'], note="ALL IN")
            #             else:
            #                 action.add(current_position, action="CALL", bet=current_bet, waiting=False, in_hand=True,
            #                            current_bet=current_bet)
            #             valid_option_chosen = True
            #         elif button.upper() == "RAISE":
            #             valid_raise_chosen = False
            #             while not valid_raise_chosen:
            #                 raise_amt = float(input("RAISE TO: "))
            #                 if check_for_all_in(raise_amt, current_position):
            #                     action.add(current_position, action="ALL IN", bet=action.log[current_position]['Stack']
            #                                                                       + action.log[current_position]['Bet'],
            #                                waiting=False, in_hand=True,
            #                                current_bet=action.log[current_position]['Stack']
            #                                            + action.log[current_position]['Bet'], note="ALL IN")
            #                     valid_raise_chosen = True
            #                 else:
            #                     if action.current_bet() == big_blind:
            #                         if raise_amt >= big_blind * 2:
            #                             action.add(current_position, action="RAISE", bet=raise_amt, waiting=False,
            #                                        in_hand=True, current_bet=raise_amt)
            #                             valid_raise_chosen = True
            #                     else:
            #                         if len(action.all_raises) == 1:
            #                             difference = action.all_raises[0] - big_blind
            #                         else:
            #                             difference = action.all_raises[-1] - action.all_raises[-2]
            #                         b = action.current_bet()
            #                         if raise_amt >= round(action.current_bet() + difference, 2):
            #                             action.add(current_position, action="RAISE", bet=raise_amt, waiting=False,
            #                                        in_hand=True, current_bet=raise_amt)
            #                             valid_raise_chosen = True
            #                 if not valid_raise_chosen:
            #                     print("Invalid raise offered.")
            #             action.new_raise(current_position, raise_amt)
            #             valid_option_chosen = True
            #         else:
            #             print("Invalid option offered.")
            #     display_log()
            #     print("\n")

            current_position += 1
            if current_position == self.num_players + 1:
                current_position = 1

    def flop(self):
        # Flop action all around
        end_flop = False
        for i in range(1, self.num_players + 1):
            if not self.action.log[i]['In hand']:
                self.action.remove_player(i)
        self.action.renew()

        # Flop stuff
        flop_exists = True
        self.flop_cards = self.dealer.flop()
        self.display_log(on_flop=True)

        while not end_flop:
            for player in self.action.log:
                print("Player " + str(player) + " Hand: " + str(self.temp_card_holder[player])
                      .strip("[]'").replace("', '", " "))
                buttons = self.options(player)
                button = input(buttons)
                if button == "FOLD":
                    self.action.add(player, action="FOLD", waiting=False, in_hand=False)
                if button == "CHECK":
                    self.action.add(player, action="CHECK", waiting=False, in_hand=True)
                if button == "CALL":
                    current_bet = self.action.current_bet()
                    self.action.add(player, action="CALL", bet=current_bet, waiting=False, in_hand=True,
                                    current_bet=current_bet)
                if button == "Raise":
                    raise_amt = input("Raise to: ")
                    self.action.add(player, action="Raise", bet=float(raise_amt), waiting=False, in_hand=True,
                                    current_bet=float(raise_amt))
                    self.action.new_raise(player, raise_amt)
                if button == "BET":
                    bet_amt = input("BET: ")
                    self.action.add(player, action="BET", bet=float(bet_amt), waiting=False, in_hand=True,
                                    current_bet=float(bet_amt))
                    self.action.new_bet(player)
                self.display_log(on_flop=True)
                print("\n")

                # Stop round if everyone's turn is finished
                flag_done = True
                for player_num in self.action.log:
                    if self.action.log[player_num]["Waiting"] and self.action.log[player_num]["In hand"]:
                        flag_done = False
                        break
                if flag_done:
                    end_flop = True
                    break
    #
    # # Turn action all around
    # end_turn = False
    # for player in action.log.copy():
    #     if not action.log[player]['In hand']:
    #         action.remove_player(player)
    # action.renew()
    #
    # # Turn stuff
    # turn = dealer.turn()
    # display_log(on_turn=True)
    #
    # while not end_turn:
    #     for player in action.log:
    #         print("Player " + str(player) + " Hand: " + str(temp_card_holder[player]))
    #         buttons = options(player)
    #         button = input(buttons)
    #         if button == "FOLD":
    #             action.add(player, action="FOLD", waiting=False, in_hand=False)
    #         if button == "CHECK":
    #             action.add(player, action="CHECK", waiting=False, in_hand=True)
    #         if button == "CALL":
    #             current_bet = action.current_bet()
    #             action.add(player, action="CALL", bet=current_bet, waiting=False, in_hand=True,
    #                        current_bet=current_bet)
    #         if button == "Raise":
    #             raise_amt = input("Raise to: ")
    #             action.add(player, action="Raise", bet=float(raise_amt), waiting=False, in_hand=True,
    #                        current_bet=float(raise_amt))
    #             action.new_raise(player, raise_amt)
    #         if button == "BET":
    #             bet_amt = input("BET: ")
    #             action.add(player, action="BET", bet=float(bet_amt), waiting=False, in_hand=True,
    #                        current_bet=float(bet_amt))
    #             action.new_bet(player)
    #         display_log()
    #         print("\n")
    #
    #         # Stop round if everyone's turn is finished
    #         flag_done = True
    #         for player_num in action.log:
    #             if action.log[player_num]["Waiting"] and action.log[player_num]["In hand"]:
    #                 flag_done = False
    #                 break
    #         if flag_done:
    #             end_turn = True
    #             break
    #
    # # River action all around
    # end_river = False
    # for player in action.log.copy():
    #     if not action.log[player]['In hand']:
    #         action.remove_player(player)
    # action.renew()
    #
    # # River stuff
    # river = dealer.river()
    # display_log(on_river=True)
    #
    # while not end_river:
    #     for player in action.log:
    #         print("Player " + str(player) + " Hand: " + str(temp_card_holder[player]))
    #         buttons = options(player)
    #         button = input(buttons)
    #         if button == "FOLD":
    #             action.add(player, action="FOLD", waiting=False, in_hand=False)
    #         if button == "CHECK":
    #             action.add(player, action="CHECK", waiting=False, in_hand=True)
    #         if button == "CALL":
    #             current_bet = action.current_bet()
    #             action.add(player, action="CALL", bet=current_bet, waiting=False, in_hand=True,
    #                        current_bet=current_bet)
    #         if button == "RAISE":
    #             raise_amt = input("Raise to: ")
    #             action.add(player, action="RAISE", bet=float(raise_amt), waiting=False, in_hand=True,
    #                        current_bet=float(raise_amt))
    #             action.new_raise(player, raise_amt)
    #         if button == "BET":
    #             bet_amt = input("BET: ")
    #             action.add(player, action="BET", bet=float(bet_amt), waiting=False, in_hand=True,
    #                        current_bet=float(bet_amt))
    #             action.new_bet(player)
    #         display_log()
    #         print("\n")
    #
    #         # Stop round if everyone's turn is finished
    #         flag_done = True
    #         for player_num in action.log:
    #             if action.log[player_num]["Waiting"] and action.log[player_num]["In hand"]:
    #                 flag_done = False
    #                 break
    #         if flag_done:
    #             end_river = True
    #             break
