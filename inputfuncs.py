import logging
from string import ascii_uppercase
from typing import Tuple
import random

from cfenums import TurnToken, PlayerType, CellState


from beesutils import BeesUtils

class InputFuncs:

    ######## Move functions ########                  
    
    @staticmethod
    def human_move(player: int, move_dict: dict, grid: object) -> object:
        """ Check's player's move against the move dictionary and the active grid.
        Returns the lowest empty cell in the column the player chooses. """

        while True:
            move = input(f"Player {player}, enter your move: ").upper()     # This f-string is the only reason the player token is here.

            if move.upper() == "DEBUG":
                BeesUtils.log_level_toggle()
                continue
            if move not in move_dict:
                print("Invalid move. Please enter a valid move.")
                continue
            
            column_index: int = move_dict[move]
            logging.debug(f"column_index: {column_index}")

            column_cells = []
            for row in range(grid.rows):
                cell = grid.grid_matrix[row][column_index]          # builds list of just that column
                if cell.cell_state == CellState.EMPTY:
                    column_cells.append(cell)
                    logging.debug(f"Empty cell found: {cell}   x, y = {cell.x}, {cell.y}")

            if not column_cells:                                    # if there's no empties then column is full
                print("That column is full. Try again.")
                continue
            
            lowest = column_cells[-1]
            logging.debug(f"lowest empty cell coordinates: {lowest.x}, {lowest.y}")
            return lowest
        
    @staticmethod    
    def computer_move(move_dict: dict, grid: object) -> object:
        """ This is identical to the human_move function except it picks a random column. \n
        It takes the same arguments and returns the same object type."""

        # This is where the computer's move logic would go. 
        # For now, it just picks a random column.
        # The loop is here so it will keep picking columns until it finds an empty one.

        while True:

            column_index = random.choice(list(move_dict.values()))          # pick random column from move dictionary
            logging.debug(BeesUtils.color(f"Computer chose column {column_index}", "green"))
            
            column_cells = []
            for row in range(grid.rows):
                cell = grid.grid_matrix[row][column_index]                  
                if cell.cell_state == CellState.EMPTY:
                    column_cells.append(cell)
                    logging.debug(f"Empty cell found: {cell}   x, y = {cell.x}, {cell.y}")

            if not column_cells:                                            
                logging.debug(BeesUtils.color("Computer tried to pick full column. Choosing again.", "red"))
                continue 

            lowest = column_cells[-1]
            logging.debug(f"lowest empty cell coordinates: {lowest.x}, {lowest.y}")
            return lowest
        

    ######## Setup functions ########
        
    @staticmethod
    def choose_size() -> Tuple[int, int]:
        """ This function allows the user to choose the size of the grid. """

        print("Type anything for default size (6x7). Type 'c' to set a custom grid size.")
        print(BeesUtils.color("Type 'debug' to toggle debug mode.", "cyan"))
        
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
                BeesUtils.log_level_toggle()
                continue

            else:
                rows = 6
                columns = 7
                return rows, columns
            
    @staticmethod
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