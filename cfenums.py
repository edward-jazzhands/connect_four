"""
Module Name: cfenums.py

    'CF Enums' stands for 'Connect Four Enums'. \n
    Contains the 3 enums used in the Connect Four game. Needs to be in its own file so it can be imported and used in all the other modules.
"""


from enum import Enum

class TurnToken(Enum):
    PLAYER1 = 1
    PLAYER2 = 2

class CellState(Enum):
    EMPTY = 0
    PLAYER1 = 1
    PLAYER2 = 2

class PlayerType(Enum):
    HUMAN = 0
    COMPUTER = 1
