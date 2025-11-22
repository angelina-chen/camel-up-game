from __future__ import annotations

from typing import Dict, List, Tuple, Set

from Pyramid import Pyramid
from RaceTrack import RaceTrack


class AIPlayer:
    """
    AI player that uses Monte Carlo simulation to estimate:
      - how often each camel finishes 1st / 2nd
      - which tiles are most frequently landed on

    NOTE: This currently only considers the 5 regular camels (no tiles or black/white
    crazy camels) in the simulation.
    """

    def __init__(self, amount_of_sims: int = 4000) -> None:
        self.amount_of_sims = amount_of_sims

    def run_simulation(
        self,
        race_track_simulatable_list: List[Tuple[str, int]],
        remaining_die: List[str],
    ) -> Tuple[Dict[str, List[int]], List[int]]:
        """
        Run Monte Carlo simulations for the current leg.

        Args:
            race_track_simulatable_list:
                List of (color, tile_index) tuples representing current camel positions.
            remaining_die:
                List of colors that are still in the pyramid (unrolled).

        Returns:
            A tuple:
              - placement_counts: dict[color] -> [first_place_count, second_place_count]
              - tile_placement: list where tile_placement[i] is how many times a camel
                ended a roll on tile i across all simulations.
        """
        # Statistics: color -> [first_count, second_count]
        placement_counts: Dict[str, List[int]] = {
            "blue": [0, 0],
            "green": [0, 0],
            "yellow": [0, 0],
            "red": [0, 0],
            "purple": [0, 0],
        }

        # Track how often each tile is landed on; default to track length 16
        # (Matches default RaceTrack length.)
        tile_placement: List[int] = [0] * 16

        # Pre-copy of positions to avoid accidental mutation of callers' list
        initial_positions = list(race_track_simulatable_list)

        for _ in range(self.amount_of_sims):
            sim_track = RaceTrack()
            sim_track.set_up_camels(initial_positions)

            sim_pyramid = Pyramid.from_simulatable(remaining_die)

            # Play out the rest of the leg
            while sim_pyramid.unrolled_dice:
                returned_dice_color, amount, _ = sim_pyramid.roll()

                sim_track.location_update(returned_dice_color, amount)

                index = sim_track.find_camel(returned_dice_color)
                if index is not None and 0 <= index < len(tile_placement):
                    tile_placement[index] += 1  # record landing tile

            placements = sim_track.get_camel_placements()  # tuple of 5 colors: 1st..5th
            color1 = placements[0]  # 1st place color
            color2 = placements[1]  # 2nd place color

            placement_counts[color1][0] += 1
            placement_counts[color2][1] += 1

        return placement_counts, tile_placement

    def display_stats(
        self,
        placement_dict: Dict[str, List[int]],
        tile_placement: List[int],
        available_bets: Dict[str, int],
        empty_spaces: Set[int],
        unrolled_dice: List[str],
    ) -> Dict[str, float]:
        """
        After running simulation, convert raw counts into expected values (EVs)
        for different actions:

          - EV of taking a race bet on each color
          - EV of placing a spectator tile on the most-visited empty tile
          - EV of rolling a die

        Args:
            placement_dict: dict[color] -> [first_place_count, second_place_count]
            tile_placement: list of tile landing counts from run_simulation
            available_bets: dict[color] -> top payout value of the next ticket
            empty_spaces: set of tile indices where tiles can be placed
            unrolled_dice: list of dice colors still in the pyramid

        Returns:
            dict[str, float]:
                - "<color>" -> EV of taking that bet now
                - "spt_<index>" -> EV of placing a spectator tile at that index
                - "roll" -> heuristic EV of rolling
        """
        evs: Dict[str, float] = {}

        # EV for each color bet
        for color, counts in placement_dict.items():
            first_count, second_count = counts
            top_bet_value = available_bets.get(color, 0)

            if top_bet_value == 0:
                evs[color] = 0.0
                continue

            sims = float(self.amount_of_sims)
            remaining = sims - first_count - second_count

            # EV formula:
            #   + top_bet_value for 1st place
            #   + 1 coin for 2nd place
            #   - 1 coin for all other outcomes
            ev = (
                first_count * top_bet_value
                + second_count
                - remaining
            ) / sims

            evs[color] = ev

        # Choose best spectator tile among empty spaces
        max_count = 0
        max_index = -1
        for index, count in enumerate(tile_placement):
            if count > max_count and index in empty_spaces:
                max_index = index
                max_count = count

        if max_index >= 0:
            ev_spectator_tile = max_count / float(self.amount_of_sims)
            evs[f"spt_{max_index}"] = ev_spectator_tile

        # Rough EV for rolling
        good_dice = len(unrolled_dice)
        unrolled_set = set(unrolled_dice)
        if "black" in unrolled_set:
            # crude approximation: black/white pair is "worse"
            good_dice -= 2

        if unrolled_dice:
            roll_ev = good_dice / len(unrolled_dice)
            # approx to 2 decimal places, like original integer-ish behavior
            roll_ev = int(roll_ev * 100) / 100
        else:
            roll_ev = 0.0

        evs["roll"] = roll_ev

        return evs
