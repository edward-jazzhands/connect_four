import logging
from enum import Enum

from cfenums import CellState


""" This is a 'grid generator' script. I'm hoping this will over time become a class that can be imported into other games. """



class Cell:
    """ Defines the properties of each cell """
    def __init__(self, x: int, y: int):         # Each cell has the X and Y coordinates baked in
        self.x = x
        self.y = y
        self.cell_state = CellState.EMPTY
        
    def __str__(self) -> str:                    # This is used when the object is printed
        """ Defining how to print cells inside the __str__ method allows us to separate
        this logic from the display function. We can modify how they look here without changing the display function. """
                         
        if self.cell_state == CellState.PLAYER1:
            return "\033[31m⬤\033[0m"   
        elif self.cell_state == CellState.PLAYER2:
            return "\033[34m⬤\033[0m"    
        else:                               
            return "O"                        # print an O if the cell is empty
        

class Grid:
    """ This initializes a grid of cells."""

    def __init__(self, rows: int, columns: int):
        self.rows = rows                   
        self.columns = columns
        try:
            self.grid_matrix = [[Cell(x, y) for y in range(columns)] for x in range(rows)]
        except Exception as e:
            logging.error(f"Error initializing grid: {e}")
            raise e

        # The line in the try block above is the list comprehension version of the following
        # this is just here for educational purposes, I'm still new to list comprehensions

        # self.grid_matrix = []                          
        # for x in range(rows):                   ## For each row in the grid,
        #     row = []                            ## Create empty list for the row
        #     for y in range(columns):            ## for each column in the row
        #         new_cell = Cell(x, y)           ## New cell = Cell object with X, Y coordinates
        #         row.append(new_cell)            ## Append new cell to the row list
        #     self.grid_matrix.append(row)        ## When row is finished, append to the grid