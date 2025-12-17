"""
Faction, Environment, and Party Dynamics Systems

This module provides systems for simulating faction politics, environmental
conditions, economic pressures, and party/companion dynamics.

Key Systems:
1. Faction Dynamics - Political relationships, territories, influence
2. Dynamic Environment - Weather, hazards, atmospheric conditions
3. Economy System - Resources, trade, scarcity
4. Companion System - Party dynamics, companion arcs, loyalty
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Any
import random
from collections import defaultdict


# =============================================================================
# FACTION DYNAMICS SYSTEM
# =============================================================================

class FactionStance(Enum):
    """Relationship stance between factions."""
    ALLIED = "allied"           # Working together
    FRIENDLY = "friendly"       # Positive relations
    NEUTRAL = "neutral"         # No strong feelings
    SUSPICIOUS = "suspicious"   # Wary but not hostile
    HOSTILE = "hostile"         # Active opposition
    WAR = "war"                 # Open conflict


class FactionType(Enum):
    """Types of factions."""
    GOVERNMENT = "government"
    CORPORATION = "corporation"
    CRIMINAL = "criminal"
    RELIGIOUS = "religious"
    MILITARY = "military"
    REBEL = "rebel"
    GUILD = "guild"
    TRIBE = "tribe"


@dataclass
class Faction:
    """A faction in the game world."""
    faction_id: str
    name: str
    faction_type: FactionType
    description: str
    leader: str = ""
    headquarters: str = ""
    influence: float = 0.5  # 0.0 to 1.0
    resources: float = 0.5  # 0.0 to 1.0
    territories: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)  # What they care about
    goals: List[str] = field(default_factory=list)
    player_reputation: float = 0.0  # -1.0 to 1.0


@dataclass
class FactionDynamicsSystem:
    """
    Tracks political relationships and faction dynamics.
    
    Creates a living political world where factions interact,
    compete, and respond to player actions.
    """
    
    factions: Dict[str, Faction] = field(default_factory=dict)
    relationships: Dict[str, Dict[str, FactionStance]] = field(default_factory=dict)
    recent_events: List[Dict[str, str]] = field(default_factory=list)
    
    def add_faction(self, faction_id: str, name: str, faction_type: FactionType,
                     description: str, **kwargs) -> Faction:
        """Add a faction to the world."""
        faction = Faction(
            faction_id=faction_id,
            name=name,
            faction_type=faction_type,
            description=description,
            **kwargs
        )
        self.factions[faction_id] = faction
        self.relationships[faction_id] = {}
        return faction
    
    def set_relationship(self, faction_a: str, faction_b: str, stance: FactionStance):
        """Set the relationship between two factions."""
        if faction_a in self.relationships:
            self.relationships[faction_a][faction_b] = stance
        if faction_b in self.relationships:
            self.relationships[faction_b][faction_a] = stance
    
    def get_relationship(self, faction_a: str, faction_b: str) -> FactionStance:
        """Get relationship between factions."""
        if faction_a in self.relationships:
            return self.relationships[faction_a].get(faction_b, FactionStance.NEUTRAL)
        return FactionStance.NEUTRAL
    
    def modify_player_rep(self, faction_id: str, change: float):
        """Modify player reputation with a faction."""
        if faction_id in self.factions:
            self.factions[faction_id].player_reputation = max(-1.0, min(1.0,
                self.factions[faction_id].player_reputation + change))
    
    def get_faction_at_location(self, location: str) -> List[Faction]:
        """Get factions that control or operate at a location."""
        return [f for f in self.factions.values() if location in f.territories]
    
    def record_event(self, description: str, factions_involved: List[str]):
        """Record a political event."""
        self.recent_events.append({
            "description": description,
            "factions": factions_involved
        })
        if len(self.recent_events) > 10:
            self.recent_events = self.recent_events[-10:]
    
    def get_faction_guidance(self, location: str = "", 
                              active_npcs: List[str] = None) -> str:
        """Generate faction dynamics guidance."""
        
        # Factions at current location
        local_factions = self.get_faction_at_location(location) if location else []
        
        local_text = ""
        if local_factions:
            local_items = []
            for f in local_factions:
                rep = f.player_reputation
                rep_label = "enemy" if rep < -0.3 else "suspicious" if rep < 0 else \
                           "neutral" if rep < 0.3 else "friendly" if rep < 0.6 else "ally"
                local_items.append(f"  - {f.name} ({f.faction_type.value}): {rep_label} rep, {f.influence:.0%} influence")
            local_text = f"""
FACTIONS AT {location.upper()}:
{chr(10).join(local_items)}"""
        
        # Tensions and conflicts
        tensions = []
        for f1_id, rels in self.relationships.items():
            for f2_id, stance in rels.items():
                if stance in [FactionStance.HOSTILE, FactionStance.WAR]:
                    f1 = self.factions.get(f1_id, None)
                    f2 = self.factions.get(f2_id, None)
                    if f1 and f2:
                        tensions.append(f"  - {f1.name} vs {f2.name}: {stance.value}")
        
        tension_text = ""
        if tensions:
            tension_text = f"""
ACTIVE CONFLICTS:
{chr(10).join(tensions[:5])}"""
        
        return f"""<faction_dynamics>
POLITICAL LANDSCAPE:
{local_text}{tension_text}

FACTION INTERACTION PRINCIPLES:
  - Factions have goals beyond the player's story
  - Helping one faction may anger another
  - Political favors come with expectations
  - Power vacuums create opportunities and dangers
  
REPUTATION MECHANICS:
  - Actions speak louder than words
  - Word travels (factions share information)
  - Past allies remember past help
  - Enemies can become allies (and vice versa)
</faction_dynamics>"""
    
    def to_dict(self) -> dict:
        return {
            "factions": {
                fid: {
                    "faction_id": f.faction_id,
                    "name": f.name,
                    "faction_type": f.faction_type.value,
                    "description": f.description,
                    "leader": f.leader,
                    "headquarters": f.headquarters,
                    "influence": f.influence,
                    "resources": f.resources,
                    "territories": f.territories,
                    "values": f.values,
                    "goals": f.goals,
                    "player_reputation": f.player_reputation
                } for fid, f in self.factions.items()
            },
            "relationships": {
                f1: {f2: s.value for f2, s in rels.items()}
                for f1, rels in self.relationships.items()
            },
            "recent_events": self.recent_events
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FactionDynamicsSystem":
        system = cls()
        system.recent_events = data.get("recent_events", [])
        
        for fid, f in data.get("factions", {}).items():
            system.factions[fid] = Faction(
                faction_id=f["faction_id"],
                name=f["name"],
                faction_type=FactionType(f["faction_type"]),
                description=f["description"],
                leader=f.get("leader", ""),
                headquarters=f.get("headquarters", ""),
                influence=f.get("influence", 0.5),
                resources=f.get("resources", 0.5),
                territories=f.get("territories", []),
                values=f.get("values", []),
                goals=f.get("goals", []),
                player_reputation=f.get("player_reputation", 0.0)
            )
        
        for f1, rels in data.get("relationships", {}).items():
            system.relationships[f1] = {
                f2: FactionStance(s) for f2, s in rels.items()
            }
        
        return system


# =============================================================================
# DYNAMIC ENVIRONMENT SYSTEM
# =============================================================================

class WeatherType(Enum):
    """Types of weather."""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"
    FOG = "fog"
    DUST = "dust"
    VACUUM = "vacuum"  # Space
    RADIATION = "radiation"


class EnvironmentHazard(Enum):
    """Environmental hazards."""
    NONE = "none"
    EXTREME_COLD = "cold"
    EXTREME_HEAT = "heat"
    TOXIC_ATMOSPHERE = "toxic"
    LOW_GRAVITY = "low_gravity"
    HIGH_GRAVITY = "high_gravity"
    RADIATION_ZONE = "radiation"
    UNSTABLE_TERRAIN = "unstable"
    VISIBILITY_ZERO = "no_visibility"


@dataclass
class EnvironmentConditions:
    """Current environmental conditions."""
    weather: WeatherType
    hazards: List[EnvironmentHazard]
    temperature: str  # Descriptive
    visibility: str  # Descriptive
    atmosphere_notes: str
    duration_remaining: int  # Scenes until change


@dataclass
class DynamicEnvironmentSystem:
    """
    Tracks weather, hazards, and atmospheric conditions.
    
    Makes the environment feel alive and creates
    gameplay considerations beyond combat and dialogue.
    """
    
    current_conditions: Optional[EnvironmentConditions] = None
    location_defaults: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    condition_history: List[str] = field(default_factory=list)
    
    # Weather effects on narrative
    WEATHER_EFFECTS: Dict[WeatherType, Dict[str, str]] = field(default_factory=lambda: {
        WeatherType.CLEAR: {
            "visibility": "Excellent",
            "movement": "Normal",
            "mood": "Exposed, nowhere to hide, bright",
            "narrative": "The clarity feels almost harsh"
        },
        WeatherType.RAIN: {
            "visibility": "Reduced",
            "movement": "Slowed, slippery",
            "mood": "Melancholy, concealment, cleansing",
            "narrative": "Rain runs down surfaces, muffles sounds"
        },
        WeatherType.STORM: {
            "visibility": "Severely reduced",
            "movement": "Dangerous",
            "mood": "Chaos, danger, urgency",
            "narrative": "Lightning strobes, thunder masks other sounds"
        },
        WeatherType.FOG: {
            "visibility": "Near zero",
            "movement": "Cautious",
            "mood": "Mystery, isolation, dread",
            "narrative": "Shapes emerge from gray, sounds distort"
        },
        WeatherType.DUST: {
            "visibility": "Reduced",
            "movement": "Impaired",
            "mood": "Hostility, endurance, grit",
            "narrative": "Dust coats everything, breathing hurts"
        }
    })
    
    def set_conditions(self, weather: WeatherType, 
                        hazards: List[EnvironmentHazard] = None,
                        temperature: str = "moderate",
                        visibility: str = "normal",
                        atmosphere: str = "",
                        duration: int = 5):
        """Set current environmental conditions."""
        self.current_conditions = EnvironmentConditions(
            weather=weather,
            hazards=hazards or [],
            temperature=temperature,
            visibility=visibility,
            atmosphere_notes=atmosphere,
            duration_remaining=duration
        )
        self.condition_history.append(weather.value)
    
    def advance_time(self) -> bool:
        """Advance time and check if conditions should change."""
        if self.current_conditions:
            self.current_conditions.duration_remaining -= 1
            return self.current_conditions.duration_remaining <= 0
        return True
    
    def get_weather_effects(self) -> Dict[str, str]:
        """Get current weather effects."""
        if self.current_conditions:
            return self.WEATHER_EFFECTS.get(self.current_conditions.weather, {})
        return {}
    
    def get_environment_guidance(self, location: str = "") -> str:
        """Generate environment guidance for narrator."""
        
        if not self.current_conditions:
            return """<environment>
No environmental conditions set.
Consider establishing:
  - Weather that affects mood and options
  - Hazards that create tension
  - Sensory details that ground the scene
</environment>"""
        
        cond = self.current_conditions
        effects = self.get_weather_effects()
        
        hazard_text = ""
        if cond.hazards:
            hazard_items = [f"  ⚠️ {h.value.replace('_', ' ').title()}" for h in cond.hazards]
            hazard_text = f"""
ACTIVE HAZARDS:
{chr(10).join(hazard_items)}"""
        
        return f"""<environment>
CONDITIONS: {cond.weather.value.upper()} | Temp: {cond.temperature} | Vis: {cond.visibility}
Duration: {cond.duration_remaining} scenes until change
{hazard_text}

WEATHER EFFECTS:
  Visibility: {effects.get('visibility', 'Normal')}
  Movement: {effects.get('movement', 'Normal')}
  Mood: {effects.get('mood', 'Neutral')}
  
NARRATIVE HOOK: "{effects.get('narrative', 'The environment persists.')}"
{f"Additional: {cond.atmosphere_notes}" if cond.atmosphere_notes else ""}

ENVIRONMENT AS NARRATIVE TOOL:
  - Weather should affect options (can't snipe in fog)
  - Hazards create urgency (can't stay here forever)
  - Sensory details ground every scene
  - Environment can mirror or contrast emotional beats
</environment>"""
    
    def to_dict(self) -> dict:
        cond_dict = None
        if self.current_conditions:
            cond_dict = {
                "weather": self.current_conditions.weather.value,
                "hazards": [h.value for h in self.current_conditions.hazards],
                "temperature": self.current_conditions.temperature,
                "visibility": self.current_conditions.visibility,
                "atmosphere_notes": self.current_conditions.atmosphere_notes,
                "duration_remaining": self.current_conditions.duration_remaining
            }
        return {
            "current_conditions": cond_dict,
            "location_defaults": self.location_defaults,
            "condition_history": self.condition_history[-10:]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DynamicEnvironmentSystem":
        system = cls()
        system.location_defaults = data.get("location_defaults", {})
        system.condition_history = data.get("condition_history", [])
        
        cond = data.get("current_conditions")
        if cond:
            system.current_conditions = EnvironmentConditions(
                weather=WeatherType(cond["weather"]),
                hazards=[EnvironmentHazard(h) for h in cond.get("hazards", [])],
                temperature=cond.get("temperature", "moderate"),
                visibility=cond.get("visibility", "normal"),
                atmosphere_notes=cond.get("atmosphere_notes", ""),
                duration_remaining=cond.get("duration_remaining", 5)
            )
        return system


# =============================================================================
# ECONOMY SYSTEM
# =============================================================================

class ResourceType(Enum):
    """Types of resources."""
    CURRENCY = "currency"
    SUPPLIES = "supplies"
    FUEL = "fuel"
    AMMUNITION = "ammunition"
    MEDICAL = "medical"
    EQUIPMENT = "equipment"
    INFORMATION = "information"
    INFLUENCE = "influence"


@dataclass
class Resource:
    """A tracked resource."""
    resource_type: ResourceType
    current: float
    maximum: float
    consumption_rate: float = 0.0  # Per scene
    scarcity_local: float = 0.5  # 0.0 abundant to 1.0 rare


@dataclass
class EconomySystem:
    """
    Tracks resources, trade, and economic pressure.
    
    Creates meaningful resource management and
    economic considerations in narrative.
    """
    
    resources: Dict[ResourceType, Resource] = field(default_factory=dict)
    trade_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    price_modifiers: Dict[str, float] = field(default_factory=dict)
    
    def set_resource(self, resource_type: ResourceType, current: float, 
                      maximum: float, consumption: float = 0.0,
                      scarcity: float = 0.5):
        """Set a resource level."""
        self.resources[resource_type] = Resource(
            resource_type=resource_type,
            current=current,
            maximum=maximum,
            consumption_rate=consumption,
            scarcity_local=scarcity
        )
    
    def modify_resource(self, resource_type: ResourceType, change: float) -> bool:
        """Modify a resource. Returns False if insufficient."""
        if resource_type in self.resources:
            r = self.resources[resource_type]
            new_value = r.current + change
            if new_value < 0:
                return False
            r.current = min(r.maximum, max(0, new_value))
            return True
        return False
    
    def consume_resources(self):
        """Consume resources based on consumption rates."""
        for r in self.resources.values():
            if r.consumption_rate > 0:
                r.current = max(0, r.current - r.consumption_rate)
    
    def get_critical_resources(self) -> List[Resource]:
        """Get resources at critical levels (<20%)."""
        return [r for r in self.resources.values() 
                if r.current / r.maximum < 0.2]
    
    def add_trade_opportunity(self, description: str, resource_type: ResourceType,
                                price: float, location: str = ""):
        """Add a trade opportunity."""
        self.trade_opportunities.append({
            "description": description,
            "resource": resource_type.value,
            "price": price,
            "location": location
        })
    
    def get_economy_guidance(self) -> str:
        """Generate economy guidance for narrator."""
        
        # Resource status
        resource_items = []
        for r in self.resources.values():
            percent = r.current / r.maximum if r.maximum > 0 else 0
            status = "🔴 CRITICAL" if percent < 0.2 else "🟡 Low" if percent < 0.5 else "🟢 OK"
            resource_items.append(f"  {r.resource_type.value}: {r.current:.0f}/{r.maximum:.0f} {status}")
        
        resource_text = "\n".join(resource_items) if resource_items else "  No resources tracked"
        
        # Critical warnings
        critical = self.get_critical_resources()
        critical_text = ""
        if critical:
            critical_items = [f"  ⚠️ {r.resource_type.value}: Only {r.current:.0f} remaining!" 
                             for r in critical]
            critical_text = f"""
CRITICAL SHORTAGES:
{chr(10).join(critical_items)}"""
        
        # Trade opportunities
        trade_text = ""
        if self.trade_opportunities:
            trade_items = [f"  - {t['description']}" for t in self.trade_opportunities[:3]]
            trade_text = f"""
TRADE OPPORTUNITIES:
{chr(10).join(trade_items)}"""
        
        return f"""<economy>
RESOURCE STATUS:
{resource_text}
{critical_text}{trade_text}

ECONOMIC PRESSURE:
  - Running low creates urgency and difficult choices
  - Scarcity reveals character (who shares? who hoards?)
  - Trade requires trust or leverage
  - Every expedition costs something

NARRATIVE USES:
  - "We don't have enough fuel to make it back"
  - "Someone's been taking more than their share"
  - "They have what we need, but at what price?"
</economy>"""
    
    def to_dict(self) -> dict:
        return {
            "resources": {
                r.resource_type.value: {
                    "resource_type": r.resource_type.value,
                    "current": r.current,
                    "maximum": r.maximum,
                    "consumption_rate": r.consumption_rate,
                    "scarcity_local": r.scarcity_local
                } for r in self.resources.values()
            },
            "trade_opportunities": self.trade_opportunities,
            "price_modifiers": self.price_modifiers
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EconomySystem":
        system = cls()
        system.trade_opportunities = data.get("trade_opportunities", [])
        system.price_modifiers = data.get("price_modifiers", {})
        
        for r in data.get("resources", {}).values():
            system.resources[ResourceType(r["resource_type"])] = Resource(
                resource_type=ResourceType(r["resource_type"]),
                current=r["current"],
                maximum=r["maximum"],
                consumption_rate=r.get("consumption_rate", 0.0),
                scarcity_local=r.get("scarcity_local", 0.5)
            )
        return system


# =============================================================================
# COMPANION/PARTY SYSTEM
# =============================================================================

class CompanionMood(Enum):
    """Companion emotional states."""
    CONTENT = "content"
    WORRIED = "worried"
    ANGRY = "angry"
    SAD = "sad"
    HOPEFUL = "hopeful"
    CONFLICTED = "conflicted"
    DETERMINED = "determined"
    EXHAUSTED = "exhausted"


class LoyaltyLevel(Enum):
    """Loyalty levels."""
    WAVERING = "wavering"
    UNCERTAIN = "uncertain"
    COMMITTED = "committed"
    DEVOTED = "devoted"
    UNSHAKEABLE = "unshakeable"


@dataclass
class Companion:
    """A party member/companion."""
    name: str
    role: str  # What they bring to the party
    loyalty: float = 0.5  # 0.0 to 1.0
    mood: CompanionMood = CompanionMood.CONTENT
    personal_goal: str = ""
    fear: str = ""
    approval_history: List[Dict[str, Any]] = field(default_factory=list)
    scenes_since_spotlight: int = 0
    arc_stage: str = "introduction"  # Companion's personal arc


@dataclass
class CompanionSystem:
    """
    Tracks party dynamics and companion arcs.
    
    Ensures companions feel like real characters
    with their own stories, not just followers.
    """
    
    companions: Dict[str, Companion] = field(default_factory=dict)
    party_morale: float = 0.7  # 0.0 to 1.0
    party_cohesion: float = 0.5  # How well they work together
    internal_conflicts: List[Dict[str, str]] = field(default_factory=list)
    
    def add_companion(self, name: str, role: str, personal_goal: str = "",
                       fear: str = "", initial_loyalty: float = 0.5) -> Companion:
        """Add a companion to the party."""
        companion = Companion(
            name=name,
            role=role,
            loyalty=initial_loyalty,
            personal_goal=personal_goal,
            fear=fear
        )
        self.companions[name] = companion
        return companion
    
    def modify_loyalty(self, name: str, change: float, reason: str = ""):
        """Modify companion loyalty."""
        if name in self.companions:
            comp = self.companions[name]
            old = comp.loyalty
            comp.loyalty = max(0.0, min(1.0, comp.loyalty + change))
            
            if abs(change) >= 0.1:  # Significant change
                comp.approval_history.append({
                    "change": change,
                    "reason": reason,
                    "old": old,
                    "new": comp.loyalty
                })
    
    def set_mood(self, name: str, mood: CompanionMood):
        """Set companion mood."""
        if name in self.companions:
            self.companions[name].mood = mood
    
    def get_loyalty_level(self, loyalty: float) -> LoyaltyLevel:
        """Convert loyalty float to level."""
        if loyalty < 0.2:
            return LoyaltyLevel.WAVERING
        elif loyalty < 0.4:
            return LoyaltyLevel.UNCERTAIN
        elif loyalty < 0.6:
            return LoyaltyLevel.COMMITTED
        elif loyalty < 0.8:
            return LoyaltyLevel.DEVOTED
        else:
            return LoyaltyLevel.UNSHAKEABLE
    
    def get_neglected_companions(self, threshold: int = 5) -> List[Companion]:
        """Get companions who haven't had spotlight recently."""
        return [c for c in self.companions.values() 
                if c.scenes_since_spotlight >= threshold]
    
    def add_conflict(self, party_member_a: str, party_member_b: str, reason: str):
        """Add internal party conflict."""
        self.internal_conflicts.append({
            "members": [party_member_a, party_member_b],
            "reason": reason
        })
    
    def advance_scene(self, spotlight_name: str = ""):
        """Advance scene and track spotlight."""
        for comp in self.companions.values():
            comp.scenes_since_spotlight += 1
        
        if spotlight_name and spotlight_name in self.companions:
            self.companions[spotlight_name].scenes_since_spotlight = 0
    
    def get_companion_guidance(self) -> str:
        """Generate companion system guidance."""
        
        # Party status
        companion_items = []
        for comp in self.companions.values():
            loyalty_level = self.get_loyalty_level(comp.loyalty)
            companion_items.append(
                f"  {comp.name} ({comp.role}): {comp.mood.value}, {loyalty_level.value} loyalty"
            )
        
        companion_text = "\n".join(companion_items) if companion_items else "  No companions"
        
        # Neglected companions
        neglected = self.get_neglected_companions()
        neglected_text = ""
        if neglected:
            neglected_items = [f"  📢 {c.name}: {c.scenes_since_spotlight} scenes without spotlight" 
                             for c in neglected[:3]]
            neglected_text = f"""
NEED ATTENTION:
{chr(10).join(neglected_items)}"""
        
        # Internal conflicts
        conflict_text = ""
        if self.internal_conflicts:
            conflict_items = [f"  ⚡ {c['members'][0]} vs {c['members'][1]}: {c['reason']}" 
                             for c in self.internal_conflicts[-2:]]
            conflict_text = f"""
INTERNAL TENSIONS:
{chr(10).join(conflict_items)}"""
        
        return f"""<companions>
PARTY STATUS: Morale {self.party_morale:.0%} | Cohesion {self.party_cohesion:.0%}

COMPANIONS:
{companion_text}
{neglected_text}{conflict_text}

COMPANION STORYTELLING:
  - Each companion has their own arc beyond the main story
  - Loyalty is earned through respect for their values
  - Personal goals should sometimes conflict with mission
  - Neglected companions become resentful or withdrawn

PARTY DYNAMICS:
  - Companions react to each other, not just player
  - Decisions should sometimes divide the party
  - Shared hardship builds bonds
  - "What would X think of this?" matters
</companions>"""
    
    def to_dict(self) -> dict:
        return {
            "companions": {
                name: {
                    "name": c.name,
                    "role": c.role,
                    "loyalty": c.loyalty,
                    "mood": c.mood.value,
                    "personal_goal": c.personal_goal,
                    "fear": c.fear,
                    "approval_history": c.approval_history[-10:],
                    "scenes_since_spotlight": c.scenes_since_spotlight,
                    "arc_stage": c.arc_stage
                } for name, c in self.companions.items()
            },
            "party_morale": self.party_morale,
            "party_cohesion": self.party_cohesion,
            "internal_conflicts": self.internal_conflicts[-5:]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CompanionSystem":
        system = cls()
        system.party_morale = data.get("party_morale", 0.7)
        system.party_cohesion = data.get("party_cohesion", 0.5)
        system.internal_conflicts = data.get("internal_conflicts", [])
        
        for name, c in data.get("companions", {}).items():
            system.companions[name] = Companion(
                name=c["name"],
                role=c["role"],
                loyalty=c.get("loyalty", 0.5),
                mood=CompanionMood(c.get("mood", "content")),
                personal_goal=c.get("personal_goal", ""),
                fear=c.get("fear", ""),
                approval_history=c.get("approval_history", []),
                scenes_since_spotlight=c.get("scenes_since_spotlight", 0),
                arc_stage=c.get("arc_stage", "introduction")
            )
        return system


# =============================================================================
# MASTER FACTION AND ENVIRONMENT ENGINE
# =============================================================================

@dataclass
class FactionEnvironmentEngine:
    """Master engine for faction, environment, economy, and party systems."""
    
    factions: FactionDynamicsSystem = field(default_factory=FactionDynamicsSystem)
    environment: DynamicEnvironmentSystem = field(default_factory=DynamicEnvironmentSystem)
    economy: EconomySystem = field(default_factory=EconomySystem)
    companions: CompanionSystem = field(default_factory=CompanionSystem)
    
    def get_comprehensive_guidance(
        self,
        location: str = "",
        active_npcs: List[str] = None
    ) -> str:
        """Generate comprehensive guidance from all systems."""
        
        sections = []
        
        # Factions
        faction_guidance = self.factions.get_faction_guidance(location, active_npcs)
        if faction_guidance:
            sections.append(faction_guidance)
        
        # Environment
        env_guidance = self.environment.get_environment_guidance(location)
        if env_guidance:
            sections.append(env_guidance)
        
        # Economy
        econ_guidance = self.economy.get_economy_guidance()
        if econ_guidance:
            sections.append(econ_guidance)
        
        # Companions
        comp_guidance = self.companions.get_companion_guidance()
        if comp_guidance:
            sections.append(comp_guidance)
        
        if not sections:
            return ""
        
        return f"""
<faction_environment_systems>
=== FACTION, ENVIRONMENT & PARTY GUIDANCE ===
{chr(10).join(sections)}
</faction_environment_systems>
"""
    
    def to_dict(self) -> dict:
        return {
            "factions": self.factions.to_dict(),
            "environment": self.environment.to_dict(),
            "economy": self.economy.to_dict(),
            "companions": self.companions.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FactionEnvironmentEngine":
        engine = cls()
        if "factions" in data:
            engine.factions = FactionDynamicsSystem.from_dict(data["factions"])
        if "environment" in data:
            engine.environment = DynamicEnvironmentSystem.from_dict(data["environment"])
        if "economy" in data:
            engine.economy = EconomySystem.from_dict(data["economy"])
        if "companions" in data:
            engine.companions = CompanionSystem.from_dict(data["companions"])
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FACTION & ENVIRONMENT ENGINE - TEST")
    print("=" * 60)
    
    engine = FactionEnvironmentEngine()
    
    # Add factions
    engine.factions.add_faction(
        "consortium", "Merchant Consortium", FactionType.CORPORATION,
        "Powerful trading conglomerate",
        territories=["Station Omega", "Trade Hub Beta"],
        influence=0.8
    )
    engine.factions.add_faction(
        "rebels", "Free Frontier", FactionType.REBEL,
        "Anti-corporate freedom fighters",
        territories=["Outer Rim"],
        influence=0.3
    )
    engine.factions.set_relationship("consortium", "rebels", FactionStance.HOSTILE)
    
    # Set environment
    engine.environment.set_conditions(
        WeatherType.STORM,
        hazards=[EnvironmentHazard.LOW_GRAVITY],
        temperature="cold",
        visibility="poor",
        atmosphere="The storm makes everything harder"
    )
    
    # Set economy
    engine.economy.set_resource(ResourceType.FUEL, 30, 100, consumption=5)
    engine.economy.set_resource(ResourceType.SUPPLIES, 15, 50, consumption=2)
    
    # Add companion
    engine.companions.add_companion(
        "Torres", "Pilot",
        personal_goal="Find her missing brother",
        fear="Losing another crewmate",
        initial_loyalty=0.6
    )
    
    print("\n--- COMPREHENSIVE GUIDANCE ---")
    guidance = engine.get_comprehensive_guidance(
        location="Station Omega",
        active_npcs=["Torres"]
    )
    print(guidance[:3000] + "..." if len(guidance) > 3000 else guidance)
