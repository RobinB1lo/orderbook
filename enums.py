from enum import Enum


class Side(Enum):
    SELL = 0
    BUY = 1


class Type(Enum):
    LIMIT = 0
    MARKET = 1
    FOK = 2
