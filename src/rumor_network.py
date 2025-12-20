"""
Rumor Network System for Starforged AI Game Master.
Generates and tracks procedural rumors and intel.
"""

from dataclasses import dataclass, field
from typing import Any
import random
from datetime import datetime, timedelta


@dataclass
class Rumor:
    """A single rumor or piece of intel."""
    id: str
    title: str
    description: str
    source: str  # NPC or location
    reliability: float  # 0.0 (false) to 1.0 (true)
    category: str  # "treasure", "danger", "opportunity", "mystery"
    location_hint: str = ""
    expires_at: str = ""  # ISO timestamp
    investigated: bool = False
    verified: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "reliability": self.reliability,
            "category": self.category,
            "location_hint": self.location_hint,
            "expires_at": self.expires_at,
            "investigated": self.investigated,
            "verified": self.verified
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Rumor":
        return cls(**data)


class RumorNetwork:
    """Manages the rumor and intel system."""
    
    def __init__(self):
        self.rumors: dict[str, Rumor] = {}
        self.rumor_counter: int = 0
        
    def generate_rumor(self, source: str, category: str = None) -> Rumor:
        """Generate a new procedural rumor."""
        if category is None:
            category = random.choice(["treasure", "danger", "opportunity", "mystery"])
        
        templates = {
            "treasure": [
                ("Ancient Cache", "Whispers speak of a pre-collapse data vault hidden in {location}. The coordinates are incomplete, but the rewards could be immense."),
                ("Salvage Opportunity", "A derelict freighter was spotted drifting near {location}. First to claim it gets the spoils."),
                ("Lost Artifact", "An archaeologist went missing searching for a Precursor artifact in {location}. Their notes might still be there.")
            ],
            "danger": [
                ("Pirate Activity", "Raiders have been spotted in {location}. Travel at your own risk."),
                ("Quarantine Zone", "A plague ship was last seen near {location}. The authorities have issued a warning."),
                ("Anomaly Detected", "Sensor readings from {location} are... wrong. Something's not right there.")
            ],
            "opportunity": [
                ("Hiring", "A merchant in {location} is looking for reliable crew. Good pay, dangerous work."),
                ("Trade Route", "New trade route opened to {location}. Early traders are making a fortune."),
                ("Research Grant", "The Science Guild is funding expeditions to {location}. They're paying well.")
            ],
            "mystery": [
                ("Disappearance", "Three ships vanished near {location} in the past month. No distress calls."),
                ("Strange Signal", "An encrypted signal is broadcasting from {location}. No one knows what it means."),
                ("Ghost Sighting", "Travelers report seeing phantom ships near {location}. Probably just stories... probably.")
            ]
        }
        
        title, desc_template = random.choice(templates[category])
        location = self._generate_location_name()
        
        self.rumor_counter += 1
        rumor_id = f"rumor_{self.rumor_counter:04d}"
        
        # Expiration: 3-7 days from now
        expires = datetime.now() + timedelta(days=random.randint(3, 7))
        
        rumor = Rumor(
            id=rumor_id,
            title=title,
            description=desc_template.format(location=location),
            source=source,
            reliability=random.uniform(0.3, 0.9),
            category=category,
            location_hint=location,
            expires_at=expires.isoformat()
        )
        
        self.rumors[rumor_id] = rumor
        return rumor
    
    def _generate_location_name(self) -> str:
        """Generate a location name."""
        locations = [
            "the Outer Rim", "Sector 7", "the Drift", "the Void", "the Expanse",
            "Station Theta", "the Derelict Fields", "the Nebula", "the Belt"
        ]
        return random.choice(locations)
    
    def investigate_rumor(self, rumor_id: str, success: bool = True) -> dict[str, Any]:
        """Mark a rumor as investigated and potentially verify it."""
        if rumor_id not in self.rumors:
            return {"success": False, "error": "Rumor not found"}
        
        rumor = self.rumors[rumor_id]
        rumor.investigated = True
        
        if success:
            # Verify based on reliability
            if random.random() < rumor.reliability:
                rumor.verified = True
                return {
                    "success": True,
                    "verified": True,
                    "message": f"The rumor about '{rumor.title}' was true!"
                }
            else:
                return {
                    "success": True,
                    "verified": False,
                    "message": f"The rumor about '{rumor.title}' was false or exaggerated."
                }
        
        return {"success": True, "verified": False, "message": "Investigation incomplete."}
    
    def get_active_rumors(self) -> list[dict]:
        """Get all non-expired, non-investigated rumors."""
        now = datetime.now()
        active = []
        
        for rumor in self.rumors.values():
            if rumor.investigated:
                continue
            
            if rumor.expires_at:
                expires = datetime.fromisoformat(rumor.expires_at)
                if expires < now:
                    continue
            
            active.append(rumor.to_dict())
        
        return active
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "rumors": {k: v.to_dict() for k, v in self.rumors.items()},
            "rumor_counter": self.rumor_counter
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RumorNetwork":
        network = cls()
        network.rumors = {k: Rumor.from_dict(v) for k, v in data.get("rumors", {}).items()}
        network.rumor_counter = data.get("rumor_counter", 0)
        return network
