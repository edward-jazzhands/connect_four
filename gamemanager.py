import logging
from typing import List, Tuple, Dict
from enum import Enum
from collections import deque
from string import ascii_uppercase
from copy import deepcopy
import random

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
        self.total_moves = 0
        self.winner_direction = None                 # for display victory direction
        self.win_starting_column = None

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
        logging.debug(BeesUtils.color(f"Switching players...", "cyan"))

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

    def reset_moves(self) -> None:
        """ Resets the number of moves made by each player. """

        self.player1_moves = 0
        self.player2_moves = 0
        self.total_moves = 1

    def set_player_types(self):

        player1, player2 = InputFuncs.choose_player_types()
        self.player1_type = player1
        self.player2_type = player2
    
    
    def move_system(self, move_dict: Dict, grid: object, hide_board: bool) -> object:
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

        if not hide_board:
            print(f"\n {sign} | Move #: {player_moves+1}\n")
            
        if player_type == PlayerType.HUMAN:       
            current_cell = InputFuncs.human_move(self.turn_token.value, move_dict, grid)
            # note: I only pass in the turn token value so it displays in the input message.
            # it has no effect on the core function.

        elif player_type == PlayerType.COMPUTER:
            current_cell = self.computer_move(move_dict, grid)

        else:
            logging.error(f"Error in move_system self.turn_token: {self.turn_token}")
            current_cell = None

        return current_cell
    
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


    def update_cell(self, current_cell: object):
        """ This function updates the cell with the current player's piece. 
        Note: This works with the cloned grid as well. """

        player_num = self.turn_token.value
        logging.debug(BeesUtils.color(f"current_cell: {current_cell}"))

        try:
            current_cell.cell_state = CellState(player_num)
            logging.debug(f"Placing Player {player_num} {current_cell}  in cell {ascii_uppercase[current_cell.y]}{current_cell.x+1}")

        except Exception as e:
            logging.error(f"Error updating cell: {e}, current cell: {current_cell}, cell state: {current_cell.cell_state}")
            raise e

   
    def computer_move(self, move_dict: dict, grid: object) -> object:
        """ """

        grid_matrix = grid.grid_matrix

        def get_possible_moves() -> list:
            """ generates a list of possible moves based on the current board state. """

            possible_moves = []                                     
            for column_number in move_dict.values():                  # for each column in the move dictionary
                lowest_cell = InputFuncs.check_column(move_dict, grid, column_number)    # check the column for the lowest empty cell
                if lowest_cell:                                       # if it found an empty cell
                    possible_moves.append(lowest_cell)                # add the cell to the possible moves list
                else:
                    possible_moves.append("FULL")                     # if the column is full, add "full" to the list
            return possible_moves                                                    

        # 1) generate list of possible moves (the lowest empty cell in each column)
        possible_moves = get_possible_moves()
        for move in possible_moves:
            if move != "FULL":
                logging.debug(f"Possible move: {move.x}, {move.y}")
            else:
                logging.debug(f"Column is full.")


        # 2) attempt each possible move and build a list of outcomes
        result_list = []                                        
        for move in possible_moves:                            # possible_moves is a list of cells, or a string "full"
            if move != "FULL":
                cloned_grid = deepcopy(grid)                                 # clone the grid each time to start fresh
                cloned_cell = cloned_grid.grid_matrix[move.x][move.y]        # get the cloned cell

                logging.debug(f"Cloning grid and cell at {move.x}, {move.y}. Cloned cell: {cloned_cell}")
                self.update_cell(cloned_cell)
                
                result = self.check_win(cloned_grid)                  # check cloned grid for winner
                result_list.append(result)
                if result != CellState.EMPTY:                  # if a winner is found, break out of the loop early
                    break
            else:
                result_list.append("FULL")                     # result_list is a list of CellStates

        # We now have a result_list of CellStates representing the outcome of each possible move.
        # EMPTY = no winner, PLAYER1 = player 1 wins, PLAYER2 = player 2 wins.
        # Each index in the list corresponds to the column index. 
        best_move = None

        # 3) find possible winners
        for i, result in enumerate(result_list):       # i is the column index
            logging.debug(f"Column {i}: {result}")
            if result != CellState.EMPTY and result != "FULL":                     # if a winner is found
                logging.debug(BeesUtils.color(f"Winner found in column {ascii_uppercase[i]}."))
                best_move = possible_moves[i]          # this is correct because possible_moves is the list of cell objects
                break       

        """ remember the cloned grid is getting updated with whoevers turn it is right now.
        That means if it finds a winner on the clone grid, that must mean the current player can win on this turn.
        It is not possible for an opponent's win to be found on the cloned grid with our method, since the opponent
        is not the one placing pieces.
        Thus, possible_winners will only contain the current player's winning moves. """

        # 4) if can't see a good move, choose random column
        if best_move is None:
            # Choose a random column
            avail_columns = [move for move in possible_moves if move != "FULL"]
            best_move = random.choice(avail_columns)

        try:
            logging.debug(BeesUtils.color(f"Computer's best move: {best_move.x}, {best_move.y}"))
        except Exception as e:
            logging.error(f"Error in computer_move: {e}, attempting {best_move}")
        return best_move
    
    ############   Check for Winner Function    ############

    def check_win(self, grid: object) -> CellState:
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
            self.winner_direction = direction_name
            self.win_starting_column = cell.y
            logging.debug(BeesUtils.color(f"self.winner_direction set to: {self.winner_direction}", "cyan"))
            logging.debug(BeesUtils.color(f"self.win_starting_column set to: {self.win_starting_column}", "cyan"))
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
    
    
    """
    start(first): (grid.rows - 1) means it starts at the bottom.  (number of rows minus 1, because zero indexing)
    stop(middle): (-1) means it stops at 0.
    step(last): (-1) means it goes up (or backwards). 
    Thus range(grid.rows - 1, -1, -1) means it starts at the bottom and goes up to the top. """


    
    
    
def choose_size_input_bridge() -> Tuple[int, int]:
    """This is here so I can keep input functions in their own module. \n
    inputfuncs does not get imported into the main game script. gamemanager is a bridge."""

    rows, columns = InputFuncs.choose_size()
    return rows, columns





