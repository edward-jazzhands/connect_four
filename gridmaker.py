import logging
from enum import Enum

from cfenums import CellState


""" This is a 'grid generator' script. I'm hoping this will over time become a class that can be imported into other games. """

ANSI = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "reset": "\033[0m",
}

class Cell:
    """ Defines the properties of each cell """
    
    def __init__(self, x: int, y: int):          # Each cell has the X and Y coordinates baked in
        self.x = x                               # this is extremely useful later in the program.
        self.y = y
        self.cell_state = CellState.EMPTY
        self.heuristic_score = 0                 # Initialize with a default heuristic score
        
    def __str__(self) -> str: 
        """ Defines how the cells look when printed normally in-game. """
                         
        if self.cell_state == CellState.PLAYER1:
            return f"{ANSI['red']}⬤{ANSI['reset']}"   
        elif self.cell_state == CellState.PLAYER2:
            return f"{ANSI['blue']}⬤{ANSI['reset']}"    
        else:                               
            return "O"                        # print an O if the cell is empty
        
    def __repr__(self) -> str:
        """ __repr__ defines how the cell looks for debugging messages """

        return f"Cell x(row): {self.x}, y(col): {self.y}"
        

class Grid:
    """ This initializes a grid of cells. \n
    Takes number of rows and columns as arguments and generates grid dynamically."""

    def __init__(self, rows: int, columns: int):
        self.rows = rows                   
        self.columns = columns
        self.total_cells = rows * columns
        self.grid_matrix = [[Cell(x, y) for y in range(columns)] for x in range(rows)]
        self.assign_heuristic_scores()

        # The line above is the list comprehension version of the following
        # this is just here for educational purposes, I'm still new to list comprehensions

        # self.grid_matrix = []                          
        # for x in range(rows):                   ## For each row in the grid,
        #     row = []                            ## Create empty list for the row
        #     for y in range(columns):            ## for each column in the row
        #         new_cell = Cell(x, y)           ## New cell = Cell object with X, Y coordinates baked in
        #         row.append(new_cell)            ## Append new cell to the row list
        #     self.grid_matrix.append(row)        ## When row is finished, append to the grid

    def assign_heuristic_scores(self):
        """ Assigns heuristic scores to each cell in the grid. """

        # Assigns the highest number to the top row and the lowest number to the bottom row. Lower is better.
        row_scores = [i for i in range(self.rows, -1, -1)]

        center = self.columns // 2      # // floor division, rounds down to the nearest whole number
        col_scores = []
        for j in range(self.columns):
            dist_from_center = abs(j - center)
            col_scores.append(dist_from_center)

        for i in range(self.rows):
            for j in range(self.columns):
                heuristic_score = row_scores[i] + col_scores[j]     # lower is better
                self.grid_matrix[i][j].heuristic_score = heuristic_score

    def reset_grid(self):
        """ Resets the grid to its default state. """

        for row in self.grid_matrix:
            for cell in row:
                cell.cell_state = CellState.EMPTY

