"""
Ship Campaign Template - The Exile's Gambit

A ready-to-play campaign set aboard a single starship with a small crew.
Designed to showcase all 48 AI systems in a constrained, high-tension setting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


class ShipZone(Enum):
    BRIDGE = "bridge"
    ENGINEERING = "engineering"
    CARGO_BAY = "cargo_bay"
    CREW_QUARTERS = "crew_quarters"
    MEDICAL_BAY = "medical_bay"
    MESS_HALL = "mess_hall"
    AIRLOCK = "airlock"
    CRAWLWAYS = "crawlways"


ZONE_DESCRIPTIONS = {
    ShipZone.BRIDGE: {
        "description": "The nerve center. Holographic displays cast blue light across worn consoles.",
        "atmosphere": "Control, visibility, vulnerability",
        "secrets": "Captain Reyes personal logs are encrypted here"
    },
    ShipZone.ENGINEERING: {
        "description": "A cathedral of machinery. The drift drive hums with barely-contained energy.",
        "atmosphere": "Power, danger, necessity",
        "secrets": "Someone has been modifying the fuel consumption logs"
    },
    ShipZone.CARGO_BAY: {
        "description": "Crates stacked high, shadows deeper. Half the cargo is legitimate.",
        "atmosphere": "Hidden things, commerce, survival",
        "secrets": "Sealed crate in the corner - no one admits to loading it"
    },
    ShipZone.CREW_QUARTERS: {
        "description": "Six bunks, six lives compressed into metal and fabric.",
        "atmosphere": "Intimacy, privacy, vulnerability",
        "secrets": "Each crew member hides something in their bunk"
    },
    ShipZone.MEDICAL_BAY: {
        "description": "Sterile white fighting a losing battle against grime.",
        "atmosphere": "Healing, fragility, truth",
        "secrets": "Medical records reveal old injuries and lies"
    },
    ShipZone.MESS_HALL: {
        "description": "A table bolted to the deck. Recycled food, recycled air, recycled grievances.",
        "atmosphere": "Community, conflict, humanity",
        "secrets": "Where alliances form and break"
    },
    ShipZone.AIRLOCK: {
        "description": "The thin line between life and void.",
        "atmosphere": "Threshold, danger, finality",
        "secrets": "Evidence of a spacewalk no one authorized"
    },
    ShipZone.CRAWLWAYS: {
        "description": "Maintenance tunnels threading through the ship bones. Dark, cramped, forgotten.",
        "atmosphere": "Secrecy, danger, shortcuts",
        "secrets": "Someone has been using these to move unseen"
    }
}


# Crew data as simple dictionaries to avoid dataclass issues
CREW_MEMBERS = [
    {
        "name": "Torres",
        "role": "Pilot",
        "age": 34,
        "background": "Former military pilot, dishonorably discharged for refusing orders.",
        "ocean": {"O": 0.4, "C": 0.8, "E": 0.3, "A": 0.5, "N": 0.6},
        "public_goal": "Get the ship to safe harbor",
        "secret_goal": "Find her brother who was on Station Omega when it went dark",
        "fear": "Losing another crewmate the way she lost her squadron",
        "secret": "She knows Captain Reyes was murdered. She saw something.",
        "voice": "Clipped, military precision. Long pauses before speaking."
    },
    {
        "name": "Kai",
        "role": "Engineer",
        "age": 28,
        "background": "Grew up on ships. Genius with machines, disaster with people.",
        "ocean": {"O": 0.7, "C": 0.5, "E": 0.4, "A": 0.6, "N": 0.5},
        "public_goal": "Keep the ship running",
        "secret_goal": "Escape the debt he owes to dangerous people",
        "fear": "Being trapped, being controlled",
        "secret": "He has been skimming fuel to pay his debts. The shortage is not natural.",
        "voice": "Fast, technical, interrupted thoughts. Awkward about feelings."
    },
    {
        "name": "Dr. Okonkwo",
        "role": "Medic",
        "age": 52,
        "background": "Was a respected surgeon before the malpractice accusation.",
        "ocean": {"O": 0.6, "C": 0.7, "E": 0.5, "A": 0.8, "N": 0.4},
        "public_goal": "Keep the crew healthy and alive",
        "secret_goal": "Prove she was framed, clear her name",
        "fear": "Making another mistake, losing another patient",
        "secret": "She found something in Captain Reyes autopsy she has not told anyone.",
        "voice": "Measured, warm, precise. Uses medical terms when nervous."
    },
    {
        "name": "Vasquez",
        "role": "Cargo Master",
        "age": 41,
        "background": "Former smuggler who went legitimate. His underworld contacts still call.",
        "ocean": {"O": 0.5, "C": 0.4, "E": 0.7, "A": 0.3, "N": 0.5},
        "public_goal": "Move cargo, get paid, stay alive",
        "secret_goal": "Retrieve the sealed crate before anyone opens it",
        "fear": "His past catching up with him, being exposed",
        "secret": "The sealed crate contains evidence that could destroy powerful people.",
        "voice": "Smooth, too friendly, always selling something. Voice hardens when cornered."
    },
    {
        "name": "Ember",
        "role": "Apprentice",
        "age": 19,
        "background": "Stowaway who earned her place. Running from a colony where she was property.",
        "ocean": {"O": 0.8, "C": 0.5, "E": 0.6, "A": 0.7, "N": 0.6},
        "public_goal": "Learn everything, become indispensable",
        "secret_goal": "Never go back, never be owned again",
        "fear": "Being sent away, being found by the people she escaped",
        "secret": "She overheard Vasquez and Yuki talking about Captain Reyes death.",
        "voice": "Quick, eager, questions everything. Voice drops when scared."
    },
    {
        "name": "Yuki",
        "role": "Security",
        "age": 37,
        "background": "Corporate enforcer who walked away. No one walks away.",
        "ocean": {"O": 0.3, "C": 0.9, "E": 0.2, "A": 0.2, "N": 0.3},
        "public_goal": "Keep the ship secure, stay useful",
        "secret_goal": "Stay hidden until the heat dies down, disappear at the next port",
        "fear": "Being found, being forced to do what they used to do",
        "secret": "They killed Captain Reyes. It was supposed to look like an accident.",
        "voice": "Minimal words, flat affect. When they speak, every word matters."
    }
]


def get_ship_campaign_state() -> Dict[str, Any]:
    """Returns complete initial state for the ship campaign."""
    
    companions = {}
    for crew in CREW_MEMBERS:
        companions[crew["name"]] = {
            "name": crew["name"],
            "role": crew["role"],
            "loyalty": 0.5,
            "mood": "worried",
            "personal_goal": crew["secret_goal"],
            "fear": crew["fear"],
            "approval_history": [],
            "scenes_since_spotlight": 0,
            "arc_stage": "introduction"
        }
    
    return {
        "final_systems": {
            "voice": {
                "established_voice": "literary",
                "established_tone": "gritty",
                "vocabulary_register": "elevated",
                "forbidden_elements": ["modern Earth slang", "breaking fourth wall", "easy solutions"],
                "preferred_elements": ["claustrophobic atmosphere", "interpersonal tension", "subtext in dialogue"]
            },
            "memory": {
                "consolidated_memories": [
                    {
                        "memory_id": "mem_0_0",
                        "summary": "Captain Reyes died three days ago. Officially: heart failure. The crew knows better.",
                        "importance": "critical",
                        "scene_range": [0, 0],
                        "key_entities": ["Captain Reyes"],
                        "emotional_weight": 0.9,
                        "tags": ["death", "mystery"]
                    }
                ],
                "current_scene": 1,
                "consolidation_threshold": 10
            },
            "encounters": {"recent_types": [], "encounter_count": 0}
        },
        
        "faction_environment": {
            "environment": {
                "current_conditions": {
                    "weather": "vacuum",
                    "hazards": [],
                    "temperature": "recycled-cold",
                    "visibility": "shipboard-normal",
                    "atmosphere_notes": "The air smells of recycled everything.",
                    "duration_remaining": 99
                }
            },
            "economy": {
                "resources": {
                    "fuel": {"resource_type": "fuel", "current": 45, "maximum": 100, "consumption_rate": 3, "scarcity_local": 0.7},
                    "supplies": {"resource_type": "supplies", "current": 60, "maximum": 100, "consumption_rate": 2, "scarcity_local": 0.5},
                    "medical": {"resource_type": "medical", "current": 30, "maximum": 50, "consumption_rate": 0.5, "scarcity_local": 0.8}
                }
            },
            "companions": {
                "companions": companions,
                "party_morale": 0.4,
                "party_cohesion": 0.5,
                "internal_conflicts": [
                    {"members": ["Torres", "Vasquez"], "reason": "Torres suspects Vasquez is hiding something"},
                    {"members": ["Kai", "Dr. Okonkwo"], "reason": "Conflict over Kai stim use"}
                ]
            }
        },
        
        "quest_lore": {
            "quests": {
                "discover_truth": {
                    "quest_id": "discover_truth",
                    "title": "The Captain Death",
                    "description": "Find out what really happened to Captain Reyes",
                    "quest_type": "main",
                    "status": "active",
                    "objectives": [
                        {"objective_id": "obj1", "description": "Review medical records", "is_completed": False, "is_optional": False},
                        {"objective_id": "obj2", "description": "Interview crew members", "is_completed": False, "is_optional": False},
                        {"objective_id": "obj3", "description": "Determine who is responsible", "is_completed": False, "is_optional": False}
                    ],
                    "narrative_stakes": "Trust on this ship is already thin."
                }
            },
            "lore": {
                "established_facts": {
                    "ship:name": "The Exile Gambit, Wanderer-class freighter",
                    "ship:age": "22 years old, patched more times than anyone can count",
                    "captain:death": "Three days ago, found in his chair on the bridge",
                    "destination:name": "Meridian Station, 8 days at current speed"
                }
            },
            "rumors": {
                "rumors": {
                    "reyes_murder": {
                        "rumor_id": "reyes_murder",
                        "content": "Captain Reyes did not die of heart failure. Someone killed him.",
                        "rumor_type": "true",
                        "source_npc": "Torres",
                        "known_by": ["Torres", "Dr. Okonkwo"],
                        "distortion_level": 0.0
                    },
                    "fuel_shortage": {
                        "rumor_id": "fuel_shortage",
                        "content": "We are burning fuel faster than we should.",
                        "rumor_type": "true",
                        "source_npc": "Torres",
                        "known_by": ["Torres", "Kai", "Vasquez"],
                        "distortion_level": 0.1
                    }
                },
                "npc_connections": {
                    "Torres": ["Dr. Okonkwo", "Kai"],
                    "Kai": ["Torres", "Ember"],
                    "Dr. Okonkwo": ["Torres", "Ember"],
                    "Vasquez": ["Yuki"],
                    "Ember": ["Kai", "Dr. Okonkwo"],
                    "Yuki": ["Vasquez"]
                }
            }
        },
        
        "advanced_simulation": {
            "relationships": {
                "relationships": {
                    "Torres:Dr. Okonkwo": {
                        "entity_a": "Torres", "entity_b": "Dr. Okonkwo",
                        "relationship_type": "friendship",
                        "dimensions": {"trust": 0.6, "respect": 0.7, "affection": 0.5}
                    },
                    "Vasquez:Yuki": {
                        "entity_a": "Vasquez", "entity_b": "Yuki",
                        "relationship_type": "professional",
                        "dimensions": {"trust": -0.3, "respect": 0.2, "fear": 0.4}
                    }
                }
            },
            "time": {
                "current_day": 1,
                "current_time": "morning",
                "deadlines": {"fuel_critical": 8}
            },
            "dialogue": {
                "memories": [
                    {
                        "speaker": "Torres", "listener": "Player",
                        "content": "Reyes did not just die. I have seen death. That was not natural.",
                        "scene": 0, "emotional_context": "grim warning",
                        "is_lie": False, "is_promise": False, "is_secret": True
                    }
                ],
                "current_scene": 1
            }
        },
        
        "character_arcs": {
            "protagonist": {
                "name": "Player",
                "current_phase": "ordinary_world",
                "flaw": "Untested as a leader, unsure who to trust",
                "external_goal": "Reach safe harbor and keep the crew alive",
                "internal_goal": "Become the captain they need"
            },
            "foreshadowing": {
                "seeds": [
                    {"seed_id": "sealed_crate", "type": "chekhov_gun", "description": "The sealed crate in the cargo bay", "importance": 0.8},
                    {"seed_id": "yuki_past", "type": "mystery", "description": "Why did Yuki really join this crew?", "importance": 0.7},
                    {"seed_id": "fuel_shortage", "type": "promise", "description": "The fuel is running low too fast", "importance": 0.6}
                ]
            }
        }
    }


def get_opening_scene() -> str:
    return """
The Exile Gambit drifts through the void, three days out from Station Omega, 
eight days from Meridian. The captain chair is empty - no, not empty. NEW.

You sit in it now, voted in by a crew that had no better options. Torres 
barely looked at you. Vasquez smiled too wide. The others... watched.

Captain Reyes is in cold storage. Heart failure, according to Dr. Okonkwo 
report. But the way Torres looked at the body, the way Yuki will not meet 
anyone eyes - something happened on this ship. Something wrong.

The morning watch has started. Through the viewscreen, stars wheel slowly 
as the drift drive carries you toward uncertain salvation. 

Six crew. One corpse. Eight days of recycled air and recycled secrets.

*You are the captain now. What do you do?*
"""


def get_crew_summary() -> str:
    return """
## The Crew of the Exile Gambit

**Torres** (Pilot, 34) - Former military. Disciplined. Watches Vasquez.
**Kai** (Engineer, 28) - Ship-born genius. Nervous. Stim problem.
**Dr. Okonkwo** (Medic, 52) - Calm. Kind. Hiding something about Reyes death.
**Vasquez** (Cargo Master, 41) - Smooth talker. Too many secrets.
**Ember** (Apprentice, 19) - Young. Sharp. Sees things others miss.
**Yuki** (Security, 37) - Cold. Efficient. Dangerous.

*One of them killed Captain Reyes. Or they are all hiding something else entirely.*
"""


def initialize_ship_campaign(game_state: Dict) -> Dict:
    """Initialize a new ship campaign by merging template state into game state."""
    template_state = get_ship_campaign_state()
    
    for key, value in template_state.items():
        if key not in game_state:
            game_state[key] = value
        elif isinstance(value, dict) and isinstance(game_state[key], dict):
            game_state[key].update(value)
    
    return game_state


if __name__ == "__main__":
    print("THE EXILE GAMBIT - Ship Campaign Template")
    print("=" * 50)
    print(get_opening_scene())
    print(get_crew_summary())
    print("\nTemplate loaded successfully!")
