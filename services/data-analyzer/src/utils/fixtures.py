from enum import StrEnum


class Action(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class MAState(StrEnum):
    SURPLUS = "SURPLUS"
    DEFICIT = "DEFICIT"
    NONE = "NONE"
