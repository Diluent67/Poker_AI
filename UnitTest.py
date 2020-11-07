from unittest.mock import patch
from Game import *

poker_game = Game(9, 0.05, 0.10, [10]*9)

# poker_game = __import__("Game")
user_input = [
]

# position = 5
# num_players = 8
# stack = 10
# small_blind = 0.05
# big_blind = 0.10
# flop_cards = None
# turn = None
# river = None

# with patch('builtins.input', side_effect=user_input):
#     raised = False
#     try:
#         stacks = poker_game.preflop()
#     except StopIteration:
#         print("Error: More inputs needed")
#     except:
#         raise
poker_game.preflop()
poker_game.flop()


# with patch('builtins.input', return_value="Call"), patch('sys.stdout', new=StringIO()) as fake_out:
#     __import__("Game.py")
# class PokerGameTest(unittest.TestCase):
#     def runTest(self, given_answer, expected_out):
#         with patch('builtins.input', return_value=given_answer), patch('sys.stdout', new=StringIO()) as fake_out:
#             __import__("Game.py")
#             # self.assertEqual(fake_out.getvalue().strip(), expected_out)
#
#     def testNo(self):
#         self.runTest('o', 'you entered no')
#
#     def testYes(self):
#         self.runTest('yes', 'you entered yes')
#
#
# if __name__ == '__main__':
#     unittest.main()
