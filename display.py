"""
Module Name: display.py

    This is the 'display' module. It contains the Display class, which is responsible for displaying the game grid. \n
"""

# TO DO - add a feature to display the NumPy array instead of the grid matrix
# TO DO - divide display into subclasses and add turtle graphics

from __future__ import annotations
from typing import *
import logging
import abc
import logging
from string import ascii_uppercase

if TYPE_CHECKING:
    from gridmaker import Cell, Grid

import beesutils

class Display:
    """ This class contains the display functions for the game. """

    def __init__(self, grid: Grid):
        self.grid = grid
        self.show_heuristic = False
        self.show_numpy = False
 
    def display_func(self) -> None:
        """ This function handles the display of whatever grid is passed into it \n
        Automatically adjusts the border based on the grid size. """

        # Box drawing characters
        top_left = "┏"
        top_right = "┓"
        bottom_left = "┗"
        bottom_right = "┛"
        horizontal = "━"
        vertical = "┃"

        grid = self.grid
        top_bar = f"   {top_left + horizontal * (grid.columns*3 + 2) + top_right}"
        bottom_bar = f"   {bottom_left + horizontal * (grid.columns*3 + 2) + bottom_right}"
        # (grid.columns*3 + 2) is because each cell is 3 characters wide, plus 2 for the ends

        # note the ASCII spacing is different on every side of the board. This is just to make it look great in the console.
        # so there's not really a better way to code this. It's just a lot of manual spacing.
        
        print("")
        print(top_bar)          

        for row in range(grid.rows):
            print(f"   {vertical} ", end="") 

            for column in range(grid.columns):
                if self.show_heuristic:
                    print(f" {grid.grid_matrix[row][column].heuristic_score} ", end="")   # notice the spaces in the f-string
                elif self.show_numpy:
                    print(f" {grid.numpy_grid[row, column]} ", end="")    # prints the numpy array instead of the grid matrix                  
                else:
                    print(f" {grid.grid_matrix[row][column]} ", end="")    # prints whatever object is at that location in the grid matrix

            print(f" {vertical}")  
        print(bottom_bar)   
              
        print("    ", end="")
        for i in range(grid.columns):
            print(" ", ascii_uppercase[i], end="")              # prints the column letters at the bottom
        print("\n")

    def reset_display(self, grid: Grid) -> None:
        """ Resets the display to the default state. """

        self.grid = grid
        self.show_heuristic = False
        self.show_numpy = False

    def toggle_feature(self, feature: str) -> None:
        """Toggle the display of a specific feature."""

        feature_dict = {
            "heuristic": "show_heuristic",
            "numpy": "show_numpy",
        }

        if feature in feature_dict:
            logging.debug(f"Feature dict incoming: {feature_dict}")
            
            attr_name = feature_dict[feature]
            current_value = getattr(self, attr_name)
            setattr(self, attr_name, not current_value)
            status = "on" if not current_value else "off"

            logging.debug(beesutils.color(f"{feature.capitalize()} scores turned {status}.", "green"))
            logging.debug(f"Feature dict outgoing: {feature_dict}")








# class Display(abc.ABC):
#     """Abstract superclass for different display implementations."""

#     @abc.abstractmethod
#     def display_func(self) -> None:
#         """Abstract method to handle the display of the game."""
#         pass

#     @abc.abstractmethod
#     def reset_display(self, grid) -> None:
#         """Abstract method to reset the display."""
#         pass

#     @abc.abstractmethod
#     def toggle_feature(self, feature: str) -> None:
#         """Abstract method to toggle a display feature."""
#         pass

# class TerminalDisplay(Display):
#     """Terminal display implementation."""

#     def __init__(self, grid: object):
#         # Initialize TerminalDisplay specific attributes
#         pass

#     def display_func(self) -> None:
#         """Override display function for terminal."""
#         # Terminal display logic
#         pass

#     def reset_display(self, grid) -> None:
#         """Override reset display function for terminal."""
#         # Terminal reset display logic
#         pass

#     def toggle_feature(self, feature: str) -> None:
#         """Override toggle feature function for terminal."""
#         # Terminal toggle feature logic
#         pass

# class TurtleDisplay(Display):
#     """Turtle display implementation."""

#     def __init__(self, grid: object):
#         # Initialize TurtleDisplay specific attributes
#         pass

#     def display_func(self) -> None:
#         """Override display function for Turtle."""
#         # Turtle display logic
#         pass

#     def reset_display(self, grid) -> None:
#         """Override reset display function for Turtle."""
#         # Turtle reset display logic
#         pass

#     def toggle_feature(self, feature: str) -> None:
#         """Override toggle feature function for Turtle."""
#         # Turtle toggle feature logic
#         pass

