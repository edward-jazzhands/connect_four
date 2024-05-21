from enum import Enum

class TurnToken(Enum):
    PLAYER1 = 1
    PLAYER2 = 2

class PlayerType(Enum):
    """ Enum for player types """
    HUMAN = 0
    COMPUTER = 1

class CellState(Enum):
    EMPTY = 0
    PLAYER1 = 1
    PLAYER2 = 2