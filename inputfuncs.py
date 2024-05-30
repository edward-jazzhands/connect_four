import logging
from string import ascii_uppercase
from typing import Tuple
import random

from cfenums import TurnToken, PlayerType, CellState


import beesutils


class HumanMoveReturner:
    """ Check's player's move against the move dictionary and the active grid.
    Returns the lowest empty cell in the column the player chooses. """
    
    def __init__(self, game_manager: object, grid: object, move_dict: dict):

        self.move_dict = move_dict
        self.grid = grid
        self.game_manager = game_manager

    def human_move(self) -> object:

        while True:
            move = input(f"{self.game_manager.turn_token.name}, enter your move: ").upper()

            if move.upper() == "DEBUG":
                beesutils.log_level_toggle()
                continue
            if move not in self.move_dict:
                print("Invalid move. Please enter a valid move.")
                continue
            
            column_index: int = self.move_dict[move]
            logging.debug(f"column_index: {column_index}")

            lowest_cell = self.game_manager.check_column(self.grid, column_index)    # check the column for the lowest empty cell

            if not lowest_cell:                                            # did not find an empty cell
                print("That column is full. Try again.")
                continue

            logging.debug(f"lowest empty cell coordinates: {repr(lowest_cell)}")
            return lowest_cell
    

################### Setup functions #####################
    

def choose_size() -> Tuple[int, int]:
    """ This function allows the user to choose the size of the grid. """

    print("Type anything for default size (6x7). Type 'c' to set a custom grid size.")
    print(beesutils.color("Type 'debug' to toggle debug mode.", "cyan"))
    
    while True:

        choice = input("Any key for default, 'c' for custom: ").lower()
        if choice == "c":
            while True:
                try:
                    rows = int(input("Enter the number of rows (MAX 20) "))
                    if rows > 20:
                        print("The maximum number of rows is 20.")
                        continue
                    elif rows < 4:
                        print("The minimum number of rows is 4.")
                        continue
                    else:
                        break
                except ValueError:
                    print("Please enter a number.")
                    continue
            while True:
                try:
                    columns = int(input("Enter the number of columns (MAX 26): "))
                    if columns > 26:
                        print("The maximum number of columns is 26.")
                        continue
                    elif columns < 4:
                        print("The minimum number of columns is 4.")
                        continue
                    else:
                        break
                except ValueError:
                    print("Please enter a number.")
                    continue

            return rows, columns
        
        elif choice.upper() == "DEBUG":
            beesutils.log_level_toggle()
            continue

        else:
            rows = 6
            columns = 7
            return rows, columns
        

def choose_player_types() -> Tuple[PlayerType, PlayerType]:
    """ This function allows the user to choose the player types """

    while True:

        while True:
            player1_choice = input("First, set Player 1 to Human or Computer (H or C): ").upper()

            if player1_choice == "H":
                player1 = PlayerType.HUMAN
                break
            elif player1_choice == "C":
                player1 = PlayerType.COMPUTER
                break
            else:
                print("Invalid input. Please enter H or C.")
                continue

        while True:
            player2_choice = input("Now, set Player 2 to Human or Computer (H or C): ").upper()

            if player2_choice == "H":
                player2 = PlayerType.HUMAN
                break
            elif player2_choice == "C":
                player2 = PlayerType.COMPUTER
                break
            else:
                print("Invalid input. Please enter H or C.")
                continue

        print(f"Player 1 is {player1.name} and Player 2 is {player2.name}.")
        confirm = input("Is this correct? (N to cancel, anything else continues): ").upper()
        if confirm == "N":
            continue
        else:
            return player1, player2