"""
Psychology System Enums and Types.
"""

from enum import Enum


class SubstanceType(str, Enum):
    ALCOHOL = "alcohol"
    STIMS = "stims"
    PAINKILLERS = "painkillers"
    HALLUCINOGENS = "hallucinogens"


class TransgressionType(str, Enum):
    VIOLENCE = "violence"
    BETRAYAL = "betrayal"
    COWARDICE = "cowardice"
    CRUELTY = "cruelty"


class BetrayalSeverity(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"
