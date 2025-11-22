import unittest
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)
BettingTicketHolder = None

if not BettingTicketHolder:
    from BettingTicketHolder import BettingTicketHolder

class TestBettingTicketHolder(unittest.TestCase):

    def setUp(self):
        self.amounts = {"blue": [2,2,3,5], "green": [2,2,3,5], "red": [2,2,3,5], "yellow": [2,2,3,5], "purple": [2,2,3,5]}
        self.betting_ticket = BettingTicketHolder.BettingTicket(3) # This is an individual ticket
        self.ticket_holder = BettingTicketHolder() # This is collection of tickets
        self.one_ticket = (3, 1, -1, -1, -1)
        self.camel_player = CamelPlayers()
    def test_initial_amounts(self):
        # Tests that all tickets are open at initialization
        self.assertSetEqual(self.ticket_holder.ticket_amounts, self.amounts)

    def test_initial_unedited(self):
        # Tests the betting ticket money_for_placements change
        self.assertEqual(self.betting_ticket.money_for_placements, self.one_ticket)

    def test_take_out_bet(self):
        # Tests that taking a bet on a color works
        self.amounts = {"blue": [2,2,3], "green": [2,2,3,5], "red": [2,2,3,5], "yellow": [2,2,3,5], "purple": [2,2,3,5]}
        self.ticket_holder.take_out_bet("blue")
        self.assertEqual(self.ticket_holder.ticket_amounts, self.amounts)
        bool = False

        # Checks that player has right color/int pair for bet
        self.test_ticket["blue"] = [] #empty stack
        for bettingAmount in [2,2,3]:
            self.test_ticket["blue"].append(BettingTicketHolder.BettingTicket(color, bettingAmount)) #stack with a blue betting tickets, without a 5

        for i in self.camel_player.bets:
            if i.color == blue and i.money_for_placements == (5,-1,-1,-1,-1):
                bool = True
        self.assertEqual( bool, True)

    def test_take_out_multiple_bet(self):
        # Tests that taking a bet on a color works
        bool = False
        self.amounts = {"blue": [2,2,3], "green": [2,2,3,5], "red": [2,2,3,5], "yellow": [2,2,3,5], "purple": [2,2,3,5]}
        self.ticket_holder.take_out_bet("blue")
        self.ticket_holder.take_out_bet("blue")

        for i in self.ticket_amounts["blue"]:
            if i.bettingAmount == 2:
                    bool = True
        self.assertEqual(bool, True)

# Pull before making changes on exchange_all_bets

if __name__ == '__main__':
    unittest.main()
