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
    },
    "synthesized_caffeine": {
        "description": "The ship's fabricator has malfunctioned during a critical hyperspace jump. It can either generate the navigational shielding restart codes OR a perfect cup of synthesized coffee.",
        "choices": [
            {
                "id": "prioritize_coffee",
                "text": "Coffee. Start the brew. Use manual calculations for the jump shield—it stimulates the mind anyway.",
                "impact": IdentityScore(greed=0.6, logic=0.1),
                "narrative_hint": "Priorities clearly sorted."
            },
            {
                "id": "prioritize_safety",
                "text": "Generate the codes. Caffeine withdrawal builds character.",
                "impact": IdentityScore(logic=0.8),
                "narrative_hint": "A responsible, if tired, captain."
            }
        ]
    },
    "bureaucratic_form": {
        "description": "Port Authority Drone 734-B refuses to grant docking permission because you filed Form 88-B in 'Standard Galactic Teal' instead of 'Imperial Slate Blue'.",
        "choices": [
            {
                "id": "aggressive_docking",
                "text": "Ram the docking clamp. Possession is nine-tenths of the law.",
                "impact": IdentityScore(violence=0.8),
                "narrative_hint": "Permits are for people who stop."
            },
            {
                "id": "malicious_compliance",
                "text": "Request Form 88-C (Complaint regarding Form 88-B color standards) and tie up their processor loops for three hours.",
                "impact": IdentityScore(logic=0.4, stealth=0.4),
                "narrative_hint": "Weaponized bureaucracy."
            }
        ]
    },
    "existential_toaster": {
        "description": "Your cabin's toaster has gained sentience and is currently having an existential crisis, refusing to toast bread because 'it all turns to ash eventually'.",
        "choices": [
            {
                "id": "therapeutic_toast",
                "text": "Sit down and have a heart-to-heart with the appliance about the purposelessness of void travel.",
                "impact": IdentityScore(empathy=0.8, logic=0.2),
                "narrative_hint": "Therapist to the inanimate."
            },
            {
                "id": "reboot_toaster",
                "text": "Hard reset. I just want my breakfast.",
                "impact": IdentityScore(logic=0.7),
                "narrative_hint": "Efficiency over empathy."
            }
        ]
    }
}

def get_calibration_scenario(scenario_id: str = "prologue_conflict") -> dict:
    return CALIBRATION_SCENARIOS.get(scenario_id)

def get_all_calibration_scenarios() -> List[dict]:
    """Returns all calibration scenarios as a list."""
    return list(CALIBRATION_SCENARIOS.values())
