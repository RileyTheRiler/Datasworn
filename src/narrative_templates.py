"""
Narrative Templates for Character Paths

Provides narrative guidance and suggested vows for each character Path type,
helping players create compelling character concepts that align with their
chosen archetype.
"""

from typing import Dict, List

# Categorize paths by archetype
PATH_CATEGORIES = {
    "combat": [
        "Armored", "Blademaster", "Gunslinger", "Slayer", "Weapon Master",
        "Veteran", "Bounty Hunter", "Sniper"
    ],
    "exploration": [
        "Explorer", "Naturalist", "Navigator", "Lore Hunter", "Scavenger",
        "Ace", "Courier"
    ],
    "social": [
        "Diplomat", "Empath", "Leader", "Loyalist", "Trader", "Artist"
    ],
    "technical": [
        "Gearhead", "Tech", "Demolitionist"
    ],
    "stealth": [
        "Infiltrator", "Sleuth", "Archer", "Outcast", "Scoundrel", "Fugitive"
    ],
    "mystical": [
        "Seer", "Shade", "Voidborn", "Haunted", "Fated", "Vestige",
        "Kinetic", "Looper"
    ],
    "support": [
        "Healer", "Mercenary", "Firedrand"
    ]
}


# Narrative templates for each category
NARRATIVE_TEMPLATES = {
    "combat": {
        "description": "Warriors and fighters who excel in direct confrontation.",
        "playstyle": "Aggressive, action-oriented gameplay with high-stakes combat encounters.",
        "suggested_vows": [
            "Hunt down the warlord who destroyed my home settlement",
            "Protect the Outer Rim colonies from raider attacks",
            "Prove myself worthy by defeating the legendary duelist of Anvil Station",
            "Find redemption for the innocent lives lost under my command",
            "Master the ancient combat techniques of the Precursors"
        ],
        "narrative_hooks": [
            "You carry the weapon of someone you failed to save",
            "A rival warrior has sworn to defeat you in single combat",
            "Your reputation precedes you, attracting both allies and enemies",
            "You're haunted by a battle where you made the wrong choice"
        ]
    },
    "exploration": {
        "description": "Adventurers and scouts who thrive in unknown territory.",
        "playstyle": "Discovery-focused gameplay with emphasis on mapping the Forge and uncovering secrets.",
        "suggested_vows": [
            "Chart the unexplored regions beyond the Void Gate",
            "Discover the lost colony ship that vanished during the Exodus",
            "Recover the ancient star map hidden in Precursor ruins",
            "Find a new habitable world for my dying settlement",
            "Uncover the truth behind the mysterious signal from the Deep Void"
        ],
        "narrative_hooks": [
            "You possess a cryptic map fragment passed down through generations",
            "A missing expedition member was someone you cared about deeply",
            "You're driven by curiosity that has gotten you into trouble before",
            "You carry evidence of something unprecedented that no one believes"
        ]
    },
    "social": {
        "description": "Negotiators and influencers who change the Forge through words and relationships.",
        "playstyle": "Diplomatic gameplay focused on building alliances and navigating complex social dynamics.",
        "suggested_vows": [
            "Broker peace between two warring factions before all-out war erupts",
            "Unite the scattered settlements under a common cause",
            "Expose the corruption at the heart of the Trade Syndicate",
            "Find and rescue a kidnapped diplomat before political collapse",
            "Negotiate safe passage through hostile territory for refugee ships"
        ],
        "narrative_hooks": [
            "You once brokered a deal that backfired catastrophically",
            "A powerful faction leader owes you a debt they'd rather forget",
            "Your reputation as a mediator is both your greatest asset and liability",
            "You carry a secret that could shift the balance of power"
        ]
    },
    "technical": {
        "description": "Engineers and technicians who solve problems through innovation and expertise.",
        "playstyle": "Problem-solving gameplay emphasizing creativity and technical solutions.",
        "suggested_vows": [
            "Reverse-engineer Precursor technology to save failing systems",
            "Sabotage the weapons project built from my stolen designs",
            "Repair the derelict generation ship before life support fails",
            "Create a device that will revolutionize Forge travel",
            "Destroy the AI that has taken control of Terminus Station"
        ],
        "narrative_hooks": [
            "Your invention was used for something terrible you never intended",
            "You can see mechanical solutions others miss, but struggle socially",
            "A piece of technology you carry is unique and highly sought after",
            "You're racing against time before your rival completes their own version"
        ]
    },
    "stealth": {
        "description": "Infiltrators and shadows who operate from the margins.",
        "playstyle": "Covert gameplay focused on information gathering, infiltration, and avoiding direct conflict.",
        "suggested_vows": [
            "Steal classified data that will expose a criminal conspiracy",
            "Infiltrate the heavily guarded fortress to rescue prisoners",
            "Discover who framed me for crimes I didn't commit",
            "Track down the assassin who killed my mentor",
            "Recover stolen artifacts from a black market syndicate"
        ],
        "narrative_hooks": [
            "You're wanted by authorities for something you may or may not have done",
            "You know secrets about powerful people who want you silenced",
            "Your face is too well-known in certain circles for your own good",
            "You carry evidence of a crime that could bring down empires"
        ]
    },
    "mystical": {
        "description": "Those touched by forces beyond normal understanding.",
        "playstyle": "Supernatural gameplay exploring the strange and inexplicable aspects of the Forge.",
        "suggested_vows": [
            "Understand the visions that plague my dreams before they consume me",
            "Seal the Void rift that threatens to tear reality apart",
            "Find others like me who can manipulate reality itself",
            "Stop the ritual that will awaken something ancient and terrible",
            "Master my powers before they destroy me and everyone around me"
        ],
        "narrative_hooks": [
            "Your abilities manifest unpredictably, often at the worst moments",
            "Others fear or revere you for powers you don't fully understand",
            "You're connected to the Void in ways that both help and haunt you",
            "A precognitive vision showed you your death, but not when or how to prevent it"
        ]
    },
    "support": {
        "description": "Specialists who keep others alive and missions successful.",
        "playstyle": "Team-focused gameplay emphasizing helping others and maintaining group cohesion.",
        "suggested_vows": [
            "Keep my crew alive through the dangerous mission ahead",
            "Atone for the patient I couldn't save by saving countless others",
            "Find a cure for the plague ravaging the Outer Rim settlements",
            "Train the next generation of specialists before I retire",
            "Prove that compassion is strength, not weakness"
        ],
        "narrative_hooks": [
            "You swore an oath to heal, but violence sometimes seems necessary",
            "Someone you saved went on to do terrible things",
            "You carry medical supplies or tools that are desperately needed elsewhere",
            "Your skills make you invaluable, which means everyone wants to control you"
        ]
    }
}


def get_path_category(path_name: str) -> str:
    """Determine which category a given path belongs to."""
    for category, paths in PATH_CATEGORIES.items():
        if path_name in paths:
            return category
    return "combat"  # Default category


def get_narrative_template(path_name: str) -> Dict:
    """Get the narrative template for a specific path."""
    category = get_path_category(path_name)
    return NARRATIVE_TEMPLATES.get(category, NARRATIVE_TEMPLATES["combat"])


def get_suggested_vows_for_path(path_name: str) -> List[str]:
    """Get suggested starting vows for a specific path."""
    template = get_narrative_template(path_name)
    return template.get("suggested_vows", [])


def get_narrative_hooks_for_path(path_name: str) -> List[str]:
    """Get narrative hooks that could inspire character backgrounds for a specific path."""
    template = get_narrative_template(path_name)
    return template.get("narrative_hooks", [])


def get_all_templates() -> Dict[str, Dict]:
    """Return all narrative templates organized by category."""
    return NARRATIVE_TEMPLATES
