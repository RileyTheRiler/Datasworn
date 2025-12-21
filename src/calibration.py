"""
Calibration Scenarios for Starforged AI Game Master.
Defines the initial branching choices that establish the baseline character identity.
"""

from typing import List, Dict
from .character_identity import IdentityScore

CALIBRATION_SCENARIOS = {
    "prologue_conflict": {
        "description": "You are pinned down behind a rusted bulkhead as the Syndicate scavengers close in. The air is thick with the smell of scorched ozone.",
        "choices": [
            {
                "id": "direct_assault",
                "text": "Check your mag-pulse charges and charge into the fray, weapons hot.",
                "impact": IdentityScore(violence=0.5, logic=0.1),
                "narrative_hint": "The Brute takes the lead."
            },
            {
                "id": "shadow_slip",
                "text": "Wait for the decompression cycle and slip through the maintenance vents in the chaos.",
                "impact": IdentityScore(stealth=0.5, logic=0.2),
                "narrative_hint": "The Shadow moves unseen."
            },
            {
                "id": "negotiate_exit",
                "text": "Open a channel to the scavengers. Everyone has a price, and you know their lead hunter's reputation.",
                "impact": IdentityScore(empathy=0.4, greed=0.2),
                "narrative_hint": "The Diplomat finds a path."
            }
        ]
    }
}

def get_calibration_scenario(scenario_id: str = "prologue_conflict") -> dict:
    return CALIBRATION_SCENARIOS.get(scenario_id)
