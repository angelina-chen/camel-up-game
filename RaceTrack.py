from CamelPlayer import CamelPlayer
from LinkedList import LinkedList
import colorama


class RaceTrack:
    """
    Represents the game board as a sequence of tiles, each containing a stack of camels.

    Attributes:
        camel_and_tile_locations (list[LinkedList]): Each index is a tile; each tile
            is a linked list stack of camels.
        race_track_length (int): Number of tiles on the track.
        camel_colors (set[str]): Set of camel colors currently on the track.
        won_camels (list[list[str]]): Tracks camels that have crossed the finish line,
            grouped by how far beyond the end they moved.
        spectator_tiles (dict[int, tuple[int, CamelPlayer]]): Maps tile index to
            (tile_type, owner), where tile_type is +1 or -1.
        has_camel_won (bool): True if any regular camel has crossed the finish line.
    """

    def __init__(self, track_length: int = 16):
        self.camel_and_tile_locations = [LinkedList() for _ in range(track_length)]
        self.race_track_length = track_length
        self.camel_colors: set[str] = set()
        self.won_camels: list[list[str]] = [[] for _ in range(3)]
        self.spectator_tiles: dict[int, tuple[int, CamelPlayer]] = {}
        self.has_camel_won = False

    def set_up_camels(self, camels: list[tuple[str, int]]) -> None:
        """
        Place camels (and initial crazy camels) on the track.

        Args:
            camels (list[tuple[str, int]]): List of (color, tile_index) pairs.
                Entries with color == "spectator" are skipped.

        Returns:
            None
        """
        for color, tile_idx in camels:
            if color == "spectator":
                continue
            self.camel_and_tile_locations[tile_idx].append((color,))
            self.camel_colors.add(color)

    def find_camel(self, color: str) -> int | None:
        """
        Find the tile index where a camel of a given color is located.

        Args:
            color (str): Color of the camel to find.

        Returns:
            int | None: Tile index if found, None otherwise.
        """
        for idx, tile in enumerate(self.camel_and_tile_locations):
            curr = tile.head
            while curr:
                if curr.data[0] == color:
                    return idx
                curr = curr.next
        return None

    def location_update(self, color: str, amount_moved: int) -> tuple[list[list[str]], bool, CamelPlayer | None, int | None]:
        """
        Move a camel (and any camels stacked above it) by a given amount.

        Handles both regular camels (blue/green/red/yellow/purple) and
        crazy camels (black/white) with their wrapping behavior. Also applies
        spectator tile effects when landed on.

        Args:
            color (str): Color of the camel that is moving.
            amount_moved (int): Number of tiles to move; can be negative
                for crazy camels.

        Raises:
            ValueError: If the camel cannot be found on the track.

        Returns:
            tuple:
                - won_camels (list[list[str]]): Updated structure of camels that
                  have crossed the finish line.
                - spectator_triggered (bool): True if a spectator tile was triggered.
                - spectator_owner (CamelPlayer | None): Owner of the triggered
                  spectator tile, if any.
                - spectator_index (int | None): Tile index of the spectator tile
                  that was triggered, if any.
        """
        current_pos = self.find_camel(color)

        spectator_triggered = False
        spectator_owner: CamelPlayer | None = None
        spectator_index: int | None = None

        if current_pos is None:
            raise ValueError(f"Camel {color} not found on track")

        moving_stack = self.camel_and_tile_locations[current_pos].remove_from(color)
        if moving_stack is None:
            raise ValueError(f"Camel {color} not found in expected tile stack")

        new_pos = current_pos + amount_moved

        if color in {"black", "white"}:
            # Crazy camels wrap around the track
            if new_pos < 0:
                new_pos = len(self.camel_and_tile_locations) - 1
            elif new_pos >= len(self.camel_and_tile_locations):
                new_pos = 0
        else:
            # Regular camels: clip at edges and mark winners beyond finish
            if new_pos < 0:
                new_pos = 0
            elif new_pos >= len(self.camel_and_tile_locations):
                overflow = new_pos - len(self.camel_and_tile_locations)
                self.won_camels[overflow].append(color)
                self.has_camel_won = True
                new_pos = len(self.camel_and_tile_locations) - 1

        self.camel_and_tile_locations[new_pos].add_stack_to_top(moving_stack)

        # Spectator tile effect
        if new_pos in self.spectator_tiles:
            tile_type, owner = self.spectator_tiles[new_pos]
            spectator_triggered = True
            spectator_owner = owner
            spectator_index = new_pos

            # Count number of camels in the stack we just placed
            n_camels = 0
            node = moving_stack
            while node:
                n_camels += 1
                node = node.next

            if tile_type == +1:
                # Move stack forward one tile
                after_pos = min(new_pos + 1, len(self.camel_and_tile_locations) - 1)
                stack_top = self.camel_and_tile_locations[new_pos].remove_stack_from_top(n_camels)
                self.camel_and_tile_locations[after_pos].add_stack_to_top(stack_top)
            elif tile_type == -1:
                # Move stack backward one tile
                after_pos = max(new_pos - 1, 0)
                stack_top = self.camel_and_tile_locations[new_pos].remove_stack_from_top(n_camels)
                self.camel_and_tile_locations[after_pos].add_stack_to_bottom(stack_top)

        return self.won_camels, spectator_triggered, spectator_owner, spectator_index

    def print_track(self) -> None:
        """
        Print the current racetrack state, showing each tile and the camels on it.

        Returns:
            None
        """
        for idx, tile in enumerate(self.camel_and_tile_locations):
            stack = tile.to_list()
            stack_flat = [camel[0] for camel in stack]
            print(f"Tile {idx}: {stack_flat}")

    def to_list(self) -> list[list[tuple[str, ...]]]:
        """
        Convert the race track into a nested list representation.

        Returns:
            list[list[tuple[str, ...]]]: For each tile, a list of camel tuples.
        """
        ret: list[list[tuple[str, ...]]] = []
        for camel_stack in self.camel_and_tile_locations:
            ret.append(camel_stack.to_list())
        return ret

    def to_simulatable_list(self) -> list[tuple[str, int]]:
        """
        Create a simplified list of camel (color, tile_index) positions,
        plus spectator tile metadata used by the AI.

        Returns:
            list[tuple[str, int]]: List of (camel_color, tile_index) pairs.
        """
        ret: list[tuple[str, int]] = []
        for idx, camel_stack in enumerate(self.camel_and_tile_locations):
            for camel in camel_stack.to_list():
                ret.append((camel[0], idx))

        for idx in self.spectator_tiles:
            tile_type, _ = self.spectator_tiles[idx]
            ret.append(("spectator", idx, tile_type, CamelPlayer("")))

        return ret

    def empty_spaces(self) -> set[int]:
        """
        Compute which tiles are valid empty spaces for placing spectator tiles.

        A tile is considered unavailable if:
            - It currently has a camel, or
            - It is a spectator tile, or
            - It is adjacent to a spectator tile.

        Returns:
            set[int]: Set of tile indices that are valid for placing a spectator tile.
        """
        ret: set[int] = set()

        # Start with tiles that have no camels
        for idx, camel_stack in enumerate(self.camel_and_tile_locations):
            if len(camel_stack.to_list()) == 0:
                ret.add(idx)

        # Remove tiles that are a spectator tile or adjacent to one
        for idx in self.spectator_tiles:
            idx = int(idx)
            ret.discard(idx - 1)
            ret.discard(idx + 1)
            ret.discard(idx)

        return ret

    def to_rotated_list(self) -> list[list[str]]:
        """
        Create a rotated, colorized matrix representation of the track,
        primarily for printing in a top-down style.

        Returns:
            list[list[str]]: Rows of strings representing camel stacks and tiles.
        """
        clr_bck = {
            "blue": colorama.Fore.LIGHTBLUE_EX,
            "green": colorama.Fore.LIGHTGREEN_EX,
            "red": colorama.Fore.LIGHTRED_EX,
            "yellow": colorama.Fore.LIGHTYELLOW_EX,
            "purple": colorama.Fore.LIGHTMAGENTA_EX,
            "black": colorama.Fore.LIGHTBLACK_EX,
            "white": colorama.Fore.LIGHTWHITE_EX,
        }

        # 7 rows is enough to represent max stack + spectator row
        ret = [[" " for _ in range(len(self.camel_and_tile_locations))] for _ in range(7)]

        # Fill camel positions
        for column_index, camel_stack in enumerate(self.camel_and_tile_locations):
            for row_index, camel in enumerate(camel_stack.to_list()):
                ret[row_index][column_index] = clr_bck[camel[0]] + "C" + colorama.Style.RESET_ALL

        # Fill spectator tiles (+/-)
        for tile in range(self.race_track_length):
            if tile in self.spectator_tiles:
                t, _ = self.spectator_tiles[tile]
                ret[0][tile] = (
                    colorama.Fore.LIGHTGREEN_EX + "+" + colorama.Style.RESET_ALL
                    if t == 1
                    else colorama.Fore.LIGHTRED_EX + "-" + colorama.Style.RESET_ALL
                )

        return ret

    def __str__(self) -> str:
        """
        Return a simple string representation of the track as a list of stacks.

        Returns:
            str: A stringified list of camel stacks by tile.
        """
        ret = "["
        for tile in self.camel_and_tile_locations:
            stack = tile.to_list()
            stack_flat = [camel[0] for camel in stack]
            ret += str(stack_flat) + ", "
        return ret[:-2] + "]"

    def get_camel_position(self, color: str) -> tuple[int, int] | None:
        """
        Get the tile index and stack index of a camel.

        Args:
            color (str): Camel color to locate.

        Returns:
            tuple[int, int] | None:
                - (tile_idx, stack_idx): tile index and position within stack
                  (0 = bottom), or None if not found.
        """
        for tile_idx, tile in enumerate(self.camel_and_tile_locations):
            curr = tile.head
            stack_idx = 0
            while curr:
                if curr.data[0] == color:
                    return tile_idx, stack_idx
                curr = curr.next
                stack_idx += 1
        return None

    def get_camel_placements(self) -> tuple[str, ...]:
        """
        Compute the ranking of all regular camels from first to last.

        Returns:
            tuple[str, ...]: A tuple of camel colors ordered from first to fifth.
        """
        entries: list[tuple[int, int, str]] = []
        for color in ["blue", "green", "red", "yellow", "purple"]:
            pos = self.get_camel_position(color)
            if pos is None:
                continue
            tile_idx, stack_idx = pos
            entries.append((tile_idx, stack_idx, color))

        # Sort by tile index, then stack index, descending (frontmost/topmost first)
        entries.sort()
        entries.reverse()

        return tuple(e[2] for e in entries)

    def any_regcamel_done(self) -> bool:
        """
        Check if any regular camel has reached the final tile.

        Returns:
            bool: True if at least one regular camel is on the last tile.
        """
        last_tile_index = self.race_track_length - 1
        for color in ["blue", "green", "red", "yellow", "purple"]:
            pos = self.get_camel_position(color)
            if pos and pos[0] == last_tile_index:
                return True
        return False


if __name__ == "__main__":
    # Simple manual test of movement and printing.
    racetrack = RaceTrack()
    racetrack.camel_and_tile_locations[0].append(("blue",))
    racetrack.camel_and_tile_locations[0].append(("yellow",))
    racetrack.camel_and_tile_locations[3].append(("green",))
    racetrack.camel_and_tile_locations[0].append(("red",))
    racetrack.camel_and_tile_locations[2].append(("purple",))

    print("Initial board:")
    racetrack.print_track()

    racetrack.location_update("blue", 2)
    print("\nAfter moving blue 2 spaces:")
    racetrack.print_track()

    racetrack.location_update("yellow", 1)
    print("\nAfter moving yellow 1 space:")
    racetrack.print_track()

    racetrack.location_update("purple", 3)
    print("\nAfter moving purple 3 spaces:")
    racetrack.print_track()

    pos = racetrack.get_camel_position("blue")
    print("\nBlue camel position:", pos)
