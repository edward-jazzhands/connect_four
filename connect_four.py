import logging
from typing import List, Tuple, Dict
from enum import Enum
import random
from collections import deque
from datetime import datetime
from string import ascii_uppercase

from cfenums import PlayerType, CellState

import beesutils

import gridmaker
import gamemanager

####### GLOBAL VARIABLES ######


time_format = "%H:%M:%S"                         ## This is the format for the timestamp.

beesutils.logging_initializer("DEBUG")           ## Set the logging level for the game.

##########################################################

class Display:
    """ This class contains the display functions for the game. """

    def __init__(self, grid: object):
        self.grid = grid
        self.show_heuristic = False
 
    def display_func(self) -> None:
        """ This function handles the display of whatever grid is passed into it \n
        Automatically adjusts the border based on the grid size. """

        grid = self.grid                                        # this just makes the code easier to read
        break_bar = "---"
        
        print("")
        print("   ", break_bar * (grid.columns+1))              # adjusts the top bar based on the number of columns

        for row in range(grid.rows):
            print("   | ", end="")                              # prints the left bar of the grid

            for column in range(grid.columns):
                if not self.show_heuristic:
                    print(f" {grid.grid_matrix[row][column]} ", end="")    # prints whatever object is at that location in the grid matrix
                else:
                    print(f" {grid.grid_matrix[row][column].heuristic_score} ", end="")

            print(" |")                                         # prints the right bar of the grid
        print("   ", break_bar * (grid.columns+1))              # bottom bar of the grid
        print("    ", end="")

        for i in range(grid.columns):
            print(" ", ascii_uppercase[i], end="")              # prints the column letters at the bottom
        print("\n")

    def reset_display(self, grid) -> None:
        """ Resets the display to the default state. """

        self.grid = grid
        self.show_heuristic = False

    def show_heuristics(self) -> None:
        """ This function toggles the display of heuristic scores on and off. """

        if self.show_heuristic:
            self.show_heuristic = False
            print(beesutils.color("Heuristic scores turned off.", "green"))
        else:
            self.show_heuristic = True
            print(beesutils.color("Heuristic scores turned on.", "green"))


#############    General game functions    ##############


def inform_user_about_debug() -> None:
    """ This function informs the user about the debug mode. """

    print(beesutils.color("Debug mode is turned on. This will print extra information to the console."))
    print("If you would like to turn off debug mode then type 'off' or 'debug' and press Enter. Anything else continues.")
    choice = input("Type here: ").lower()
    if choice in ["off", "debug"]:
        beesutils.log_level_toggle()


def create_move_dict(grid: object) -> dict:
    """ Generates a connect-four move dictionary from whatever grid is passed into it. (Columns only)""" 

    columns = grid.columns                          # This move dictionary is very simple. 
    move_dict = {}                                  # It goes A:0, B:1, C:2, etc.

    for col in range(columns):
        move_dict[ascii_uppercase[col]] = col

    return move_dict 


#############   START OF MAIN GAME   ##############


def main_game(game_manager) -> None:
    """ This contains the main game loop and initialization. \n
    game_manager is the object, gamemanager is the module. """

    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        inform_user_about_debug()                         

    print("Connect Four game starting. ", beesutils.color("HINT:"), " Type 'debug' at any point to toggle DEBUG on or off.")
    
    game_manager.player_types_bridge()                                # sets self.player1_type and self.player2_type
    logging.debug(f"Player 1: {game_manager.player1_type}, Player 2: {game_manager.player2_type}")    # PlayerType enum    

    rows: int
    columns: int
    rows, columns = game_manager.choose_size_bridge()                 # Can be default or custom

    grid: object = gridmaker.Grid(rows, columns)                 
    logging.debug(beesutils.color(f"Grid initialized. grid.rows = {grid.rows}, grid.columns = {grid.columns}"))

    move_dict: dict = create_move_dict(grid)                            # Format: A:0, B:1, C:2, etc.
    logging.debug(beesutils.color(f"Move dictionary: {move_dict}"))     # scales automatically with grid size

    game_display: object = Display(grid)
    game_manager.init_move_calculators(grid, move_dict)                   # computer move calculator


    def game_loop(hide_board: bool = False, ultrasim: bool = False) -> CellState:

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
            timestamp1 = beesutils.timestamp()                          
            timestamp1_formatted = timestamp1.strftime(time_format)         # Format the timestamp for display
            print(beesutils.color(f"\nGame starting at {timestamp1_formatted}"))
            
        previous_player = None                                          
        while True:

            ################ CORE GAME LOOP ################

            """ Some notes about the system:
            The game_manager is toggling the turn token each loop with switch_player()
            By default it starts on PLAYER1. When the move system is called, it will check the current turn token,
            and then check whether that player is a human or computer. Then it will run the appropriate class.
            Those classes handle the move validation. Then either way it returns the same thing: a cell object.
            This system is great because its modular and automatic. In our game loop, we just call the move system
            every time and the game manager takes care of the rest. We don't even need to pass any arguments.
            The move calculators get initialized with the grid and the move dictionary, so they have everything they need."""

            if not hide_board:
                game_display.display_func()                 # display the board
                if previous_player:                         # enum
                    print(f"Last move: Column {ascii_uppercase[current_cell.y]} by Player {previous_player.value}")

            logging.debug(f"game_manager.remaining_cells = {game_manager.remaining_cells}")

            # this pauses the game every turn if both players are computer and debug is on
            if game_manager.player1_type == PlayerType.COMPUTER and game_manager.player2_type == PlayerType.COMPUTER:
                if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                
                    while True:
                        debug_wait = input("'debug': toggle, 'heuristic': show heuristics. Anything else continues: ").lower()
                        if debug_wait == "debug":
                            beesutils.log_level_toggle()
                            continue
                        elif debug_wait == "heuristic":
                            game_display.show_heuristics()
                            continue
                        else:
                            break

            current_cell: object = game_manager.move_system(hide_board)       # where the auto-magic happens

            # update the board with the cell we got from move_system
            game_manager.update_cell(current_cell)

            game_manager.move_counter()                                            # keep track of moves made and remaining           
            winner: CellState = game_manager.check_win(grid)                       # returns CellState.EMPTY if no winner

            ################ END OF CORE GAME LOOP ################
            #                                                     #
            ################   IF WINNER SECTION   ################

            if winner != CellState.EMPTY:                                          # if there is a winner
                
                if not ultrasim:
                    game_display.display_func()                                    # print the final display

                    elapsed_time: float = beesutils.elapsed_calc(timestamp1)   # easier to do math on the raw timestamp and then format it
                    elapsed_formatted: str = beesutils.format_elapsed(elapsed_time)


                    print(beesutils.color(f"Winner found in direction: {game_manager.winner_direction} -"), end=" ")
                    print(beesutils.color(f"starting in column {ascii_uppercase[game_manager.win_starting_column]}", "cyan"))

                    if winner == CellState.PLAYER1:
                        print(beesutils.color(f"\nPlayer 1 ⬤ is the winner!", "red"), end=" ")
                        print(f"They won in {game_manager.player1_moves} moves.\n")
                    else:
                        print(beesutils.color(f"\nPlayer 2 ⬤ is the winner!", "blue"), end=" ")
                        print(f"They won in {game_manager.player2_moves} moves.\n")

                    print(f"The game took {elapsed_formatted}\n")         
                return winner    
                                                           
            elif game_manager.remaining_cells == 0:                           # no winner, board full
                
                if not ultrasim:
                    game_display.display_func()    
                    logging.debug(beesutils.color(f"game_manager.remaining_cells = {game_manager.remaining_cells}"))         
                    print("It's a draw!")                                   
                return CellState.EMPTY  
            else:                                                           # no winner, board not full
                previous_player = game_manager.turn_token                   # this is an Enum member
                game_manager.switch_player()                                # flips turn token
                continue
    
    ######### END OF GAME LOOP FUNCTION #########
    #                                           #
    ######### Simulation mode section  ##########

    if game_manager.player1_type == PlayerType.COMPUTER and game_manager.player2_type == PlayerType.COMPUTER:
        
        print(beesutils.color("Detected that both players are COMPUTER. Please enter the number of games to simulate."))
        logging.debug(beesutils.color("Also note you are in DEBUG mode. It will pause every turn.", "cyan"))
        logging.debug(beesutils.color("Toggle debug off to let it run automatically.", "cyan"))

        while True:
            simulation_count = input("Enter a number (or 'debug'): ")
            if simulation_count == "debug":
                beesutils.log_level_toggle()
                continue
            try:
                simulation_count = int(simulation_count)
                break
            except ValueError:
                print("Please enter a number.")

        hide_board: bool = False
        ultrasim: bool = False    

        print("Would you like to hide the board during the game?", beesutils.color("Type 'Y/y' to hide the board."))
        print("This is useful if you are running a large number of simulations.")
        print(beesutils.color("Note that it will still show the final board at the end of each game.", "cyan"))
        print(beesutils.color("Or if you want it to not show the board at ALL (for huge numbers of simulations), type 'ultrasim'.", "red"))
        hide_board_inp = input(beesutils.color("'Y/y' to hide, 'ultrasim' hides all. Anything else shows board: ")).upper()
        
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
        timestamp2 = beesutils.timestamp()
                              
        for i in range(simulation_count):
            game_result: CellState = game_loop(hide_board, ultrasim)   
            print(f"Game {i+1} completed. Game result: {game_result.name}") 

            if game_result == CellState.PLAYER1:
                player1_wins += 1
            elif game_result == CellState.PLAYER2:
                player2_wins += 1
            else:
                draws += 1

            if game_result != CellState.EMPTY:        # <-- I honestly have no idea why this line needs to be here but apparently it does
                win_direction_dict[f"{game_manager.winner_direction} wins"] += 1

            grid.reset_grid()                                                # reset the grid
            game_display.reset_display(grid)                                 # reset the display
            game_manager.reset_game(grid.total_cells)                        # reset the game manager
            
        elapsed_time: float = beesutils.elapsed_calc(timestamp2)
        elapsed_formatted: str = beesutils.format_elapsed(elapsed_time)            

        print(beesutils.color(f"\nSimulation of {simulation_count} games completed."))
        print(beesutils.color(f"Player 1 wins: {player1_wins},", "red"), end=" ")
        print(beesutils.color(f"Player 2 wins: {player2_wins},", "blue"), f"Draws: {draws}")

        for key, value in win_direction_dict.items():
            print(f"{key}: {value}", end=" | ")

        print(f"\nStart time: {timestamp2.strftime(time_format)}, End time: {beesutils.timestamp().strftime(time_format)}")
        print(f"Simulations took {elapsed_formatted}")

    ###### End of Simulation mode #######

    else:        # if sim mode is not on

        game_loop()


#################################################################        

def external_loop():
    """I'm not sure it really matters much to initialize the game manager outside the main game loop. \n
    At least I get to use the play_again function. """

    logging.debug("External loop initialized.")                     
    
    while True:                                            

        game_manager = gamemanager.GameManager()      
        main_game(game_manager)  
        if not game_manager.play_again():
            print("Goodbye!")
            break


if __name__ == "__main__":
    external_loop()