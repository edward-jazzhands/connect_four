"""
Module Name: simmode.py

    Holds the GameSimulator class. This class is responsible for running simulations of the game.
"""


from __future__ import annotations
from typing import *
import logging

if TYPE_CHECKING:
    from gamemanager import GameManager
    from gridmaker import Cell, Grid

import beesutils
from cfenums import PlayerType, CellState



time_format = "%H:%M:%S"                         ## for the timestamp.


class GameSimulator:
    """ This class is responsible for running simulations of the game."""

    def __init__(self, game_manager: GameManager, game_loop: Callable, game_display: Callable):
        self.game_manager = game_manager
        self.game_loop = game_loop
        self.grid = game_manager.grid
        self.display = game_display

    def run_simulations(self):

        game_manager = self.game_manager
        grid = self.grid
        game_loop = self.game_loop
        display = self.display

        
        print(beesutils.color("Detected that both players are COMPUTER. Please enter the number of games to simulate."))
        logging.debug(beesutils.color("Also note you are in DEBUG mode. It will pause every turn.", "cyan"))
        logging.debug(beesutils.color("Toggle debug off to let it run automatically.", "cyan"))

        while True:
            simulation_count = input("Enter a number (or 'debug'): ")
            if simulation_count == "debug":
                beesutils.log_level_toggle()
                continue
            try:
                simulation_count = int(simulation_count)
                break
            except ValueError:
                print("Please enter a number.")

        hide_board: bool = False
        ultrasim: bool = False    

        print("Would you like to hide the board during the game?", beesutils.color("Type 'Y/y' to hide the board."))
        print("This is useful if you are running a large number of simulations.")
        print(beesutils.color("Note that it will still show the final board at the end of each game.", "cyan"))
        print(beesutils.color("Or if you want it to not show the board at ALL (for huge numbers of simulations), type 'ultrasim'.", "red"))
        hide_board_inp = input(beesutils.color("'Y/y' to hide, 'ultrasim' hides all. Anything else shows board: ")).upper()
        
        if hide_board_inp == "Y":
            hide_board = True  
        elif hide_board_inp == "ULTRASIM":
            hide_board = True
            ultrasim = True
        
        player1_wins, player2_wins, draws = 0, 0, 0
        win_direction_dict = {
            "horizontal wins": 0,
            "vertical wins": 0,
            "down-right wins": 0,
            "down-left wins": 0,
        }           
        timestamp2 = beesutils.timestamp()
                            
        for i in range(simulation_count):
            game_result: CellState = game_loop(hide_board, ultrasim)   
            print(f"Game {i+1} completed. Game result: {game_result.name}") 

            if game_result == CellState.PLAYER1:
                player1_wins += 1
            elif game_result == CellState.PLAYER2:
                player2_wins += 1
            else:
                draws += 1

            if game_result != CellState.EMPTY:        # <-- I honestly have no idea why this line needs to be here but apparently it does
                win_direction_dict[f"{game_manager.winner_direction} wins"] += 1

            grid.reset_grid()                                                # reset the grid
            display.reset_display(grid)                                 # reset the display
            game_manager.reset_game(grid.total_cells)                        # reset the game manager
            
        elapsed_time: float = beesutils.elapsed_calc(timestamp2)
        elapsed_formatted: str = beesutils.format_elapsed(elapsed_time)            

        print(beesutils.color(f"\nSimulation of {simulation_count} games completed."))
        print(beesutils.color(f"Player 1 wins: {player1_wins},", "red"), end=" ")
        print(beesutils.color(f"Player 2 wins: {player2_wins},", "blue"), f"Draws: {draws}")

        for key, value in win_direction_dict.items():
            print(f"{key}: {value}", end=" | ")

        print(f"\nStart time: {timestamp2.strftime(time_format)}, End time: {beesutils.timestamp().strftime(time_format)}")
        print(f"Simulations took {elapsed_formatted}")

    ###### End of Simulation mode #######