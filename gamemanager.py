"""
Module Name: gamemanager.py

    This module holds the GameManager class. This class manages the game state and acts as an intermediary
    between the main game loop and the other modules.
"""

from __future__ import annotations
from typing import *
import logging
from string import ascii_uppercase

from cfenums import TurnToken, PlayerType, CellState
import inputfuncs
import complogic
import checkinglogic
import beesutils

if TYPE_CHECKING:
    from gridmaker import Grid, Cell
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

    def attach_grid(self, grid: Grid, move_dict: dict) -> None:
        """ Attaches the grid and move dictionary to the GameManager. """

        self.grid = grid
        self.move_dict = move_dict
        logging.debug(beesutils.color(f"Grid and move dictionary attached to GameManager."))


    def init_check_system(self) -> None:
        """ Initializes the Checking System. """

        self.checking_system = checkinglogic.CheckingSystem(self)
        logging.debug(beesutils.color(f"Checking System initialized."))


    def init_move_calculators(self) -> None:
        """ Initializes the Move Calculators. """

        self.comp_move_calc = complogic.ComputerMoveCalculator(self)
        self.human_move_calc = inputfuncs.HumanMoveReturner(self)
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


    def reset_game(self, total_cells: int) -> None:
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
    

    def move_counter(self) -> None:
        """ Increments the number of moves made by the current player. """

        if self.turn_token == TurnToken.PLAYER1:
            self.player1_moves += 1
            self.remaining_cells -= 1
        elif self.turn_token == TurnToken.PLAYER2:
            self.player2_moves += 1
            self.remaining_cells -= 1


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



    def update_cell(self, current_cell: Cell, updater_flip: bool = False) -> None:
        """ This function updates the cell with the current player's piece.\n
        If bool is toggled to False, it will place the opponent's piece (opposite the current turn_token)"""
        # The cloned cells get passed into this function for checking. The main grid is updated in the main game loop.

        logging.debug(f"Starting update_cell function. {repr(current_cell)} | {beesutils.color(f'updater_flip: {updater_flip}', 'orange')} ")

        x = current_cell.x
        y = current_cell.y

        if not updater_flip:
            player_num = self.turn_token.value
        else:                                               # if updater_flip is turned on (set to True)
            if self.turn_token == TurnToken.PLAYER1:
                player_num = TurnToken.PLAYER2.value
            else:
                player_num = TurnToken.PLAYER1.value

        try:
            current_cell.cell_state = CellState(player_num)         # update the main grid
            logging.debug(f"Placing Player {player_num} {current_cell}  in cell {ascii_uppercase[current_cell.y]}{current_cell.x+1}")

        except Exception as e:
            logging.error(f"Error updating cell: {e}, current cell: {repr(current_cell)}")
            raise e
        
        
    def update_numpy(self, current_cell: Cell) -> None:

        x = current_cell.x
        y = current_cell.y
        player_num = self.turn_token.value
        self.grid.numpy_grid[x, y] = player_num


    #################   Move system   ##################
    
    
    def move_system(self, hide_board: bool) -> Cell:
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
            current_cell = self.human_move_calc.human_move()        # self-method of HumanMoveReturner

        elif player_type == PlayerType.COMPUTER:
            current_cell = self.comp_move_calc.computer_move()      # self-method of ComputerMoveCalculator

        else:
            logging.error(f"Error in move_system. self.turn_token: {self.turn_token}", "red")
            current_cell = None

        return current_cell
            

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