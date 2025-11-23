# camel-up-game
Updated from private repository

A console-based implementation of *Camel Up* with Python game logic, Monte Carlo simulation for AI betting hints, and a small Java console UI module for player avatars.

```mermaid
---
config:
  layout: elk
  theme: neo-dark
---
classDiagram
direction LR

    class TheGame {
        +Pyramid pyramid
        +BettingTicketHolder betting_tents
        +RaceTrack race_track
        +List[CamelPlayer] players
        +List[CamelPlayer] all_players
        +AIPlayer ai_player
        +get_bets_available_string() str
        +get_game_state_str() str
        +prompt_player_input(player: CamelPlayer, extra_text: str, extra_text_2: str) str
        +roll_dice(player: CamelPlayer) (bool, str)
        +get_hint() dict
        +start_game(num_players: int) void
        +place_spectator_tile(player: CamelPlayer, position: int) (int, str)
        +show_winner_screen() void
    }

    class AIPlayer {
        +int amount_of_sims
        +run_simulation(race_track_simulatable_list: list[(str,int)], remaining_die: list[str]) (dict, list[int])
        +display_stats(placement_dict: dict, tile_placement: list[int], available_bets: dict[str,int], empty_spaces: set[int], unrolled_dice: list[str]) dict[str,float]
    }

    class BettingTicketHolder {
        +dict[str, list[BettingTicket]] ticket_amounts
        +dict[str, list[BettingTicket]] unedited_tickets
        +take_out_bet(color: str, camel_player: CamelPlayer) bool
        +exchange_all_bets(players: list[CamelPlayer], camel_ordering: (str,...)) void
        +get_available_bets() dict[str,int]
        +get_player_bets_str(plrs: list[CamelPlayer]) str
    }

    class BettingTicket {
        +str color
        +tuple[int,...] money_for_placements
    }

    class Pyramid {
        +(str,...) unrolled_dice_original
        +list[str] unrolled_dice
        +list[(str,int)] rolled_dice
        +roll() (str, int, bool)
        +reset() void
        +to_simulatable() list[str]
        +from_simulatable(unrolled_dice: list[str]) Pyramid
        +to_printable() str
        +is_last_roll() bool
    }

    class CamelPlayer {
        +str name
        +int amount_of_money
        +list[BettingTicket] bets
        +bool is_ai
        +__str__() str
    }

    class RaceTrack {
        +list[LinkedList] camel_and_tile_locations
        +int race_track_length
        +set[str] camel_colors
        +list[list[str]] won_camels
        +dict[int,(int,CamelPlayer)] spectator_tiles
        +bool has_camel_won
        +set_up_camels(camels: list[(str,int)]) void
        +find_camel(color: str) int
        +location_update(color: str, amount_moved: int) (list[list[str]], bool, CamelPlayer, int)
        +print_track() void
        +to_list() list[list[(str,)]]
        +to_simulatable_list() list
        +empty_spaces() set[int]
        +to_rotated_list() list[list[str]]
        +__str__() str
        +get_camel_position(color: str) (int,int)
        +get_camel_placements() (str,...)
        +any_regcamel_done() bool
    }

    class LinkedList {
        +Node head
        +append(data: tuple) void
        +to_list() list[tuple]
        +remove_from(color: str) Node
        +add_stack_to_top(node: Node) void
        +remove_stack_from_top(n: int) Node
        +add_stack_to_bottom(node: Node) void
        +__str__() str
    }

    class Node {
        +tuple data
        +Node next
        +__str__() str
    }

    %% Relationships
    TheGame *-- Pyramid
    TheGame *-- BettingTicketHolder
    TheGame *-- RaceTrack
    TheGame *-- CamelPlayer
    TheGame *-- AIPlayer

    BettingTicketHolder *-- BettingTicket
    BettingTicketHolder --> CamelPlayer

    RaceTrack *-- LinkedList
    LinkedList *-- Node
    RaceTrack --> CamelPlayer

    AIPlayer --> RaceTrack
    AIPlayer --> Pyramid
