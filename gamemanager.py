import logging
from typing import List, Tuple, Dict
from enum import Enum
from collections import deque
from string import ascii_uppercase

from cfenums import TurnToken, PlayerType, CellState


from inputfuncs import InputFuncs
from beesutils import BeesUtils



class GameManager:
    """ Manages the game state. Also contains a bunch of functions that are called by the main game loop.
    Acts as an intermediary between the main game loop and the input functions. """


    def __init__(self):

        self.player1_type = PlayerType.HUMAN         # default to human
        self.player2_type = PlayerType.HUMAN         # default to human
        self.turn_token = TurnToken.PLAYER1          # keeps track of whose turn it is
        self.player1_moves = 0
        self.player2_moves = 0
        self.total_moves = 1
        self.winner = None                           # not currently used!
        self.initialization_message()

    
    @staticmethod
    def initialization_message() -> None:

        logging.debug(BeesUtils.color(f"GameManager initialized."))

    @staticmethod
    def play_again() -> bool:
        """ This is called in the external loop if main_game() is exited. """

        while True:
            logging.debug(BeesUtils.color(f"play_again called."))
            play_again = input("Would you like to play again? (Y/N): ")
            play_again = play_again.upper()
            if play_again == "Y":
                logging.debug(BeesUtils.color(f"Game should be restarting..."))
                return True
            elif play_again == "N":
                logging.debug(BeesUtils.color(f"Game Manager stopped.", "red"))       
                return False
            else:
                print("Invalid input. Please enter Y or N.")
                continue

    def switch_player(self) -> None:
        """ Switches the current player. """

        if self.turn_token == TurnToken.PLAYER1:
            self.turn_token = TurnToken.PLAYER2
        elif self.turn_token == TurnToken.PLAYER2:
            self.turn_token = TurnToken.PLAYER1

    def increment_moves(self) -> None:
        """ Increments the number of moves made by the current player. """

        if self.turn_token == TurnToken.PLAYER1:
            self.player1_moves += 1
            self.total_moves += 1
        elif self.turn_token == TurnToken.PLAYER2:
            self.player2_moves += 1
            self.total_moves += 1

    def set_player_types(self):

        player1, player2 = InputFuncs.choose_player_types()
        self.player1_type = player1
        self.player2_type = player2
    
    
    def move_system(self, move_dict: Dict, grid: object) -> object:
        """ This function checks if the turn_token is on a human or computer player. \n
        It then calls the appropriate function to get the current cell. """ 
        # Also important to note here that the functions in InputFuncs do not actually care who's turn it is.
        # they just validate the move and return the cell.

        logging.debug(f"Current player turn token: {self.turn_token}")
        
        if self.turn_token == TurnToken.PLAYER1:
            player_type = self.player1_type
            player_moves = self.player1_moves
            sign = f"{BeesUtils.color("Player 1's turn ⬤", "red")}"
            
        else:
            player_type = self.player2_type
            player_moves = self.player2_moves
            sign = f"{BeesUtils.color("Player 2's turn ⬤", "blue")}"

        logging.debug(f"Player type: {player_type}")

        print(f"\n {sign} | Move #: {player_moves+1}\n")
            
        if player_type == PlayerType.HUMAN:       
            current_cell = InputFuncs.human_move(self.turn_token.value, move_dict, grid)
            # note: I only pass in the turn token value so it displays in the input message.
            # it has no effect on the core function.

        elif player_type == PlayerType.COMPUTER:
            current_cell = InputFuncs.computer_move(move_dict, grid)        # computer players don't need turn token

        else:
            logging.error(f"Error in move_system. Not human or computer. self.turn_token: {self.turn_token}")
            current_cell = None

        return current_cell
    
    
def choose_size_input_bridge() -> Tuple[int, int]:
    """This is here so I can keep input functions in their own module. \n
    inputfuncs does not get imported into the main game script. gamemanager is a bridge."""

    rows, columns = InputFuncs.choose_size()
    return rows, columns





