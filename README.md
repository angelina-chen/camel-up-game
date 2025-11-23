# camel-up-game
Updated from private repository

```mermaid

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
        +List~CamelPlayer~ players
        +List~CamelPlayer~ all_players
        +AIPlayer ai_player
        +start_game(num_players: int)
        +roll_dice(player: CamelPlayer)
        +get_hint()
        +show_winner_screen()
    }

    class AIPlayer {
        +int amount_of_sims
        +run_simulation(board: list[(str,int)], dice: list[str])
        +display_stats(...)
    }

    class BettingTicketHolder {
        +Dict~str, List~BettingTicket~~ ticket_amounts
        +Dict~str, List~BettingTicket~~ unedited_tickets
        +take_out_bet(color: str, player: CamelPlayer) bool
        +exchange_all_bets(players: list[CamelPlayer], ordering: (str,...))
        +get_available_bets() Dict~str,int~
    }

    class BettingTicket {
        +str color
        +tuple[int,...] money_for_placements
    }

    class Pyramid {
        +tuple[str,...] unrolled_dice_original
        +List~str~ unrolled_dice
        +List~(str,int)~ rolled_dice
        +roll() (str, int, bool)
        +reset()
        +to_simulatable() list[str]
    }

    class RaceTrack {
        +List~LinkedList~ camel_and_tile_locations
        +int race_track_length
        +set~str~ camel_colors
        +Dict~int,(int,CamelPlayer)~ spectator_tiles
        +bool has_camel_won
        +set_up_camels(camels: list[(str,int)])
        +find_camel(color: str) int
        +location_update(color: str, amount_moved: int)
        +get_camel_placements() (str,...)
        +empty_spaces() set[int]
    }

    class CamelPlayer {
        +str name
        +int amount_of_money
        +List~BettingTicket~ bets
        +bool is_ai
        +__str__() str
    }

    class LinkedList {
        +Node head
        +append(data: tuple)
        +to_list() list[tuple]
        +remove_from(color: str) Node
        +add_stack_to_top(node: Node)
        +remove_stack_from_top(n: int) Node
        +add_stack_to_bottom(node: Node)
    }

    class Node {
        +tuple data
        +Node next
    }

    class AvatarScreen {
        <<Java>>
        +showStartScreen(names: List<String>)
        +showEndScreen(names: List<String>)
    }

    %% Relationships
    TheGame *-- Pyramid
    TheGame *-- BettingTicketHolder
    TheGame *-- RaceTrack
    TheGame *-- CamelPlayer
    TheGame *-- AIPlayer

    BettingTicketHolder *-- BettingTicket

    RaceTrack *-- LinkedList
    LinkedList *-- Node

    AIPlayer --> Pyramid
    AIPlayer --> RaceTrack

    TheGame ..> AvatarScreen : "subprocess: java AvatarScreen"
