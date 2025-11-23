# camel-up-game
Updated from private repository.

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
        +AIPlayer ai_player
        +start_game()
        +roll_dice(player)
        +prompt_player_input()
        +show_winner_screen()
    }

    class AIPlayer {
        +int amount_of_sims
        +run_simulation(race_track_list, dice_list)
        +display_stats()
    }

    class BettingTicketHolder {
        +Dict~str, List[BettingTicket]~ ticket_amounts
        +Dict unedited_tickets
        +take_out_bet(color, CamelPlayer) bool
        +exchange_all_bets(players, ordering)
        +get_available_bets() Dict
    }

    class BettingTicket {
        +str color
        +Tuple money_for_placements
    }

    class Pyramid {
        +List unrolled_dice
        +List rolled_dice
        +roll() (color, amount, is_last)
        +reset()
    }

    class RaceTrack {
        +List~LinkedList~ camel_and_tile_locations
        +find_camel(color) int
        +location_update(color, amount)
        +get_camel_position(color)
        +get_camel_placements()
        +to_rotated_list()
        +empty_spaces()
    }

    class CamelPlayer {
        +str name
        +int amount_of_money
        +List bets
        +bool is_ai
    }

    class LinkedList {
        +Node head
        +append(data)
        +remove_from(color)
        +add_stack_to_top(node)
        +remove_stack_from_top(n)
        +add_stack_to_bottom(node)
        +to_list()
    }

    class Node {
        +Tuple data
        +Node next
    }

    %% Java side
    class AvatarScreen {
        <<Java>>
        +void renderAvatars(List<String> names)
        +void showStartScreen()
        +void showEndScreen()
    }

    %% Relationships
    LinkedList --> Node
    RaceTrack --> LinkedList
    TheGame --> Pyramid
    TheGame --> RaceTrack
    TheGame --> BettingTicketHolder
    TheGame --> CamelPlayer
    TheGame --> AIPlayer
    BettingTicketHolder --> BettingTicket

    %% External Java Integration
    TheGame ..> AvatarScreen : calls via subprocess\n(java AvatarScreen)

