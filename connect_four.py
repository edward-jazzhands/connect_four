import logging
from typing import List, Tuple, Dict
from enum import Enum
import random
from collections import deque
from datetime import datetime
from string import ascii_uppercase

from cfenums import PlayerType, CellState

from beesutils import BeesUtils

import gridmaker
import gamemanager

####### GLOBAL VARIABLES ######


time_format = "%H:%M:%S"                         ## This is the format for the timestamp.

BeesUtils.logging_initializer("DEBUG")           ## Set the logging level for the game.

##########################################################
 
def game_display(grid: object) -> None:
    """ This function handles the display of whatever grid is passed into it \n
    Automatically adjusts the border based on the grid size. """

    break_bar = "---"
    
    print("")
    print("   ", break_bar * (grid.columns+1))              # adjusts the top bar based on the number of columns

    for row in range(grid.rows):
        print("   | ", end="")                              # prints the left bar of the grid

        for column in range(grid.columns):
            print(f" {grid.grid_matrix[row][column]} ", end="")    # prints whatever object is at that location in the grid matrix

        print(" |")                                         # prints the right bar of the grid
    print("   ", break_bar * (grid.columns+1))              # bottom bar of the grid
    print("    ", end="")

    for i in range(grid.columns):
        print(" ", ascii_uppercase[i], end="")              # prints the column letters at the bottom
    print("\n")


############   Check for Winner Function    ############
        
def check_win(grid: object, game_manager: object) -> CellState:
    """Checks the grid for a winner. If winner, returns CellState of winner, otherwise CellState.EMPTY."""

    logging.debug(f"Starting check_win function.")

    grid_matrix = grid.grid_matrix

    direction_dict = {
        "horizontal": (0, 1),             # right
        "vertical": (1, 0),               # down
        "down-right": (1, 1),             # down-right
        "down-left": (1, -1)              # down-left
    }

    #### Helpers ####
    def is_valid_cell(row_boundary: int, col_boundary: int) -> bool:
        """Checks if a cell is within the grid boundaries."""

        is_in_boundaries = 0 <= row_boundary < grid.rows and 0 <= col_boundary < grid.columns
        return is_in_boundaries

    def check_line(cell: object, direction_name: str) -> CellState:
        """ Checks for a streak of four in a line. This runs after is_valid_cell. """

        dr, dc = direction_dict[direction_name]                          # unpacks the direction tuple
        if cell.cell_state == CellState.EMPTY:                               
            return None                                                  # break out function if empty

        logging.debug(f"Cell not empty, potential line is in boundaries. Checking {direction_name} at ({cell.x}, {cell.y})")
        
        # This breaks out the function if it hits a cell that is not the same state as the original.
        for i in range(1, 4):
            if grid_matrix[cell.x + i * dr][cell.y + i * dc].cell_state != cell.cell_state:
                return None
            
        # thus if we didn't return None, then we have a winner.
        logging.debug(BeesUtils.color(f"Winner found in direction {direction_name} starting at ({cell.x}, {cell.y})"))
        game_manager.winner_direction = direction_name
        game_manager.win_starting_column = cell.y
        return cell.cell_state   
    
    #### End of Helpers ######
    
    for row in range(grid.rows):
        for col in range(grid.columns):
            
            cell: object = grid_matrix[row][col]
            if cell.cell_state == CellState.EMPTY:                          # Skip if current cell is empty
                continue                                               
            else:
                for direction_name, direction_tuple in direction_dict.items():
                    dr, dc = direction_tuple
                    row_boundary: int = row + 3 * dr                             # breaking out the math just makes it easier to understand
                    col_boundary: int = col + 3 * dc
                    if is_valid_cell(row_boundary, col_boundary):           # check if (current cell + 3) is in bounds
                        result = check_line(cell, direction_name)       # pass in start coordinate and direction
                        if result:
                            return result        # returns CellState.PLAYER1 or CellState.PLAYER2 if winner is found 

    return CellState.EMPTY                       # defaults to CellState.EMPTY if no winner is found


#############    General game functions    ##############


def inform_user_about_debug() -> None:
    """ This function informs the user about the debug mode. """

    print(BeesUtils.color("Debug mode is turned on. This will print extra information to the console."))
    print("If you would like to turn off debug mode then type 'off' or 'debug' and press Enter. Anything else continues.")
    choice = input("Type here: ").lower()
    if choice in ["off", "debug"]:
        BeesUtils.log_level_toggle()


def create_move_dict(grid: object) -> dict:
    """ Generates a connect-four move dictionary from whatever grid is passed into it. (Columns only)"""
    # Allows for dynamic grid sizes. 

    columns = grid.columns                          # This move dictionary is very simple. 
    move_dict = {}                                  # It goes A:0, B:1, C:2, etc.

    for col in range(columns):
        move_dict[ascii_uppercase[col]] = col

    return move_dict 


def update_cell(current_cell: object, player: PlayerType):
    """ This function updates the cell with the current player's piece."""

    try:
        current_cell.cell_state = CellState(player.value)
        logging.debug(f"Placing {player} {current_cell}  in cell {ascii_uppercase[current_cell.y]}{current_cell.x+1}")
    
    except Exception as e:
        logging.error(f"Error updating cell: {e}")
        raise e


#############   START OF MAIN GAME   ##############


def main_game(game_manager) -> None:
    """ This contains the main game loop and initialization. \n
    game_manager is the object, gamemanager is the module. """

    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        inform_user_about_debug()                         

    print("Connect Four game starting. ", BeesUtils.color("HINT:"), " Type 'debug' at any point to toggle DEBUG on or off.")
    
    game_manager.set_player_types()                                  # self method, sets self.player1_type and self.player2_type
    logging.debug(f"Player 1: {game_manager.player1_type}, Player 2: {game_manager.player2_type}")    # PlayerType enum    

    rows: int
    columns: int
    rows, columns = gamemanager.choose_size_input_bridge()            # Can be default or custom

    grid: object = gridmaker.Grid(rows, columns)                 
    logging.debug(BeesUtils.color(f"Grid initialized. grid.rows = {grid.rows}, grid.columns = {grid.columns}"))

    move_dict: dict = create_move_dict(grid)                            # Format: A:0, B:1, C:2, etc.
    logging.debug(BeesUtils.color(f"Move dictionary: {move_dict}"))     # scales automatically with grid size
                                  
    total_cells: int = grid.rows * grid.columns


    def game_loop(grid: object, move_dict: dict, game_manager: object, hide_board: bool = False, ultrasim: bool = False) -> CellState:

        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            # This just checks modifying a cell state and displaying it.

            current_cell = grid.grid_matrix[0][0]
            current_cell.cell_state = CellState.PLAYER1
            print("Player 1: ", current_cell)                               
            current_cell.cell_state = CellState.PLAYER2
            print("Player 2: ", current_cell)
            current_cell.cell_state = CellState.EMPTY                       # Resets to empty after testing
            input("Press Enter to continue...")

        if not ultrasim:
            timestamp1 = BeesUtils.timestamp()                          
            timestamp1_formatted = timestamp1.strftime(time_format)         # Format the timestamp for display
            print(BeesUtils.color(f"\nGame starting at {timestamp1_formatted}"))
            
        previous_player = None                                          
        while True:

            ################ CORE GAME LOOP ################

            """ Some notes about the system: The game_manager is toggling the turn token each loop with switch_player()
            By default it starts on PLAYER1. When the move system is called, it will check the current turn token,
            and then check whether that player is a human or computer. Then it will run the appropriate function.
            Those functions handle the move validation. Then either way it returns the same thing: a cell object.
            This system is great because its modular and automatic. It just runs the same function with the same
            args every time and the game manager takes care of the rest. """

            if not hide_board:
                game_display(grid)
                if previous_player:         # enum
                    print(f"Last move: Column {ascii_uppercase[current_cell.y]} by Player {previous_player.value}")

            # this pauses the game every turn if debug is on
            if game_manager.player1_type == PlayerType.COMPUTER and game_manager.player2_type == PlayerType.COMPUTER:
                if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                
                    while True:
                        debug_wait = input("Type anything to continue, or 'debug' to toggle debug mode:")
                        if debug_wait == "debug":
                            BeesUtils.log_level_toggle()
                            continue
                        else:
                            break

            current_cell: object = game_manager.move_system(move_dict, grid, hide_board)       # where the auto-magic happens

            # update the board with the cell from move_system, and the current player token
            update_cell(current_cell, game_manager.turn_token)

            game_manager.increment_moves()                                 # increment the move counter              
            winner: CellState = check_win(grid, game_manager)         # returns CellState.EMPTY if no winner

            ################ END OF CORE GAME LOOP ################

            if winner != CellState.EMPTY:                                  # if there is a winner
                
                if not ultrasim:
                    game_display(grid)                                         # print the final display

                    elapsed_time: float = BeesUtils.elapsed_calc(timestamp1)   # easier to do math on the raw timestamp and then format it
                    elapsed_formatted: str = BeesUtils.format_elapsed(elapsed_time)


                    print(BeesUtils.color(f"Winner found in direction: {game_manager.winner_direction} -"), end=" ")
                    print(BeesUtils.color(f"starting in column {ascii_uppercase[game_manager.win_starting_column]}", "cyan"))

                    if winner == CellState.PLAYER1:
                        print(BeesUtils.color(f"\nPlayer 1 ⬤ is the winner!", "red"), end=" ")
                        print(f"They won in {game_manager.player1_moves} moves.\n")
                    else:
                        print(BeesUtils.color(f"\nPlayer 2 ⬤ is the winner!", "blue"), end=" ")
                        print(f"They won in {game_manager.player2_moves} moves.\n")

                        print(f"The game took {elapsed_formatted}\n")         
                return winner    
                                                           
            elif game_manager.total_moves - 1 == total_cells:               # if the board is full
                
                if not ultrasim:
                    game_display(grid)                                      
                    print("It's a draw!")                                   
                return CellState.EMPTY  
            else:                                                           # no winner, board not full
                previous_player = game_manager.turn_token                   # this is an Enum member
                game_manager.switch_player()                                # flips turn token
                continue
    
    ######### END OF GAME LOOP FUNCTION #########
    #-------------------------------------------#
    ######### Simulation mode section  ##########

    if game_manager.player1_type == PlayerType.COMPUTER and game_manager.player2_type == PlayerType.COMPUTER:
        
        print(BeesUtils.color("Detected that both players are COMPUTER. Please enter the number of games to simulate."))
        logging.debug(BeesUtils.color("Also note you are in DEBUG mode. It will pause every turn.", "cyan"))
        logging.debug(BeesUtils.color("Toggle debug off to let it run automatically.", "cyan"))

        while True:
            simulation_count = input("Enter a number (or 'debug'): ")
            if simulation_count == "debug":
                BeesUtils.log_level_toggle()
                continue
            try:
                simulation_count = int(simulation_count)
                break
            except ValueError:
                print("Please enter a number.")

        hide_board = False
        ultrasim = False    

        print("Would you like to hide the board during the game?", BeesUtils.color("Type 'Y/y' to hide the board."))
        print("This is useful if you are running a large number of simulations.")
        print(BeesUtils.color("Note that it will still show the final board at the end of each game.", "cyan"))
        print(BeesUtils.color("Or if you want it to not show the board at ALL (for huge numbers of simulations), type 'ultrasim'.", "red"))
        hide_board_inp = input(BeesUtils.color("'Y/y' to hide, 'ultrasim' hides all. Anything else shows board: ")).upper()
        
        if hide_board_inp == "Y":
            hide_board = True  
        elif hide_board_inp == "ULTRASIM":
            hide_board = True
            ultrasim = True
        
        player1_wins, player2_wins, draws = 0, 0, 0
        win_direction_dict = {
            "horizontal wins": 0,
            "vertical wins": 0,
            "down-right wins": 0,
            "down-left wins": 0,
        }           
        timestamp2 = BeesUtils.timestamp()
                              
        for i in range(simulation_count):
            game_result: CellState = game_loop(grid, move_dict, game_manager, hide_board, ultrasim)   
            print(f"Game {i+1} completed. Game result: {game_result.name}")         # remove this for uber-sim

            if game_result == CellState.PLAYER1:
                player1_wins += 1
            elif game_result == CellState.PLAYER2:
                player2_wins += 1
            else:
                draws += 1

            win_direction_dict[f"{game_manager.winner_direction} wins"] += 1

            grid = gridmaker.Grid(rows, columns)                     # reset the grid
            game_manager.reset_moves()                               # reset the move counter
            
        elapsed_time: float = BeesUtils.elapsed_calc(timestamp2)
        elapsed_formatted: str = BeesUtils.format_elapsed(elapsed_time)            

        print(BeesUtils.color(f"\nSimulation of {simulation_count} games completed."))
        print(BeesUtils.color(f"Player 1 wins: {player1_wins},", "red"), end=" ")
        print(BeesUtils.color(f"Player 2 wins: {player2_wins},", "blue"), f"Draws: {draws}")

        for key, value in win_direction_dict.items():
            print(f"{key}: {value}", end=" | ")

        print(f"\nStart time: {timestamp2.strftime(time_format)}, End time: {BeesUtils.timestamp().strftime(time_format)}")
        print(f"Simulations took {elapsed_formatted}")

    ###### End of Simulation mode #######

    else:        # if sim mode is not on

        game_loop(grid, move_dict, game_manager)


#################################################################        

def external_loop():
    """I'm not sure it really matters much to initialize the game manager outside the main game loop. \n
    At least I get to use the play_again function. """

    logging.debug("External loop initialized. Printing environment variables.")
    BeesUtils.print_env_variables()                       
    
    while True:                                            

        game_manager = gamemanager.GameManager()      
        main_game(game_manager)  
        if not game_manager.play_again():
            print("Goodbye!")
            break


if __name__ == "__main__":
    external_loop()