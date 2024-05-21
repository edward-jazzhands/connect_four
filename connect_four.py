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

# Available log levels are DEBUG, INFO, WARNING, ERROR, CRITICAL


##########################################################
 
def game_display(grid: object) -> None:
    """ This function handles the display of whatever grid is passed into it, assuming its a 2D list of Cell objects. """

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
        print(" ", ascii_uppercase[i], end="")                 # prints the column letters at the bottom
    print("\n")


#####################################################
        
def check_win(grid: object) -> CellState:
    """ returns 0 for no winner, 1 for player 1, 2 for player 2."""

    debug_gridscanning = False              # turning this on will print a ton of extra information about the grid scanning process
                                            # this was useful for debugging the win-checking algorithm
    logging.debug(f"\033[33m Checking for a winner... \033[0m")

    grid = grid.grid_matrix                 # the grid has several properties, we specifically want the grid_matrix
                                            # I could also pass in the grid_matrix directly, but this is more explicit.
    rows = len(grid)
    cols = len(grid[0])

    logging.debug(f"Checking horizontal")
    for row in range(rows):
        for col in range(cols - 3):

            if grid[row][col].cell_state != CellState.EMPTY:
               if grid[row][col].cell_state == grid[row][col+1].cell_state == \
               grid[row][col+2].cell_state == grid[row][col+3].cell_state:
                                       
                    logging.debug(f"\033[33m Winner found checking horizontal at row {row}, col {col} \033[0m")
                    return grid[row][col].cell_state
        if debug_gridscanning:
            logging.debug(f"Horizontal check of row {row} completed. Continuing...")         


    logging.debug(f"Checking vertical")
    for col in range(cols):
        for row in range(rows - 3):
            
            if grid[row][col].cell_state != CellState.EMPTY and \
               grid[row][col].cell_state == grid[row+1][col].cell_state == \
               grid[row+2][col].cell_state == grid[row+3][col].cell_state:
                
                logging.debug(f"\033[33m Winner found checking vertical at row {row}, col {col} \033[0m")
                return grid[row][col].cell_state
            
        if debug_gridscanning:
            logging.debug(f"Vertical check of column {col} completed. Continuing...")

    logging.debug(f"Checking diagonal (top-left to bottom-right \\ )")
    for row in range(rows - 3):
        for col in range(cols - 3):

            if grid[row][col].cell_state != CellState.EMPTY and \
               grid[row][col].cell_state == grid[row+1][col+1].cell_state == \
               grid[row+2][col+2].cell_state == grid[row+3][col+3].cell_state:
                
                logging.debug(f"\033[33m Winner found checking diagonal \\ at row {row}, col {col} \033[0m")
                return grid[row][col].cell_state
            
        if debug_gridscanning:
            logging.debug(f"forward Diagonal check of row {row} completed. Continuing...")

    logging.debug(f"Checking diagonal (top-right to bottom-left / )")
    for row in range(rows - 3):
        for col in range(3, cols):

            if grid[row][col].cell_state != CellState.EMPTY and \
               grid[row][col].cell_state == grid[row+1][col-1].cell_state == \
               grid[row+2][col-2].cell_state == grid[row+3][col-3].cell_state:
                
                logging.debug(f"\033[33m Winner found checking diagonal / at row {row}, col {col} \033[0m")
                return grid[row][col].cell_state
            
        if debug_gridscanning:
            logging.debug(f"backward Diagonal check of row {row} completed. Continuing...")
            
    logging.debug(f"\033[33m No winner found. \033[0m")
    return CellState.EMPTY


#################################################################

def inform_user_about_debug() -> None:
    """ This function informs the user about the debug mode. """

    print("Debug mode is turned on. This will print extra information to the console.")
    print("If you would like to turn off debug mode then type 'off' or 'debug' and press Enter. Anything else continues.")
    choice = input("Type here: ").lower()
    if choice in ["off", "debug"]:
        BeesUtils.log_level_toggle()                                 # toggles the logging level


def create_move_dict(grid: object) -> dict:
    """ Generates a connect-four move dictionary from whatever grid is passed into it. (Columns only)"""
    # Undernote: Allows for dynamic grid sizes. 

    columns = grid.columns                          # This move dictionary is very simple. It goes A:0, B:1, C:2, etc.
    move_dict = {}

    for col in range(columns):                      # Just translates a letter to column index
        move_dict[ascii_uppercase[col]] = col          # game logic takes care of the rest 

    return move_dict 


def update_cell(current_cell: object, player: int) -> bool:
    """ This function updates the cell with the player's piece. Returns True if successful."""
    # note: that bool return is literally just used for a debug message. Its a bit silly.

    logging.debug(f"Current cell x, y = {current_cell.x}, {current_cell.y}")
    logging.debug(f"Current cell state: {current_cell.cell_state}")

    try:
        current_cell.cell_state = CellState(player)
        logging.debug(f"Player {player}: {current_cell}")
        return True
    except Exception as e:
        logging.error(f"Error updating cell: {e}")
        raise e


#############   START OF MAIN GAME   ##############


def main_game(game_manager) -> None:
    """ This contains the main game loop and initialization. \n
    Remember game_manager is the object, gamemanager is the module. """

    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        inform_user_about_debug()                         

    print("Connect Four game starting. HINT: Type 'debug' at any point to toggle DEBUG on or off.")
    
    game_manager.set_player_types()                                  # self method, sets self.player1_type and self.player2_type
    logging.debug(f"Player 1: {game_manager.player1_type}, Player 2: {game_manager.player2_type}")    # PlayerType enum      

    rows: int
    columns: int
    rows, columns = gamemanager.choose_size_input_bridge()             # Can be default or custom

    grid: object = gridmaker.Grid(rows, columns)                 
    logging.debug(f"\033[33m Grid initialized. grid.rows = {grid.rows}, grid.columns = {grid.columns} \033[0m")

    move_dict: dict = create_move_dict(grid)                   # Create the move dictionary
    logging.debug(f"\033[33m Move dictionary: {move_dict} \033[0m")
                                  
    total_cells: int = grid.rows * grid.columns


    def game_loop(grid: object, move_dict: dict, game_manager: object):

        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            # This checks modifying a cell state and displaying it.

            current_cell = grid.grid_matrix[0][0]
            current_cell.cell_state = CellState.PLAYER1
            print("Player 1: ", current_cell)                               
            current_cell.cell_state = CellState.PLAYER2
            print("Player 2: ", current_cell)
            current_cell.cell_state = CellState.EMPTY                       # Resets to empty after testing
            input("Press Enter to continue...")


        timestamp1 = BeesUtils.timestamp()                                  # Get the start time of the game in raw format
        timestamp1_formatted = timestamp1.strftime(time_format)             # Format the timestamp for display
        print(f"\n\033[33m Game starting at {timestamp1_formatted} \033[0m")

        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                if game_manager.player1_type == PlayerType.COMPUTER and game_manager.player2_type == PlayerType.COMPUTER:
                    print("Both players are computers, and you're in DEBUG mode. Game will pause each turn.")
                    print("Turn off debug mode and they will play automatically, very fast.")
                    print("Remember you can turn off debug by typing 'debug'")

        previous_player = None                                          
        while True:

            ################ CORE GAME LOOP ################

            """ Some notes about the system: The game_manager is toggling the turn token each loop with switch_player()
            By default it starts on PLAYER1. When the move system is called, it will check the current turn token,
            and then check whether that player is a human or computer. Then it will run the appropriate function.
            Those functions handle the validation. Then either way it returns the same thing: a cell object.
            This system is great because its modular and automatic. We literally just run the same function
            every time and the game manager takes care of the rest. """

            game_display(grid)

            if previous_player:         # enum
                print(f"Last move: Column {ascii_uppercase[current_cell.y]} by Player {previous_player.value}")

            if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                if game_manager.player1_type == PlayerType.COMPUTER and game_manager.player2_type == PlayerType.COMPUTER:

                    while True:
                        debug_wait = input("Type anything to continue, or 'debug' to toggle debug mode:")
                        if debug_wait == "debug":
                            BeesUtils.log_level_toggle()
                            continue
                        else:
                            break

            current_cell: object = game_manager.move_system(move_dict, grid)       # where the auto-magic happens

            # update the board with the cell from move_system, and the current player token
            update_cell_pass: bool = update_cell(current_cell, game_manager.turn_token.value)

            logging.debug (f"Update cell pass: {update_cell_pass}")        # this bool is not used anywhere but this line.

            game_manager.increment_moves()                                 # increment the move counter              
            winner: CellState = check_win(grid)                            # returns CellState.EMPTY if no winner
            logging.debug(f"Winner check: {winner}")                       # returns CellState.PLAYER1 or CellState.PLAYER2 if winner

            ################ END OF CORE GAME LOOP ################


            if winner != CellState.EMPTY:                                  # if there is a winner

                game_display(grid)                 
                try:
                    elapsed_time: float = BeesUtils.elapsed_calc(timestamp1)   # easier to do math on the raw timestamp and then format it
                    elapsed_formatted: str = BeesUtils.format_elapsed(elapsed_time)
                except Exception as e:
                    logging.error(f"Error getting elapsed time: {e}")
                    raise e
                if winner == CellState.PLAYER1:
                    print(f"\n\033[31mPlayer 1 ⬤ is the winner! \033[0m They won in {game_manager.player1_moves} moves.\n") 
                else:
                    print(f"\n\033[34mPlayer 2 ⬤ is the winner! \033[0m They won in {game_manager.player2_moves} moves.\n")
                print(f"The game took {elapsed_formatted}\n")         
                break                                                   
            elif game_manager.total_moves - 1 == total_cells:           # if the board is full
                game_display(grid)                                      # print the final display
                print("It's a draw!")                                   
                break  
            else:                                                       # no winner, board not full
                logging.debug("No winner found. Continuing...")
                previous_player = game_manager.turn_token               # this is an Enum member
                game_manager.switch_player()                            # flips turn token
                continue 


    ## run game loop after initializations                                     
    game_loop(grid, move_dict, game_manager)
        

#################################################################        

def external_loop():
    """I'm not sure it really matters much to initialize the game manager outside the main game loop. \n
    At least I get to use the play_again function. """                         
    
    while True:                                            

        game_manager = gamemanager.GameManager()      
        main_game(game_manager)  
        if not game_manager.play_again():
            print("Goodbye!")
            break


if __name__ == "__main__":
    external_loop()
