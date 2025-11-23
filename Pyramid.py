import random
import colorama


class Pyramid:
    """
    Represents the dice pyramid used to roll dice in the game.

    Attributes:
        unrolled_dice_original (tuple[str, ...]): Original set of dice colors.
        unrolled_dice (list[str]): Dice colors that have not yet been rolled.
        rolled_dice (list[tuple[str, int]]): Dice that have been rolled
            in the current leg as (color, value).
    """

    def __init__(self):
        """
        Initialize the pyramid with all dice unrolled.
        """
        self.unrolled_dice_original = ("blue", "green", "yellow", "red", "purple", "black", "white")
        self.unrolled_dice = list(self.unrolled_dice_original)
        self.rolled_dice = []

    @staticmethod
    def from_simulatable(unrolled_dice: list) -> "Pyramid":
        """
        Construct a Pyramid from a list of unrolled dice colors.

        Args:
            unrolled_dice (list[str]): Colors of dice that are still unrolled.

        Returns:
            Pyramid: A new Pyramid instance with the given unrolled dice.
        """
        ret = Pyramid()
        # Approximate rolled dice as those not in the provided unrolled list
        ret.rolled_dice = list(set(ret.unrolled_dice) - set(unrolled_dice))
        ret.unrolled_dice = unrolled_dice.copy()
        return ret

    def to_simulatable(self) -> list:
        """
        Export current unrolled dice colors in a simple list form.

        Returns:
            list[str]: Colors of unrolled dice.
        """
        return self.unrolled_dice

    def roll(self) -> tuple[str, int, bool]:
        """
        Roll a single die from the pyramid.

        For normal camels (blue, green, yellow, red, purple), the roll
        moves them forward 1–3 spaces.

        For black/white dice, the returned number is negative and has
        special semantics elsewhere in the game.

        Returns:
            tuple[str, int, bool]:
                - str: Color of the die rolled.
                - int: Number of spaces to move (negative for black/white).
                - bool: True if this roll ends the leg; False otherwise.
        """
        if self.unrolled_dice:
            rand_color = random.choice(self.unrolled_dice)
            dice_roll = random.randint(1, 3)

            # Track rolled dice for display
            self.rolled_dice.append((rand_color, dice_roll))
            self.unrolled_dice.remove(rand_color)

            if rand_color not in {"black", "white"}:
                # Regular camel roll
                is_last = self.is_last_roll()
                return rand_color, dice_roll, is_last

            # Black/white "crazy" dice: move backwards (negative spaces)
            if rand_color == "black":
                # Once black is rolled, white can no longer appear
                if "white" in self.unrolled_dice:
                    self.unrolled_dice.remove("white")
                # Even if this might be last roll logically, original code
                # always returns False here, so we preserve that behavior.
                return rand_color, -dice_roll, False
            else:
                # rand_color == "white"
                if "black" in self.unrolled_dice:
                    self.unrolled_dice.remove("black")
                return "white", -dice_roll, False

        # No dice left to roll – keep behavior consistent with original
        print("Error, no more dice left to roll")
        return "", -9999, True

    def is_last_roll(self) -> bool:
        """
        Check whether the last roll of the leg has been reached.

        A roll is considered the last if:
          - There are no unrolled dice left, or
          - Only the black and white dice remain unrolled.

        Returns:
            bool: True if no further "normal" rolls can occur; False otherwise.
        """
        if not self.unrolled_dice:
            return True
        if "black" in self.unrolled_dice and "white" in self.unrolled_dice and len(self.unrolled_dice) == 2:
            return True
        return False

    def to_printable(self) -> str:
        """
        Produce a human-readable, colorized representation of rolled/unrolled dice.

        Returns:
            str: A string showing which dice have been rolled and which remain.
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
        # Same glyph for positive/negative 1–3, just visually a die face
        to_dice_ascii = {
            1: "⚀ ",
            2: "⚁ ",
            3: "⚂ ",
            -1: "⚀ ",
            -2: "⚁ ",
            -3: "⚂ ",
        }

        ret = "Rolled: "

        for color, value in self.rolled_dice:
            ret += clr_bck[color] + to_dice_ascii[value] + colorama.Style.RESET_ALL

        ret += " Unrolled: "
        for dice in self.unrolled_dice:
            ret += clr_bck[dice] + "☐ " + colorama.Style.RESET_ALL + " "

        return ret

    def reset(self) -> None:
        """
        Reset the pyramid to its initial state for a new leg.

        Returns:
            None
        """
        self.unrolled_dice = list(self.unrolled_dice_original)
        self.rolled_dice = []


if __name__ == "__main__":
    pass
