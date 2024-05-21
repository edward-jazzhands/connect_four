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
