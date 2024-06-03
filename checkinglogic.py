"""
Module Name: complogic.py

    This module holds the CheckingSystem class. This class is responsible for checking the grid for a winner and
    it is also responsible for checking if a column is full and returning the lowest empty cell in the column.
"""


from __future__ import annotations
from typing import *

import logging

import beesutils
from cfenums import CellState

if TYPE_CHECKING:
    from gridmaker import Grid, Cell
    from gamemanager import GameManager



class CheckingSystem:

    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager
        self.grid = game_manager.grid
        self.grid_matrix = self.grid.grid_matrix
        self.numpy_grid = self.grid.numpy_grid


    def check_column(self, column_index: int) -> Cell:
        """ This scans from the bottom up and returns the first empty cell it hits."""
        # This is actually more efficient than scanning from the top down because we don't need to keep a running list of empty cells.

        for row in range(self.grid.rows - 1, -1, -1):                       # scans the column from the bottom up
            current_cell = self.grid_matrix[row][column_index]              # iterate through the column              
            if current_cell.cell_state == CellState.EMPTY:             # as soon as it hits an empty cell,
                return current_cell                                    # return the cell


    ##########   Check for winner Function   ###########

    def check_win(self, feed_grid: Grid, test_mode: bool = False) -> CellState:
        """Checks the grid for a winner. If winner, returns CellState of winner, otherwise CellState.EMPTY.
        When test_mode is set to True, it will not update the winner_direction or win_starting_column variables. 
        Note you HAVE TO pass in the grid because it can scan cloned grids as well (not limited to main self grid!)"""

        logging.debug(f"Starting check_win function. {beesutils.color(f'Test mode: {test_mode}', 'orange')} ")

        grid = feed_grid
        grid_matrix = feed_grid.grid_matrix
        numpy_grid = self.numpy_grid

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

        def check_line(cell: Cell, direction_name: str) -> CellState:
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
                self.game_manager.winner_direction = direction_name               
                self.game_manager.win_starting_column = cell.y
                logging.debug(beesutils.color(f"self.winner_direction set to: {self.game_manager.winner_direction}", "cyan"))
                logging.debug(beesutils.color(f"self.win_starting_column set to: {self.game_manager.win_starting_column}", "cyan"))
            return cell.cell_state
        
        #### End of Helpers ######
        
        for row in range(grid.rows):
            for col in range(grid.columns):
                
                cell: Cell = grid_matrix[row][col]
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