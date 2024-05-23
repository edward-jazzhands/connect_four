import logging
from string import ascii_uppercase
from typing import Tuple
import random

from cfenums import TurnToken, PlayerType, CellState


from beesutils import BeesUtils

"""Plan to implement computer AI:
1) easy: computer checks if possible victory for both players. If it sees its own victory, take it. If it sees the opponent's victory, block it.
2) also easy: prioritize the center columns.
3) medium: look ahead one move. If it sees its next move will lead to the opponent winning, it will avoid that move.
4) hard: heuristics and minimax algorithm. """



class InputFuncs:

    ######## Move functions ########


    @staticmethod
    def check_column(move_dict: dict, grid: object, column_number: int) -> object:
        """ This scans from the bottom up and returns the first empty cell it hits.
        This is actually more efficient than scanning from the top down because we don't need to keep a running list of empty cells."""

        grid_matrix = grid.grid_matrix

        for row in range(grid.rows - 1, -1, -1):                       # scans the column from the bottom up

            current_cell = grid_matrix[row][column_number]             # iterate through the column              
            if current_cell.cell_state == CellState.EMPTY:             # as soon as it hits an empty cell,
                return current_cell                                    # return the cell
                  
    
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

            lowest_cell = InputFuncs.check_column(move_dict, grid, column_index)    # check the column for the lowest empty cell

            if not lowest_cell:                                                     # did not find an empty cell
                print("That column is full. Try again.")
                continue

            logging.debug(f"lowest empty cell coordinates: {lowest_cell.x}, {lowest_cell.y}")
            return lowest_cell
        
        
    @staticmethod    
    def computer_move(move_dict: dict, grid: object) -> object:
        """ """

        # column_index = random.choice(list(move_dict.values()))          # pick random column from move dictionary

        grid_matrix = grid.grid_matrix

        """
        start(first): (grid.rows - 1) means it starts at the bottom.  (number of rows minus 1, because zero indexing)
        stop(middle): (-1) means it stops at 0.
        step(last): (-1) means it goes up (or backwards). 
        Thus range(grid.rows - 1, -1, -1) means it starts at the bottom and goes up to the top. """

        def get_possible_moves() -> list:
            """ generates a list of possible moves based on the current board state. """

            possible_moves = []                                     
            for column_number in move_dict.values():                  # for each column in the move dictionary
                lowest_cell = InputFuncs.check_column(move_dict, grid, column_number)    # check the column for the lowest empty cell
                if lowest_cell:                                       # if it found an empty cell
                    possible_moves.append(lowest_cell)                # add the cell to the possible moves list

            return possible_moves                                                    
        
        # 4) build list of outcomes for each move
        # 5) choose best outcome
        # 6) if can't see a good move, choose random column
        # 7) return the lowest empty cell in the chosen column

        # 1) deep clone the board
        cloned_grid = deepcopy(grid)

        # 2) generate list of possible moves (the lowest empty cell in each column)
        possible_moves = get_possible_moves()
        logging.debug(f"Computer's possible_moves list: {possible_moves}")

        # 3) attempt each possible move and build a list of outcomes
        for cell in possible_moves:
            cloned_grid = deepcopy(grid)
            cloned_grid.apply_move(cell.x, cell.y)
            # evaluate the outcome of the move


        return
        

    ################### Setup functions #####################
        
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
            




def computer_move(move_dict: dict, grid: object) -> object:
    """This function generates a computer's move based on the given move dictionary and grid.
    It returns the lowest empty cell in the chosen column."""

    # 1) Deep clone the board
    cloned_grid = deepcopy(grid)

    # 2) Generate list of possible moves
    possible_moves = generate_possible_moves(move_dict, cloned_grid)

    # 3) Attempt each possible move and build a list of outcomes
    outcomes = []
    for column_index, row_index in possible_moves:
        # Clone the board and apply the move
        cloned_board = deepcopy(cloned_grid)
        cloned_board.apply_move(column_index, row_index)

        # Evaluate the outcome of the move
        outcome = evaluate_outcome(cloned_board)
        outcomes.append((column_index, row_index, outcome))

    # 4) Choose the best outcome
    best_outcome = max(outcomes, key=lambda x: x[2])
    best_column_index, best_row_index, best_outcome_type = best_outcome

    # 5) If no good move, choose random column
    if best_outcome_type == "no_good_move":
        column_index = random.choice(list(move_dict.values()))
        lowest_empty_cell = get_lowest_empty_cell(column_index, cloned_grid)
        return lowest_empty_cell

    # Return the lowest empty cell in the chosen column
    return best_row_index, best_column_index

def generate_possible_moves(move_dict: dict, grid: object) -> list:
    """Generate a list of possible moves based on the current board state."""
    possible_moves = []
    for column_index in move_dict.values():
        row_index = get_lowest_empty_cell(column_index, grid)
        if row_index is not None:
            possible_moves.append((column_index, row_index))
    return possible_moves

def get_lowest_empty_cell(column_index: int, grid: object) -> int:
    """Get the lowest empty cell in the specified column."""
    for row_index in range(grid.rows - 1, -1, -1):
        if grid.grid_matrix[row_index][column_index].cell_state == CellState.EMPTY:
            return row_index
    return None

def evaluate_outcome(board_state: object) -> str:
    """Evaluate the outcome of the current board state."""
    # Implement your logic to evaluate the outcome (e.g., win, block, no_good_move)
    pass
