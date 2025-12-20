"""
Psychology API Request Models for Starforged AI Game Master.
"""

from pydantic import BaseModel
from typing import Optional


# Phobia System
class AddPhobiaRequest(BaseModel):
    session_id: str
    name: str
    triggers: list[str]
    severity: float = 0.5


class TriggerPhobiaRequest(BaseModel):
    session_id: str
    narrative_text: str


# Addiction System
class UseSubstanceRequest(BaseModel):
    session_id: str
    substance: str  # "alcohol", "stims", "painkillers", "hallucinogens"


# Moral Injury System
class RecordTransgressionRequest(BaseModel):
    session_id: str
    transgression_type: str  # "violence", "betrayal", "cowardice", "cruelty"
    description: str
    weight: float = 1.0


class ForgiveTransgressionRequest(BaseModel):
    session_id: str
    index: int


# Trust/Betrayal Dynamics
class AdjustTrustRequest(BaseModel):
    session_id: str
    npc_id: str
    delta: float


class RecordBetrayalRequest(BaseModel):
    session_id: str
    betrayer_id: str
    description: str
    severity: str  # "minor", "moderate", "severe", "catastrophic"


# Dream System
class TriggerDreamRequest(BaseModel):
    session_id: str
    recent_memories: list[str] = []
    suppressed_memories: list[str] = []
