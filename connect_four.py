import logging
from typing import *
import random
from collections import deque
from datetime import datetime
from string import ascii_uppercase
import turtle

from cfenums import PlayerType, CellState
import beesutils
from gridmaker import Grid, Cell
from gamemanager import GameManager
from display import Display
from simmode import GameSimulator


####### GLOBAL VARIABLES ######

time_format = "%H:%M:%S"                         ## for the timestamp.

beesutils.logging_initializer("DEBUG")           ## can specifiy a log file here if needed. Check docstring for details.


#############    General game functions    ##############

def inform_user_about_debug() -> None:

    print(beesutils.color("Debug mode is turned on. This will print extra information to the console."))
    print("If you would like to turn off debug mode then type 'off' or 'debug' and press Enter. Anything else continues.")
    choice = input("Type here: ").lower()
    if choice in ["off", "debug"]:
        beesutils.log_level_toggle()

def create_move_dict(grid: Grid) -> dict:
    """ Generates a connect-four move dictionary from whatever grid is passed into it. (Columns only) \n
    This could be in the Grid class, but the dictionary is different for every type of game so I figured it makes more sense
    to have it here.""" 

    columns = grid.columns                          # This move dictionary is very simple. 
    move_dict = {}                                  # It goes A:0, B:1, C:2, etc.

    for col in range(columns):
        move_dict[ascii_uppercase[col]] = col

    return move_dict 


#############   START OF MAIN GAME   ##############

def main_game(game_manager: GameManager) -> None:
    """ Contains the initialization, the main game loop function,
    and controls running the simulation mode. """


    def game_loop(hide_board: bool = False, ultrasim: bool = False) -> CellState:

        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            # This just checks modifying a cell state and displaying it.
            # This was one of the first debug checkers I built. It's not really needed anymore, but meh. Sanity checks are nice.

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
            The game_manager is toggling the turn token each loop with its self-method switch_player()
            By default it starts on PLAYER1. When the move system is called, it will check the current turn token,
            and then check whether that player is a human or computer, and sends it to the appropriate class.
            Those classes handle the move validation. They both return a cell object, which the move system passes back here.
            Once there's a chosen cell, the game_manager updates the cell and then runs the checking class."""

            if not hide_board:
                game_display.display_func()                 # display the board
                if previous_player:                         # enum
                    print(f"Last move: Column {ascii_uppercase[current_cell.y]} by Player {previous_player.value}")

            logging.debug(f"game_manager.remaining_cells = {game_manager.remaining_cells}")

            # this pauses the game every turn if both players are computer and debug is on
            if game_manager.player1_type == PlayerType.COMPUTER and game_manager.player2_type == PlayerType.COMPUTER:
                if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                
                    while True:
                        debug_wait = input("avail: 'debug', 'heuristic', 'numpy' | Anything else continues: ").lower()
                        if debug_wait == "debug":
                            beesutils.log_level_toggle()
                            break
                        elif debug_wait == "heuristic":
                            game_display.toggle_feature("heuristic")
                            break
                        elif debug_wait == "numpy":
                            game_display.toggle_feature("numpy")
                            break
                        else:
                            break

            current_cell: Cell = game_manager.move_system(hide_board)       # where the auto-magic happens

            # update the board and the numpy grid with the cell we got from move_system
            game_manager.update_cell(current_cell)
            game_manager.update_numpy(current_cell)

            game_manager.move_counter()                                                 # keep track of moves made and remaining           
            winner: CellState = game_manager.checking_system.check_win(grid)            # returns CellState.EMPTY if no winner

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
    
    ######### end of game loop function #########
    #                                           #
    #########    MAIN PROGRAM CORE     ##########


    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        inform_user_about_debug()                         

    print("Connect Four game starting. ", beesutils.color("HINT:"), " Type 'debug' at any point to toggle DEBUG on or off.")
    
    game_manager.player_types_bridge()                                  # sets self.player1_type and self.player2_type
    logging.debug(f"Player 1: {game_manager.player1_type}, Player 2: {game_manager.player2_type}")    # PlayerType enum    

    rows: int
    columns: int
    rows, columns = game_manager.choose_size_bridge()                   # Can be default or custom

    grid: Grid = Grid(rows, columns)                 
    logging.debug(beesutils.color(f"Grid initialized. grid.rows = {grid.rows}, grid.columns = {grid.columns}"))

    move_dict: dict = create_move_dict(grid)                            # Format: A:0, B:1, C:2, etc.
    logging.debug(beesutils.color(f"Move dictionary: {move_dict}"))     # scales automatically with grid size

    game_display: Display = Display(grid)

    game_manager.attach_grid(grid, move_dict)
    game_manager.init_check_system()                                    # checking system class
    game_manager.init_move_calculators()                                # move calculator classes for human and computer

    """ Notes about initialization:
    There's 5 things being initialized here:
     1. The grid, 2. The move dictionary, 3. The display, 4. The checking system, 5. The move calculators.
     All of them are classes except for the move dictionary, which is just a dictionary. """

    if game_manager.player1_type == PlayerType.COMPUTER and game_manager.player2_type == PlayerType.COMPUTER:
        
        simulator = GameSimulator(game_manager, game_loop, game_display)
        simulator.run_simulations()

    else:        # if sim mode is not on

        game_loop()

#################################################################        

def external_loop():
    """I'm not sure it really matters much to initialize the game manager outside the main game loop. \n
    At least I get to use the play_again function. I suppose I could add in save games or a menu or something."""

    logging.debug("External loop initialized.")                     
    
    while True:                                            

        game_manager = GameManager()      
        main_game(game_manager)  
        if not game_manager.play_again():
            print("Goodbye!")
            break

if __name__ == "__main__":
    external_loop()