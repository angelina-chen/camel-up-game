import os
import re
import random

import colorama

from AIPlayer import AIPlayer
from BettingTicketHolder import BettingTicketHolder
from CamelPlayer import CamelPlayer
from Pyramid import Pyramid
from RaceTrack import RaceTrack
import subprocess

colorama.just_fix_windows_console()


class TheGame:
    """
    Orchestrates a full game of Camel Up: players, turns, dice, bets, and AI hints.
    """

    @staticmethod
    def get_input_force(repeat_question: str, is_valid_reply_function) -> str:
        """
        Repeatedly prompt the user until a valid reply is provided.

        Args:
            repeat_question (str): The question or prompt to display.
            is_valid_reply_function (Callable[[str], bool]): Function that returns
                True if the input is acceptable, False otherwise.

        Returns:
            str: A validated user input string.
        """
        print(repeat_question)
        console_input = re.sub(r"[() \n]+", "", input().lower().strip())
        while not is_valid_reply_function(console_input):
            os.system("cls")
            print(repeat_question)
            console_input = input().lower().strip()
        return console_input

    def __init__(self):
        """
        Initialize a new game: pyramid, betting tickets, racetrack, and AI.
        """
        self.pyramid = Pyramid()
        self.betting_tents = BettingTicketHolder()
        self.race_track = RaceTrack()

        # Random initial positions for regular camels
        temp: list[tuple[str, int]] = []
        for color in ["blue", "green", "red", "yellow", "purple"]:
            temp.append((color, random.randint(1, 3)))

        # Place crazy camels at tile 15 by default
        temp.append(("black", 15))
        temp.append(("white", 15))

        self.race_track.set_up_camels(temp)
        self.players: list[CamelPlayer] = []
        self.all_players: list[CamelPlayer] = []
        self.ai_player = AIPlayer()

    def payout_bets(self, players: list[CamelPlayer], camel_ordering: tuple[str, ...]) -> None:
        """
        Settle all outstanding bets for the given players.

        Args:
            players (list[CamelPlayer]): Players whose bets are being settled.
            camel_ordering (tuple[str, ...]): Final ordering of camels for the leg.

        Returns:
            None
        """
        self.betting_tents.exchange_all_bets(players, camel_ordering)

    def get_bets_available_string(self) -> str:
        """
        Build a colorized string summarizing available bets.

        Returns:
            str: Human-readable representation of the top bet value for each color.
        """
        available_bets = self.betting_tents.get_available_bets()
        clr_bck = {
            "blue": colorama.Back.LIGHTBLUE_EX,
            "green": colorama.Back.LIGHTGREEN_EX,
            "red": colorama.Back.LIGHTRED_EX,
            "yellow": colorama.Back.LIGHTYELLOW_EX,
            "purple": colorama.Back.LIGHTMAGENTA_EX,
        }

        tent_str_rep = "Available bets:" + colorama.Fore.BLACK
        for ticket_color in ["blue", "green", "red", "yellow", "purple"]:
            tent_str_rep += clr_bck[ticket_color] + str(available_bets[ticket_color])

        tent_str_rep += colorama.Style.RESET_ALL
        return tent_str_rep

    def get_game_state_str(self) -> str:
        """
        Build a full string representation of the current game state:
        bets, dice, board, and player money.

        Returns:
            str: A multi-line string representing the game state.
        """
        ret = ""
        ret += f"{self.get_bets_available_string()}            {self.pyramid.to_printable()}\n"

        board_rows = self.race_track.to_rotated_list()
        ret += "+Start+" + "-" * (self.race_track.race_track_length * 2 - 1) + "+Finish+\n"
        board_rows.reverse()
        for row in board_rows:
            ret += "|     |" + "_".join(row) + "|      |\n"
        ret += "+Start+0-1-2-3-4-5-6-7-8-9-0-1-2-3-4-5+Finish+\n"

        for player in self.all_players:
            ret += f"{player.name} has {player.amount_of_money} coin(s)\n"

        return ret

    def prompt_player_input(self, player: CamelPlayer, extra_text: str, extra_text_2: str) -> str:
        """
        Ask the player to choose an action for their turn.

        Args:
            player (CamelPlayer): The current player.
            extra_text (str): Additional informational text to show.
            extra_text_2 (str): More informational text (e.g., bet summaries).

        Returns:
            str: Player's choice ("1", "2", "3", or "4").
        """
        full_prompt = (
            self.get_game_state_str()
            + extra_text
            + "\n"
            + extra_text_2
            + f"\n{player.name}'s turn\n"
              "Choose an action:\n"
              "1. Roll dice\n"
              "2. Place a bet\n"
              "3. Place spectator tile\n"
              "4. Ask for a hint\n"
              "Enter 1, 2, 3, or 4:"
        )
        return self.get_input_force(full_prompt, lambda reply: reply in {"1", "2", "3", "4"})

    def roll_dice(self, player: CamelPlayer) -> tuple[bool, str]:
        """
        Roll a die from the pyramid and move the corresponding camel.

        The roller gains 1 coin if the die is for a regular camel.

        Args:
            player (CamelPlayer): The player who rolled the die.

        Returns:
            tuple[bool, str]:
                - has_leg_ended (bool): True if the leg ended after this roll.
                - msg (str): Human-readable summary of the roll.
        """
        returned_dice_color, amount, has_leg_ended = self.pyramid.roll()

        if returned_dice_color not in {"black", "white"}:
            player.amount_of_money += 1

        # Check if camel is on track before moving (should normally always be)
        if self.race_track.find_camel(returned_dice_color) is None:
            return (
                has_leg_ended,
                f"Rolled {returned_dice_color} camel: moves {amount} spaces. "
                "(No such camel on the racetrack, skipping move.)\n",
            )

        _, triggered, owner, tile_idx = self.race_track.location_update(returned_dice_color, amount)
        if triggered and owner:
            owner.amount_of_money += 1
            print(
                f"{owner.name} gains 1 coin for a camel landing on their spectator "
                f"tile at tile {tile_idx}!"
            )

        return has_leg_ended, f"Rolled {returned_dice_color} camel: moves {amount} spaces.\n"

    def get_hint(self) -> dict[str, float]:
        """
        Use the AIPlayer to run simulations and compute suggested EVs.

        Returns:
            dict[str, float]: Mapping of actions/colors to expected values:
                - "<color>" for race bets
                - "spt_<index>" for spectator tile placement at a tile
                - "roll" for rolling.
        """
        camel_placements, most_visited_tiles = self.ai_player.run_simulation(
            self.race_track.to_simulatable_list(),
            self.pyramid.to_simulatable(),
        )
        best_hints = self.ai_player.display_stats(
            camel_placements,
            most_visited_tiles,
            self.betting_tents.get_available_bets(),
            self.race_track.empty_spaces(),
            self.pyramid.to_simulatable(),
        )
        return best_hints

    def start_game(self, num_players: int = 2) -> None:
        """
        Set up players, shuffle their order, and run the main game loop.

        Args:
            num_players (int): Number of players. Defaults to 2.

        Returns:
            None
        """
        player_names: list[str] = []
        print("Play Camel Up!\n")

        for i in range(num_players):
            name = input(
                f"Enter name for Player {i + 1} (Enter AI to play against AI): "
            ).strip() or f"Player{i + 1}"
            player_names.append(name)

        self.players = [CamelPlayer(name) for name in player_names]
        self.all_players = self.players.copy()

        try:
            subprocess.run(["java", "AvatarScreen", *player_names], check=False)
        except FileNotFoundError:
        # Java or AvatarScreen not available; fail silently
            pass

        # Shuffle turn order
        random.shuffle(self.players)
        extra_text = "\nPlayer order:\n"
        for idx, player in enumerate(self.players):
            extra_text += f"{idx + 1}. {player.name}\n"

        # Main game loop
        while True:
            cur_player = self.players.pop(0)
            os.system("cls")

            player_bets_str = self.betting_tents.get_player_bets_str(self.all_players)
            max_color = ""
            max_ev = -1.0
            max_tile_pos = -1  # Only used for spectator tile placement

            if cur_player.is_ai:
                # AI chooses the action based on EV
                evs = self.get_hint()
                for col, ev in evs.items():
                    if "spt_" in col:
                        max_tile_pos = int(col[4:])
                    if ev > max_ev:
                        max_ev = ev
                        max_color = col

                # Map best EV label to an action choice
                if max_color == "roll":
                    player_input = "1"
                elif "spt_" in max_color:
                    player_input = "3"
                else:
                    player_input = "2"
            else:
                player_input = self.prompt_player_input(cur_player, extra_text, player_bets_str)

            has_used_turn = False
            extra_text = ""  # Reset per turn

            if player_input == "1":
                # Roll dice
                has_used_turn = True
                has_leg_ended, extra_text = self.roll_dice(cur_player)
                if has_leg_ended:
                    extra_text += "The leg has ended.\n"
                    self.payout_bets(self.players, self.race_track.get_camel_placements())
                    self.pyramid.reset()
                    self.race_track.spectator_tiles = {}

                if self.race_track.has_camel_won:
                    self.show_winner_screen()
                    break

            elif player_input == "2":
                # Place a bet
                color_bet_on = max_color  # Default for AI
                if not cur_player.is_ai:
                    color_bet_on = TheGame.get_input_force(
                        "Which camel color would you like to take out a bet on? \n"
                        "(b)lue (g)reen (r)ed (y)ellow (p)urple (c)ancel\n"
                        + self.get_bets_available_string()
                        + "\n",
                        lambda reply: reply
                        in {
                            "blue",
                            "green",
                            "red",
                            "yellow",
                            "purple",
                            "cancel",
                            "b",
                            "g",
                            "r",
                            "y",
                            "p",
                            "c",
                        },
                    )

                # Map single-letter choices to full colors
                if color_bet_on in {"b", "g", "r", "y", "p"}:
                    color_bet_on = {
                        "b": "blue",
                        "g": "green",
                        "r": "red",
                        "y": "yellow",
                        "p": "purple",
                    }[color_bet_on]

                if color_bet_on not in {"cancel", "c"}:
                    worked = self.betting_tents.take_out_bet(color_bet_on, cur_player)
                    if worked:
                        has_used_turn = True
                        extra_text = f"{cur_player.name} has taken out a bet on {color_bet_on}."
                    else:
                        extra_text = f"There were no bets available for the {color_bet_on} camel."

            elif player_input == "3":
                # Place spectator tile
                tile, signum = self.place_spectator_tile(cur_player, max_tile_pos)
                has_used_turn = True
                extra_text = f"{cur_player.name} has placed a {signum} spectator tile on tile {tile}."

            elif player_input == "4":
                # Ask for a hint
                extra_text = str(self.get_hint())

            # Reinsert current player based on whether they used their turn
            if has_used_turn:
                self.players.append(cur_player)
            else:
                self.players.insert(0, cur_player)

    def place_spectator_tile(self, player: CamelPlayer, position: int) -> tuple[int, str]:
        """
        Place a spectator tile for a player, either interactively or based on AI choice.

        Args:
            player (CamelPlayer): Player placing the tile.
            position (int): Suggested tile index (used by AI).

        Returns:
            tuple[int, str]:
                - tile_idx (int): Position where the tile was placed.
                - sign_label (str): "positive" or "negative".
        """
        os.system("cls")
        print(self.get_game_state_str())
        pos = 0

        if player.is_ai:
            pos = position
        else:
            # Validate tile position interactively
            while True:
                user_input = input(
                    f"Enter a track position (0 to {self.race_track.race_track_length - 1}) "
                    "to place a spectator tile:\n"
                    "(Cannot be adjacent to another spectator tile, or on a tile with a camel):\n"
                ).strip()
                if not user_input.isdigit():
                    print("Invalid input: not a number.")
                    continue
                pos = int(user_input)
                if pos < 0 or pos >= self.race_track.race_track_length:
                    print(
                        f"Invalid position: must be between 0 and "
                        f"{self.race_track.race_track_length - 1}."
                    )
                    continue

                # No adjacent spectator tile
                adj = {pos - 1, pos + 1}
                blocked = False
                for a in adj:
                    if 0 <= a < self.race_track.race_track_length and a in self.race_track.spectator_tiles:
                        print(f"Cannot place: tile {a} has a spectator tile (adjacency rule).")
                        blocked = True
                        break
                if blocked:
                    continue

                # No camel on tile
                if self.race_track.camel_and_tile_locations[pos].head is not None:
                    print(f"Cannot place: tile {pos} already has at least one camel.")
                    continue

                # No spectator tile already on this tile
                if pos in self.race_track.spectator_tiles:
                    print(f"Cannot place: tile {pos} already has a spectator tile.")
                    continue

                break

        # Choose tile type: positive or negative
        while True:
            if player.is_ai:
                tile_type_input = "n"
            else:
                tile_type_input = input(
                    "Place a (p)ositive (+1) or (n)egative (-1) spectator tile? (p/n): "
                ).strip().lower()

            if tile_type_input in {"p", "n", "positive", "negative"}:
                tile_type = +1 if tile_type_input in {"p", "positive"} else -1
                break
            else:
                print("Enter 'p' for positive or 'n' for negative")

        sign_label = "positive" if tile_type == +1 else "negative"
        self.race_track.spectator_tiles[pos] = (tile_type, player)

        return pos, sign_label

    def show_winner_screen(self) -> None:
        """
        Print the final results of the game and exit.

        Returns:
            None
        """
        placements = self.race_track.get_camel_placements()
        print("\nTHE RACE IS OVER!!!")
        print("Final camel placements:")
        for idx, color in enumerate(placements):
            print(f"{idx + 1}: {color.capitalize()} camel")
        for player in self.all_players:
            print(f"{player.name} ended with {player.amount_of_money} coin(s)")
        exit()


if __name__ == "__main__":
    game = TheGame()
    num_players = int(TheGame.get_input_force("How many players will play? ", str.isnumeric))
    game.start_game(num_players)
