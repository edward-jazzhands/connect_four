"""
Module Name: complogic.py

    This module holds the ComputerMoveCalculator class. This class is responsible for calculating the computer's move in Connect Four.
"""

from __future__ import annotations
from typing import *
import logging
from string import ascii_uppercase
from copy import deepcopy
import random

from cfenums import TurnToken, PlayerType, CellState
import beesutils

if TYPE_CHECKING:
    from gamemanager import GameManager
    from gridmaker import Cell, Grid

""" 
To Do:
-Implement MiniMax Algorithm
-Convert entire function to a class    <- DONE
-Make a numpy array to use for logic instead of directly on the grid/cell objects."""


class ComputerMoveCalculator:

    def __init__(self, game_manager: GameManager):

        self.game_manager = game_manager
        self.grid = game_manager.grid
        self.move_dict = game_manager.move_dict
        self.numpy_grid = game_manager.grid.numpy_grid
        self.check_column = game_manager.checking_system.check_column
        self.check_win = game_manager.checking_system.check_win
        self.update_cell = game_manager.update_cell

    def get_possible_moves(self) -> None:
        """ Appends either cells or the string "FULL" to the possible_moves list."""

        self.possible_moves = []                            
        for column_number in self.move_dict.values():                  # for each column in the move dictionary
            lowest_cell = self.check_column(column_number)    # check the column for the lowest empty cell
            if lowest_cell:                                            # if it found an empty cell
                self.possible_moves.append(lowest_cell)                # add the cell to the possible moves list
                logging.debug(f"Appending cell to possible moves: {repr(lowest_cell)}")
            else:
                self.possible_moves.append("FULL")                     # if the column is full, add "full" to the list
        logging.debug(f"Stage 1) Possible moves: {self.possible_moves}")

    # possible_moves is a list of cells. Each cell is the lowest empty cell in the column.
    # It can also be the string "FULL" if the column is full.   
    

    def attempt_possible_moves(self, updater_flip: bool = False, check_above: bool = True) -> List[Union[CellState, str]]:
        """ This function attempts each possible move and returns a list which is the result of each move. \n
        updater_flip: if True attempts moves for the opponent in possible_moves list. \n
        check_above: if True, checks the cell above the current cell for the opponent's winning move. """

        logging.debug(f"Starting attempt_possible_moves. updater_flip: {updater_flip}, check_above: {check_above}")

        def get_cloned_cell_above(move: Cell, cloned_grid: Grid) -> Optional[Cell]:
            """Checks if the current cell is in the top row. If not, returns the cell above it. If it is, returns None."""

            if move.x > 0:                                                  # 0 = top row
                return cloned_grid.grid_matrix[move.x-1][move.y]            # x-1 = cell above
            return None
        
        def update_and_check(cloned_cell: Cell, cloned_grid: Grid, updater_flip: bool) -> CellState:

            self.update_cell(cloned_cell, updater_flip)             # updating cloned cell updates the cloned grid
            return self.check_win(cloned_grid, True)                # run check_win on cloned grid in Test mode
            
        def process_result(move: Cell) -> Union[CellState, str]:
            """This function returns the result of the move. \n"""

            cloned_cell_above = None 
            cloned_grid = deepcopy(self.grid)                                    # clone the grid each time to start fresh
            cloned_cell = cloned_grid.grid_matrix[move.x][move.y]           # get the cloned cell
            if check_above:                                        
                cloned_cell_above = get_cloned_cell_above(move, cloned_grid)

            result: CellState = update_and_check(cloned_cell, cloned_grid, updater_flip)  # check for computer's winning move

            if result != CellState.EMPTY:                                   # if computer sees its own winning move
                return result                                       
            
            if cloned_cell_above:                                           # For this to happen: check above is true, and its not the top row

                opp_result: CellState = update_and_check(cloned_cell_above, cloned_grid, True)
                if opp_result != CellState.EMPTY:
                    logging.debug(beesutils.color("Opponent has a winning move in cell above. Appending 'BAD'", "red"))
                    return "BAD"
                
            # } else { 
            return CellState.EMPTY 
        
        ##########   END OF HELPERS   ###########
        #                                       #
        ###### attempt_possible_moves CORE ######
                   
        result_list = []
        for move in self.possible_moves:                                       
            if move == "FULL":
                result_list.append(move)
                continue

            result = process_result(move)

            if result != CellState.EMPTY:                   # if a winner is found
                logging.debug(beesutils.color(f"Winning move found in column {ascii_uppercase[move.y]}", "red"))
                result_list.append(result)                  # result is a CellState (CellState.PLAYER1 or CellState.PLAYER2)
                continue                              

            if result == "BAD":                               # if the opponent has a winning move in the cell above
                result_list.append(move)
                continue

            result_list.append(result)                      # it reaches this if: column is not full, not a bad move, and not a winner

        logging.debug(f"Finished attempting possible moves.")
        return result_list
    
    
    def examine_list(self, result_list: List[Union[CellState, str]], player_str: str) -> Optional[Cell]:
        """Pass the result list and the player string (current or opposing). Allows us to reuse this function for both current and opposing player. \n
        Note that the player_str has no effect on the function. It was only added to ensure it's clear which player we're checking for."""
                                                                        
        if player_str == "opp":    
            if self.game_manager.turn_token == TurnToken.PLAYER1:
                player = TurnToken.PLAYER2.name
            else:
                player = TurnToken.PLAYER1.name            
        else:
            player = self.game_manager.turn_token.name

        logging.debug(beesutils.color("RESULT LIST:", "cyan"))
        
        for i, result in enumerate(result_list):           # i is the column index, result is a CellState or a string
            logging.debug(beesutils.color(f"{player} ({player_str}): Column {ascii_uppercase[i]}({i}): {result}", "cyan")) 

            if result != "FULL" and result != "BAD" and result != CellState.EMPTY:    # if there is a winner
                best_move = self.possible_moves[i]          # possible_moves is the list of cells to use for reference

                logging.debug(beesutils.color(f"Winner found for {player} in column {ascii_uppercase[i]}.", "red"))
                return best_move                        # return early if a winner is found
            
        # } else {           
        return None                        # if it completes the loop without finding a winner, return None
    
    
    def last_resort(self, result_list: List[Union[CellState, str]]) -> Cell:
        """If there's no winners, this returns the best heuristic cell available, skipping bad moves. \n
        Unless there's only bad moves, in which case it just returns those (results in losing the game) \n"""

        logging.debug("Didn't find anything good. Checking for neutral move...")

        move_types = {"NEUTRAL": [], "BAD": []}

        for i, move in enumerate(result_list):
            if move != "FULL":
                if move != "BAD":
                    move_types["NEUTRAL"].append(self.possible_moves[i])
                else:
                    move_types["BAD"].append(self.possible_moves[i])

        # note: because it gets the actual cell objects from possible_moves, after this point it doesn't matter what order they're in.

        avail_cells = move_types["NEUTRAL"] or move_types["BAD"]        # this is called a short-circuit evaluation
        # a short-circuit evaluation is when the first condition is True, it doesn't bother checking the second condition
        # so here, if there's neutral moves it will only use those, otherwise it will use the bad moves
        
        for key, value in move_types.items():       # just for debugging
            for move in value:
                logging.debug(beesutils.color(f"{key} move: Column {ascii_uppercase[move.y]}: {repr(move)} | heuristic_score: {move.heuristic_score}", "purple"))

        best_heuristic_cell = self.get_best_heuristic_with_random(avail_cells)

        logging.debug(beesutils.color(f"Cell chosen: Column {ascii_uppercase[best_heuristic_cell.y]}: {repr(best_heuristic_cell)} | heuristic_score: {best_heuristic_cell.heuristic_score}", "green"))
        return best_heuristic_cell
    
    
    def get_best_heuristic_with_random(self, avail_cells: List[Cell], randomness_threshold: float = 0.2) -> Cell:
        """ Adds a random element to the heuristic selection process. This is to prevent the computer from always making the same moves.
        The randomness_threshold is the probability of ignoring the heuristic score entirely. Otherwises randomizes from cells tied for best."""

        # randomness_threshold: probability of picking a random move instead of the best heuristic move
        if random.random() < randomness_threshold:
            logging.debug("Randomness triggered: Picking a completely random cell.")
            return random.choice(avail_cells)
        
        # Step 1: Find the minimum heuristic score
        min_score: int = min(cell.heuristic_score for cell in avail_cells)            # generator expression to find the minimum score
        
        # Step 2: Collect all cells with the minimum heuristic score
        min_score_cells = [cell for cell in avail_cells if cell.heuristic_score == min_score]
        
        # Step 3: Select a random cell from the list of cells with the minimum score
        best_heuristic_cell = random.choice(min_score_cells)
        
        return best_heuristic_cell
    
    
    #############    END OF HELPERS    #############
    #                                              #
    ##########   Start of Function core   ##########

    def computer_move(self) -> Cell:

        self.get_possible_moves()
        if not self.possible_moves:
            raise ValueError(beesutils.color("Error in computer_move. Possible moves is empty. ", "red"))

        logging.debug(beesutils.color("Attempting possible moves for computer's turn...", "green"))
        result_list = self.attempt_possible_moves()                          # index matches the column

        best_move: Optional[Cell] = self.examine_list(result_list, "current")                
        if best_move is not None:                                       # return early if a winner is found
            return best_move                     

        logging.debug(beesutils.color("Checking if opponent has winning move...", "green"))
        result_list_opp = self.attempt_possible_moves(True, False)           # updater_flip True, check_above False

        best_move: Optional[Cell] = self.examine_list(result_list_opp, "opp")      
        if best_move is not None:                                       # return early if a winner is found
            return best_move
        
        if best_move is None:
            last_resort_move: Cell = self.last_resort(result_list)
            return last_resort_move
    

    ### NOTES ON HOW IT WORKS ###

    # possible_moves is a list of cell objects. Each cell object is the lowest empty cell in the column.
    # It can also be the string "FULL" if the column is full.

    # The result_list should have 4 possible entries:
    # 1) CellState.PLAYER1 or CellState.PLAYER2 if a winner is found, depending on who's turn it is
    # 2) CellState.EMPTY if no winner is found
    # 3) "FULL" if the column is full
    # 4) "BAD" if the opponent has a winning move in the cell above the current cell  

    # The result_list_opp should have 3 possible entries:
    # 1) CellState.PLAYER1 or CellState.PLAYER2 if a winner is found, depending on the opposite of who's turn it is
    # 2) CellState.EMPTY if no winner is found
    # 3) "FULL" if the column is full