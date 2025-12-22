"""
Law Enforcement System - Suspicion, investigation, pursuit, escalation.
Manages faction security responses to player crimes and suspicious behavior.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import time


class EscalationLevel(Enum):
    """Law enforcement escalation levels."""
    NONE = "none"
    WARNING = "warning"
    FINE = "fine"
    ARREST = "arrest"
    LETHAL = "lethal"


@dataclass
class Crime:
    """Record of a crime committed."""
    crime_id: str
    crime_type: str  # theft, assault, murder, smuggling, treason
    severity: int  # 1-5
    faction_witnessed: List[str]
    location: str
    timestamp: float
    witnesses: List[str]  # NPC IDs


@dataclass
class Investigation:
    """Active investigation of player."""
    investigation_id: str
    faction: str
    suspicion_level: float
    start_time: float
    duration: float
    location: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class Pursuit:
    """Active pursuit of player."""
    pursuit_id: str
    faction: str
    ship_count: int
    start_time: float
    duration_remaining: float
    escalation_level: EscalationLevel
    blockade_active: bool = False


@dataclass
class Bounty:
    """Bounty on player."""
    faction: str
    amount: int
    crimes: List[str]  # Crime IDs
    posted_time: float


@dataclass
class WitnessReport:
    """Witness report of a crime."""
    witness_id: str
    crime_id: str
    faction_reported_to: str
    timestamp: float
    reliability: float  # 0.0-1.0


class LawSystem:
    """Manages law enforcement and crime tracking."""
    
    def __init__(self, config):
        self.config = config
        self.player_suspicion: Dict[str, float] = {}  # faction -> suspicion
        self.active_investigations: List[Investigation] = []
        self.active_pursuits: List[Pursuit] = []
        self.bounties: Dict[str, Bounty] = {}  # faction -> bounty
        self.witness_reports: List[WitnessReport] = []
        self.alert_decay_timers: Dict[str, float] = {}  # faction -> time
        self.crime_history: List[Crime] = []
        self._crime_counter = 0
        self._investigation_counter = 0
        self._pursuit_counter = 0
    
    def tick(self, delta_time: float, player_state: Dict) -> List[Dict]:
        """
        Update law enforcement simulation.
        
        Args:
            delta_time: Time elapsed in hours
            player_state: Player's current state (crimes, posture, etc.)
            
        Returns:
            List of law enforcement events
        """
        events = []
        
        # Decay suspicion for all factions
        for faction in list(self.player_suspicion.keys()):
            self.player_suspicion[faction] -= self.config.suspicion_decay_rate * delta_time
            if self.player_suspicion[faction] <= 0:
                del self.player_suspicion[faction]
                events.append({
                    "type": "suspicion_cleared",
                    "faction": faction
                })
        
        # Update investigations
        for investigation in list(self.active_investigations):
            investigation.duration -= delta_time
            
            if investigation.duration <= 0:
                # Investigation complete
                self.active_investigations.remove(investigation)
                
                if investigation.suspicion_level >= self.config.suspicion_threshold_pursuit:
                    # Escalate to pursuit
                    pursuit = self._start_pursuit(investigation.faction, investigation.suspicion_level)
                    events.append({
                        "type": "pursuit_initiated",
                        "faction": investigation.faction,
                        "pursuit_id": pursuit.pursuit_id
                    })
                else:
                    events.append({
                        "type": "investigation_concluded",
                        "faction": investigation.faction,
                        "result": "insufficient_evidence"
                    })
        
        # Update pursuits
        for pursuit in list(self.active_pursuits):
            pursuit.duration_remaining -= delta_time
            
            if pursuit.duration_remaining <= 0:
                # Pursuit abandoned
                self.active_pursuits.remove(pursuit)
                events.append({
                    "type": "pursuit_abandoned",
                    "faction": pursuit.faction
                })
            else:
                # Check for escalation
                suspicion = self.player_suspicion.get(pursuit.faction, 0.0)
                if suspicion >= self.config.suspicion_threshold_lethal and pursuit.escalation_level != EscalationLevel.LETHAL:
                    pursuit.escalation_level = EscalationLevel.LETHAL
                    events.append({
                        "type": "pursuit_escalated",
                        "faction": pursuit.faction,
                        "new_level": "lethal"
                    })
                
                # Check for blockade
                if suspicion >= self.config.blockade_threshold and not pursuit.blockade_active:
                    pursuit.blockade_active = True
                    events.append({
                        "type": "blockade_initiated",
                        "faction": pursuit.faction
                    })
        
        # Decay bounties
        for faction, bounty in list(self.bounties.items()):
            bounty.amount -= int(self.config.bounty_decay_rate * bounty.amount * delta_time)
            if bounty.amount <= 0:
                del self.bounties[faction]
                events.append({
                    "type": "bounty_expired",
                    "faction": faction
                })
        
        # Check for new investigations based on suspicion
        for faction, suspicion in self.player_suspicion.items():
            if suspicion >= self.config.suspicion_threshold_investigation:
                # Check if already investigating
                if not any(inv.faction == faction for inv in self.active_investigations):
                    investigation = self._start_investigation(faction, suspicion)
                    events.append({
                        "type": "investigation_started",
                        "faction": faction,
                        "investigation_id": investigation.investigation_id
                    })
        
        return events
    
    def report_crime(self, crime_type: str, severity: int, location: str, 
                     witnesses: List[str], factions: List[str]) -> Crime:
        """
        Report a crime committed by the player.
        
        Args:
            crime_type: Type of crime
            severity: Severity (1-5)
            location: Where it occurred
            witnesses: List of NPC witness IDs
            factions: Factions that have jurisdiction
            
        Returns:
            Crime record
        """
        self._crime_counter += 1
        crime = Crime(
            crime_id=f"crime_{self._crime_counter}",
            crime_type=crime_type,
            severity=severity,
            faction_witnessed=factions,
            location=location,
            timestamp=time.time(),
            witnesses=witnesses
        )
        
        self.crime_history.append(crime)
        
        # Add suspicion to relevant factions
        multiplier = self.config.crime_severity_multipliers.get(crime_type, 0.5)
        suspicion_increase = severity * multiplier * 0.2  # Scale to 0.0-1.0
        
        for faction in factions:
            current = self.player_suspicion.get(faction, 0.0)
            self.player_suspicion[faction] = min(1.0, current + suspicion_increase)
        
        # Process witness reports
        for witness_id in witnesses:
            if random.random() < self.config.witness_report_chance:
                for faction in factions:
                    report = WitnessReport(
                        witness_id=witness_id,
                        crime_id=crime.crime_id,
                        faction_reported_to=faction,
                        timestamp=time.time(),
                        reliability=random.uniform(0.6, 1.0)
                    )
                    self.witness_reports.append(report)
        
        # Post bounty if severe enough
        if severity >= 4:
            for faction in factions:
                self._post_bounty(faction, [crime.crime_id])
        
        return crime
    
    def _start_investigation(self, faction: str, suspicion: float) -> Investigation:
        """Start an investigation."""
        self._investigation_counter += 1
        investigation = Investigation(
            investigation_id=f"inv_{self._investigation_counter}",
            faction=faction,
            suspicion_level=suspicion,
            start_time=time.time(),
            duration=self.config.investigation_duration,
            location="current"
        )
        self.active_investigations.append(investigation)
        return investigation
    
    def _start_pursuit(self, faction: str, suspicion: float) -> Pursuit:
        """Start a pursuit."""
        self._pursuit_counter += 1
        
        # Determine escalation level based on suspicion
        if suspicion >= self.config.suspicion_threshold_lethal:
            escalation = EscalationLevel.LETHAL
        elif suspicion >= self.config.suspicion_threshold_pursuit:
            escalation = EscalationLevel.ARREST
        else:
            escalation = EscalationLevel.WARNING
        
        pursuit = Pursuit(
            pursuit_id=f"pursuit_{self._pursuit_counter}",
            faction=faction,
            ship_count=int(suspicion * 5) + 1,  # 1-5 ships
            start_time=time.time(),
            duration_remaining=self.config.pursuit_duration_max,
            escalation_level=escalation
        )
        self.active_pursuits.append(pursuit)
        return pursuit
    
    def _post_bounty(self, faction: str, crime_ids: List[str]):
        """Post a bounty on the player."""
        total_severity = sum(
            crime.severity for crime in self.crime_history 
            if crime.crime_id in crime_ids
        )
        
        amount = self.config.bounty_base_amount + (total_severity * self.config.bounty_multiplier_per_severity)
        
        if faction in self.bounties:
            # Add to existing bounty
            self.bounties[faction].amount += amount
            self.bounties[faction].crimes.extend(crime_ids)
        else:
            self.bounties[faction] = Bounty(
                faction=faction,
                amount=amount,
                crimes=crime_ids,
                posted_time=time.time()
            )
    
    def clear_suspicion(self, faction: str, amount: float = 1.0):
        """Clear suspicion for a faction (e.g., via bribe or disguise)."""
        if faction in self.player_suspicion:
            self.player_suspicion[faction] = max(0.0, self.player_suspicion[faction] - amount)
            if self.player_suspicion[faction] == 0:
                del self.player_suspicion[faction]
    
    def get_suspicion(self, faction: str) -> float:
        """Get current suspicion level for a faction."""
        return self.player_suspicion.get(faction, 0.0)
    
    def get_total_bounty(self) -> int:
        """Get total bounty across all factions."""
        return sum(bounty.amount for bounty in self.bounties.values())
    
    def is_wanted(self) -> bool:
        """Check if player has any active bounties."""
        return len(self.bounties) > 0
    
    def to_dict(self) -> Dict:
        """Serialize state."""
        return {
            "player_suspicion": self.player_suspicion,
            "bounties": {
                faction: {
                    "amount": bounty.amount,
                    "crimes": bounty.crimes,
                    "posted_time": bounty.posted_time
                }
                for faction, bounty in self.bounties.items()
            },
            "crime_counter": self._crime_counter,
            "investigation_counter": self._investigation_counter,
            "pursuit_counter": self._pursuit_counter
        }
    
    @classmethod
    def from_dict(cls, data: Dict, config) -> LawSystem:
        """Deserialize state."""
        system = cls(config)
        system.player_suspicion = data.get("player_suspicion", {})
        system._crime_counter = data.get("crime_counter", 0)
        system._investigation_counter = data.get("investigation_counter", 0)
        system._pursuit_counter = data.get("pursuit_counter", 0)
        
        # Restore bounties
        for faction, bounty_data in data.get("bounties", {}).items():
            system.bounties[faction] = Bounty(
                faction=faction,
                amount=bounty_data["amount"],
                crimes=bounty_data["crimes"],
                posted_time=bounty_data["posted_time"]
            )
        
        return system


# Need to import random
import random
