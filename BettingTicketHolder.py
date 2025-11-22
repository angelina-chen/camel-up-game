import copy
import colorama
from CamelPlayer import CamelPlayer


class BettingTicketHolder:
    """
    Manages betting tickets for all camel colors during the game.

    This class tracks available tickets, allows players to take bets, and
    handles settling bets at the end of a leg.
    """

    class BettingTicket:
        """
        Represents a single betting ticket for a camel.

        Attributes:
            color (str): Camel color the ticket refers to.
            money_for_placements (tuple[int]): Payouts indexed by placement:
                index 0 → 1st place payout
                index 1 → 2nd place payout
                index 2 → penalty for 3rd place
                index 3 → penalty for 4th place
                index 4 → penalty for 5th place
        """

        def __init__(self, color: str, money_for_placements: tuple[int, ...] | int | None = None):
            """
            Initialize a betting ticket.

            Args:
                color (str): The camel color for this ticket.
                money_for_placements (tuple[int] | int | None):
                    - If int: treated as the 1st place payout.
                    - If tuple: used directly.
                    - If None: defaults to (5, 1, -1, -1, -1).
            """
            self.color = color

            if isinstance(money_for_placements, int):
                self.money_for_placements = (money_for_placements, 1, -1, -1, -1)
            else:
                self.money_for_placements = money_for_placements or (5, 1, -1, -1, -1)

    def __init__(self):
        """
        Initialize the betting ticket holder.

        Creates a stack of tickets for each camel color with
        payouts (2, 2, 3, 5) from top to bottom.

        Colors tracked: blue, green, red, yellow, purple.
        """
        self.ticket_amounts: dict[str, list[BettingTicketHolder.BettingTicket]] = {}

        for color in ["blue", "green", "red", "yellow", "purple"]:
            self.ticket_amounts[color] = [
                BettingTicketHolder.BettingTicket(color, amount)
                for amount in [2, 2, 3, 5]
            ]

        # Deep copy for resetting between legs
        self.unedited_tickets = copy.deepcopy(self.ticket_amounts)

    def take_out_bet(self, color: str, camel_player: CamelPlayer) -> bool:
        """
        Removes the top ticket for a camel color and assigns it to a player.

        Args:
            color (str): Camel color to take a bet for.
            camel_player (CamelPlayer): Player taking the bet.

        Returns:
            bool: True if a ticket was available and taken; False otherwise.

        Examples:
            >>> tents = BettingTicketHolder()
            >>> player = CamelPlayer("Alice")
            >>> tents.take_out_bet("blue", player)
            True
        """
        stack = self.ticket_amounts.get(color, [])
        bet = stack.pop() if stack else None

        if bet:
            camel_player.bets.append(bet)
            return True
        return False

    def exchange_all_bets(self, players: list[CamelPlayer], camel_ordering: tuple[str, ...]):
        """
        Settles all outstanding bets for all players based on race results.

        Args:
            players (list[CamelPlayer]): Players whose bets must be settled.
            camel_ordering (tuple[str, ...]): Camel finishing order
                where index 0 = 1st place, index 1 = 2nd place, etc.

        Returns:
            None

        Example:
            >>> tents = BettingTicketHolder()
            >>> p = CamelPlayer("A")
            >>> tents.take_out_bet("blue", p)
            >>> tents.exchange_all_bets([p], ("blue","red","green","yellow","purple"))
            # Player A receives payout for blue camel.
        """
        for player in players:
            while player.bets:
                bet = player.bets.pop()
                placement = camel_ordering.index(bet.color)
                payout = bet.money_for_placements[placement]
                player.amount_of_money += payout

        # Reset deck for the next leg
        self.ticket_amounts = copy.deepcopy(self.unedited_tickets)

    def get_available_bets(self) -> dict[str, int]:
        """
        Returns the top available payout for each camel color.

        Returns:
            dict[str, int]:
                Keys are camel colors, values are payouts.
                Value is 0 when no bets remain for a color.

        Example:
            >>> tents = BettingTicketHolder()
            >>> tents.get_available_bets()
            {"blue": 2, "green": 2, "red": 2, ...}
        """
        results: dict[str, int] = {}

        for color, stack in self.ticket_amounts.items():
            results[color] = stack[-1].money_for_placements[0] if stack else 0

        return results

    @staticmethod
    def get_player_bets_str(plrs: list[CamelPlayer]) -> str:
        """
        Formats and returns a readable string of each player's outstanding bets.

        Args:
            plrs (list[CamelPlayer]): List of players.

        Returns:
            str: A formatted multiline string describing bets.

        Example:
            Output might look like:
                Alice has the following bets: [5][2]
                Bob has no outstanding bets
        """
        clr_bck = {
            "blue": colorama.Back.LIGHTBLUE_EX,
            "green": colorama.Back.LIGHTGREEN_EX,
            "red": colorama.Back.LIGHTRED_EX,
            "yellow": colorama.Back.LIGHTYELLOW_EX,
            "purple": colorama.Back.LIGHTMAGENTA_EX,
        }

        result = ""

        for plr in plrs:
            if not plr.bets:
                result += f"{plr.name} has no outstanding bets\n"
                continue

            result += f"{plr.name} has the following bets: "

            for bet in plr.bets:
                payout = bet.money_for_placements[0]
                color = bet.color
                result += (
                    colorama.Fore.BLACK
                    + clr_bck[color]
                    + str(payout)
                    + colorama.Style.RESET_ALL
                )

            result += "\n"

        return result
