import logging
from typing import List, Tuple, Dict
from enum import Enum
from collections import deque
from string import ascii_uppercase
from copy import deepcopy
import random

from cfenums import TurnToken, PlayerType, CellState


import inputfuncs
import complogic
import beesutils

# TO DO
# Create an enum array inside the grid class
# make complogic use the enum array instead of the grid_matrix



class GameManager:
    """ Manages the game state. Also contains a bunch of functions that are called by the main game loop.
    Acts as an intermediary between the main game loop and the other modules. """

    ########## Initialization Methods ##########


    def __init__(self):

        self.player1_type = PlayerType.HUMAN         # default to human
        self.player2_type = PlayerType.HUMAN         # default to human
        self.turn_token = TurnToken.PLAYER1          # keeps track of whose turn it is
        self.player1_moves = 0
        self.player2_moves = 0
        self.remaining_cells = 0
        self.winner_direction = None                 # for display victory direction
        self.win_starting_column = None
        self.initialization_message()


    def init_move_calculators(self, grid: object, move_dict: dict) -> None:
        """ Initializes the Move Calculators. """

        self.comp_move_calc = complogic.ComputerMoveCalculator(self, grid, move_dict)
        self.human_move_calc = inputfuncs.HumanMoveReturner(self, grid, move_dict)
        logging.debug(beesutils.color(f"Move Calculators initialized."))

    
    @staticmethod
    def initialization_message() -> None:

        logging.debug(beesutils.color(f"GameManager initialized."))


    ##############  General Self-Methods  ##############


    def switch_player(self) -> None:
        """ Switches the current player. """
        logging.debug(beesutils.color(f"Switching players...", "cyan"))

        if self.turn_token == TurnToken.PLAYER1:
            self.turn_token = TurnToken.PLAYER2
        elif self.turn_token == TurnToken.PLAYER2:
            self.turn_token = TurnToken.PLAYER1

    def move_counter(self) -> None:
        """ Increments the number of moves made by the current player. """

        if self.turn_token == TurnToken.PLAYER1:
            self.player1_moves += 1
            self.remaining_cells -= 1
        elif self.turn_token == TurnToken.PLAYER2:
            self.player2_moves += 1
            self.remaining_cells -= 1

    def reset_game(self, total_cells) -> None:
        """ Resets the game state back to the beginning. """

        self.player1_moves = 0
        self.player2_moves = 0
        self.remaining_cells = total_cells
        self.winner_direction = None
        self.win_starting_column = None
        self.turn_token = TurnToken.PLAYER1

    def player_types_bridge(self):

        player1, player2 = inputfuncs.choose_player_types()
        self.player1_type = player1
        self.player2_type = player2

    def choose_size_bridge(self) -> Tuple[int, int]:

        rows, columns = inputfuncs.choose_size()
        self.remaining_cells = rows * columns
        return rows, columns


    def update_win_counters(self, direction: str) -> None:
        """ This function increments the win counters based on the direction of the win. """

        if self.winner_direction == "horizontal":
            self.horizontal_wins += 1
        elif self.winner_direction == "vertical":
            self.vertical_wins += 1
        elif self.winner_direction == "down-right":
            self.down_right_wins += 1
        elif self.winner_direction == "down-left":
            self.down_left_wins += 1
        else:
            logging.error(f"Error in update_win_counters. Invalid direction: {direction}")


    def update_cell(self, current_cell: object, updater_flip: bool = False) -> None:
        """ This function updates the cell with the current player's piece. 
        If bool is toggled to False, it will place the opponent's piece (opposite the current turn_token)"""

        logging.debug(f"Starting update_cell function. {repr(current_cell)} | {beesutils.color(f'updater_flip: {updater_flip}', 'orange')} ")

        if not updater_flip:
            player_num = self.turn_token.value
        else:                                               # if updater_flip is turned on (set to True)
            if self.turn_token == TurnToken.PLAYER1:
                player_num = TurnToken.PLAYER2.value
            else:
                player_num = TurnToken.PLAYER1.value

        try:
            current_cell.cell_state = CellState(player_num)
            logging.debug(f"Placing Player {player_num} {current_cell}  in cell {ascii_uppercase[current_cell.y]}{current_cell.x+1}")

        except Exception as e:
            logging.error(f"Error updating cell: {e}, current cell: {repr(current_cell)}")
            raise e
        
    @staticmethod
    def check_column(grid: object, column_index: int) -> object:
        """ This scans from the bottom up and returns the first empty cell it hits.
        This is actually more efficient than scanning from the top down because we don't need to keep a running list of empty cells."""

        grid_matrix = grid.grid_matrix

        for row in range(grid.rows - 1, -1, -1):                       # scans the column from the bottom up
            current_cell = grid_matrix[row][column_index]              # iterate through the column              
            if current_cell.cell_state == CellState.EMPTY:             # as soon as it hits an empty cell,
                return current_cell                                    # return the cell


    #############  End of General methods   ############
    #                                                  #
    #################   Move system   ##################
    
    
    def move_system(self, hide_board: bool) -> object:
        """ This function checks if the turn_token is on a human or computer player. \n
        It then calls the appropriate function and returns the chosen cell. """ 


        logging.debug(f"Current player turn token: {self.turn_token}")
        
        if self.turn_token == TurnToken.PLAYER1:
            player_type = self.player1_type
            player_moves = self.player1_moves
            sign = f"{beesutils.color("Player 1's turn ⬤", "red")}"
            
        else:
            player_type = self.player2_type
            player_moves = self.player2_moves
            sign = f"{beesutils.color("Player 2's turn ⬤", "blue")}"

        logging.debug(f"Player type: {player_type}")

        if not hide_board:
            print(f"\n {sign} | Move #: {player_moves+1}\n")
            
        if player_type == PlayerType.HUMAN:       
            current_cell = self.human_move_calc.human_move()

        elif player_type == PlayerType.COMPUTER:
            current_cell = self.comp_move_calc.computer_move()      

        else:
            logging.error(f"Error in move_system. self.turn_token: {self.turn_token}", "red")
            current_cell = None

        return current_cell
            
    
    ##############   End of Move System    #############
    #                                                  #
    ##########   Check for winner Function   ###########

    def check_win(self, grid: object, test_mode: bool = False) -> CellState:
        """Checks the grid for a winner. If winner, returns CellState of winner, otherwise CellState.EMPTY.
        When test_mode is set to True, it will not update the winner_direction or win_starting_column variables. """

        logging.debug(f"Starting check_win function. {beesutils.color(f'Test mode: {test_mode}', 'orange')} ")


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
            
            # This breaks out the function if it hits a cell that is not the same state as the original.
            for i in range(1, 4):
                if grid_matrix[cell.x + i * dr][cell.y + i * dc].cell_state != cell.cell_state:
                    return None
                
            # thus if we didn't return None, then we have a winner.
            logging.debug(beesutils.color(f"Winner found in direction {direction_name} starting at {repr(cell)}"))
            if not test_mode:
                self.winner_direction = direction_name                  # this is the only reason this is a self method
                self.win_starting_column = cell.y
                logging.debug(beesutils.color(f"self.winner_direction set to: {self.winner_direction}", "cyan"))
                logging.debug(beesutils.color(f"self.win_starting_column set to: {self.win_starting_column}", "cyan"))
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
                        row_boundary: int = row + 3 * dr                        # breaking out the math just makes it easier to understand
                        col_boundary: int = col + 3 * dc
                        if is_valid_cell(row_boundary, col_boundary):           # check if (current cell + 3) is in bounds
                            result = check_line(cell, direction_name)           # pass in start coordinate and direction
                            if result:
                                return result        # returns CellState.PLAYER1 or CellState.PLAYER2 if winner is found 

        return CellState.EMPTY                       # defaults to CellState.EMPTY if no winner is found
    
    
    ############# End of check_win function ############
    #                                                  #
    ################# Bridge functions #################

    

    ############## End of Bridge functions #############
    #                                                  #
    ####################   Extras  #####################


    @staticmethod
    def play_again() -> bool:
        """ This is called in the external loop if main_game() is exited. """

        while True:
            logging.debug(beesutils.color(f"play_again called."))
            play_again = input("Would you like to play again? (Y/N): ")
            play_again = play_again.upper()
            if play_again == "Y":
                logging.debug(beesutils.color(f"Game should be restarting..."))
                return True
            elif play_again == "N":
                logging.debug(beesutils.color(f"Game Manager stopped.", "red"))       
                return False
            else:
                print("Invalid input. Please enter Y or N.")
                continue


    






