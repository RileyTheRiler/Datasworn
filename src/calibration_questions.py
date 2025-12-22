from src.character_identity import WoundType, IdentityScore

CALIBRATION_SCENARIO = [
    {
        "id": "background",
        "text": "Before the Ironlands, before the stars... who were you?",
        "choices": [
            {
                "id": "soldier",
                "text": "A soldier who followed orders until they couldn't.",
                "wound_impact": {WoundType.MARTYR: 0.3, WoundType.JUDGE: 0.2},
                "identity_impact": {"violence": 0.2, "dedication": 0.3}
            },
            {
                "id": "scoundrel",
                "text": "A scoundrel who lived by their wits and charm.",
                "wound_impact": {WoundType.TRICKSTER: 0.3, WoundType.HEDONIST: 0.2},
                "identity_impact": {"stealth": 0.2, "greed": 0.2}
            },
            {
                "id": "scholar",
                "text": "A researcher seeking truth in a universe of lies.",
                "wound_impact": {WoundType.PEDANT: 0.3, WoundType.CONTROLLER: 0.2},
                "identity_impact": {"logic": 0.3, "curiosity": 0.2}
            }
        ]
    },
    {
        "id": "loss",
        "text": "What did you lose that you can never get back?",
        "choices": [
            {
                "id": "family",
                "text": "My family. I failed to protect them.",
                "wound_impact": {WoundType.GHOST: 0.4, WoundType.SAVIOR: 0.2},
                "identity_impact": {"empathy": 0.2}
            },
            {
                "id": "status",
                "text": "My name. I was betrayed and stripped of honor.",
                "wound_impact": {WoundType.AVENGER: 0.4, WoundType.JUDGE: 0.2},
                "identity_impact": {"justice": 0.3}
            },
            {
                "id": "innocence",
                "text": "My innocence. I did something unforgivable.",
                "wound_impact": {WoundType.FUGITIVE: 0.4, WoundType.JUDGE: 0.2},
                "identity_impact": {"guilt": 0.3}
            }
        ]
    },
    {
        "id": "regret",
        "text": "What keeps you awake when the ship is silent?",
        "choices": [
            {
                "id": "inaction",
                "text": "The time I stood by and did nothing.",
                "wound_impact": {WoundType.COWARD: 0.3, WoundType.MARTYR: 0.2},
                "identity_impact": {"caution": 0.2}
            },
            {
                "id": "cruelty",
                "text": "The time I hurt someone just because I could.",
                "wound_impact": {WoundType.DESTROYER: 0.3, WoundType.PREDATOR: 0.2},
                "identity_impact": {"violence": 0.2}
            },
            {
                "id": "blindness",
                "text": "The time I didn't see the trap until it was too late.",
                "wound_impact": {WoundType.PARANOID: 0.3, WoundType.CONTROLLER: 0.2},
                "identity_impact": {"logic": 0.2}
            }
        ]
    },
    {
        "id": "motivation",
        "text": "Why are you out here in the Forge?",
        "choices": [
            {
                "id": "redemption",
                "text": "To make up for what I've done.",
                "wound_impact": {WoundType.MARTYR: 0.2, WoundType.SAVIOR: 0.3},
                "identity_impact": {"altruism": 0.3}
            },
            {
                "id": "escape",
                "text": "To run until they stop chasing me.",
                "wound_impact": {WoundType.FUGITIVE: 0.3, WoundType.COWARD: 0.1},
                "identity_impact": {"freedom": 0.3}
            },
            {
                "id": "power",
                "text": "To build something that lasts.",
                "wound_impact": {WoundType.CONTROLLER: 0.2, WoundType.NARCISSIST: 0.2},
                "identity_impact": {"ambition": 0.3}
            }
        ]
    }
]

def get_calibration_questions():
    """Return the list of calibration questions."""
    return CALIBRATION_SCENARIO
