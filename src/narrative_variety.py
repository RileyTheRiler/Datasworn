"""
Narrative Variety System - POV Shifts, Document Inserts, Flashbacks

Adds variety to narrative presentation through different perspectives,
document formats, and temporal shifts.

Key Systems:
1. POV Shift - Perspective changes to other characters
2. Document Insert - Logs, messages, reports
3. Flashback Trigger - Memory-based temporal shifts
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class POVType(Enum):
    """Types of point-of-view."""
    PLAYER = "player"  # Standard second-person
    NPC_FIRST = "npc_first"  # First-person from NPC
    NPC_THIRD = "npc_third"  # Third-person limited (NPC)
    OMNISCIENT = "omniscient"  # Third-person omniscient
    COLLECTIVE = "collective"  # "We" perspective


class DocumentType(Enum):
    """Types of document inserts."""
    SHIP_LOG = "ship_log"
    PERSONAL_LOG = "personal_log"
    INTERCEPTED_MESSAGE = "intercepted_message"
    MEDICAL_REPORT = "medical_report"
    MISSION_BRIEFING = "mission_briefing"
    SECURITY_ALERT = "security_alert"
    SYSTEM_DIAGNOSTIC = "system_diagnostic"
    FOUND_NOTE = "found_note"


class FlashbackTrigger(Enum):
    """What triggers a flashback."""
    LOCATION = "location"  # Returning to a place
    OBJECT = "object"  # Seeing/touching an item
    PERSON = "person"  # Encountering someone
    SENSORY = "sensory"  # Smell, sound, etc.
    STRESS = "stress"  # Psychological state
    DREAM = "dream"  # During rest


@dataclass
class POVShift:
    """A perspective shift to another character."""
    shift_id: str
    target_character: str
    pov_type: POVType
    scene: int
    
    # Content
    purpose: str  # Why this shift? (reveal info, build tension, etc.)
    duration: str = "brief"  # "brief", "scene", "extended"
    
    def to_dict(self) -> dict:
        return {
            "shift_id": self.shift_id,
            "target_character": self.target_character,
            "pov_type": self.pov_type.value,
            "scene": self.scene,
            "purpose": self.purpose,
            "duration": self.duration,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "POVShift":
        return cls(
            shift_id=data["shift_id"],
            target_character=data["target_character"],
            pov_type=POVType(data["pov_type"]),
            scene=data["scene"],
            purpose=data["purpose"],
            duration=data.get("duration", "brief"),
        )


@dataclass
class DocumentInsert:
    """A document presented to the player."""
    document_id: str
    document_type: DocumentType
    title: str
    content: str
    scene: int
    
    # Metadata
    author: Optional[str] = None
    timestamp: Optional[str] = None
    classification: str = "UNCLASSIFIED"
    
    # Narrative purpose
    reveals: List[str] = field(default_factory=list)  # What info does this reveal?
    
    def format_document(self) -> str:
        """Format the document for display."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"[{self.document_type.value.upper().replace('_', ' ')}]")
        if self.classification != "UNCLASSIFIED":
            lines.append(f"CLASSIFICATION: {self.classification}")
        lines.append(f"TITLE: {self.title}")
        if self.author:
            lines.append(f"AUTHOR: {self.author}")
        if self.timestamp:
            lines.append(f"TIMESTAMP: {self.timestamp}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(self.content)
        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "document_type": self.document_type.value,
            "title": self.title,
            "content": self.content,
            "scene": self.scene,
            "author": self.author,
            "timestamp": self.timestamp,
            "classification": self.classification,
            "reveals": self.reveals,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DocumentInsert":
        return cls(
            document_id=data["document_id"],
            document_type=DocumentType(data["document_type"]),
            title=data["title"],
            content=data["content"],
            scene=data["scene"],
            author=data.get("author"),
            timestamp=data.get("timestamp"),
            classification=data.get("classification", "UNCLASSIFIED"),
            reveals=data.get("reveals", []),
        )


@dataclass
class Flashback:
    """A temporal shift to a past event."""
    flashback_id: str
    trigger: FlashbackTrigger
    trigger_description: str
    
    # Temporal info
    current_scene: int
    flashback_to_scene: int  # Which past scene (or -1 for pre-game)
    time_description: str  # "Three years ago", "Last week", etc.
    
    # Content
    memory_description: str
    emotional_tone: str  # "nostalgic", "traumatic", "bittersweet", etc.
    reveals: List[str] = field(default_factory=list)
    
    # Control
    is_reliable: bool = True  # False for unreliable/distorted memories
    
    def to_dict(self) -> dict:
        return {
            "flashback_id": self.flashback_id,
            "trigger": self.trigger.value,
            "trigger_description": self.trigger_description,
            "current_scene": self.current_scene,
            "flashback_to_scene": self.flashback_to_scene,
            "time_description": self.time_description,
            "memory_description": self.memory_description,
            "emotional_tone": self.emotional_tone,
            "reveals": self.reveals,
            "is_reliable": self.is_reliable,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Flashback":
        return cls(
            flashback_id=data["flashback_id"],
            trigger=FlashbackTrigger(data["trigger"]),
            trigger_description=data["trigger_description"],
            current_scene=data["current_scene"],
            flashback_to_scene=data["flashback_to_scene"],
            time_description=data["time_description"],
            memory_description=data["memory_description"],
            emotional_tone=data["emotional_tone"],
            reveals=data.get("reveals", []),
            is_reliable=data.get("is_reliable", True),
        )


@dataclass
class NarrativeVariety:
    """Master system for narrative variety."""
    
    pov_shifts: List[POVShift] = field(default_factory=list)
    documents: List[DocumentInsert] = field(default_factory=list)
    flashbacks: List[Flashback] = field(default_factory=list)
    
    current_scene: int = 0
    _shift_counter: int = 0
    _document_counter: int = 0
    _flashback_counter: int = 0
    
    # Usage tracking
    last_pov_shift: int = -10
    last_document: int = -10
    last_flashback: int = -10
    
    def add_pov_shift(
        self,
        target_character: str,
        pov_type: POVType,
        purpose: str,
        duration: str = "brief",
    ) -> str:
        """Add a POV shift."""
        self._shift_counter += 1
        shift_id = f"pov_{self._shift_counter:03d}"
        
        shift = POVShift(
            shift_id=shift_id,
            target_character=target_character,
            pov_type=pov_type,
            scene=self.current_scene,
            purpose=purpose,
            duration=duration,
        )
        
        self.pov_shifts.append(shift)
        self.last_pov_shift = self.current_scene
        return shift_id
    
    def add_document(
        self,
        document_type: DocumentType,
        title: str,
        content: str,
        author: Optional[str] = None,
        reveals: List[str] = None,
    ) -> str:
        """Add a document insert."""
        self._document_counter += 1
        document_id = f"doc_{self._document_counter:03d}"
        
        document = DocumentInsert(
            document_id=document_id,
            document_type=document_type,
            title=title,
            content=content,
            scene=self.current_scene,
            author=author,
            reveals=reveals or [],
        )
        
        self.documents.append(document)
        self.last_document = self.current_scene
        return document_id
    
    def add_flashback(
        self,
        trigger: FlashbackTrigger,
        trigger_description: str,
        time_description: str,
        memory_description: str,
        emotional_tone: str = "nostalgic",
        is_reliable: bool = True,
    ) -> str:
        """Add a flashback."""
        self._flashback_counter += 1
        flashback_id = f"flashback_{self._flashback_counter:03d}"
        
        flashback = Flashback(
            flashback_id=flashback_id,
            trigger=trigger,
            trigger_description=trigger_description,
            current_scene=self.current_scene,
            flashback_to_scene=-1,  # Pre-game by default
            time_description=time_description,
            memory_description=memory_description,
            emotional_tone=emotional_tone,
            is_reliable=is_reliable,
        )
        
        self.flashbacks.append(flashback)
        self.last_flashback = self.current_scene
        return flashback_id
    
    def should_vary_narrative(self) -> Dict[str, bool]:
        """Check if narrative variety is due."""
        scenes_since_pov = self.current_scene - self.last_pov_shift
        scenes_since_doc = self.current_scene - self.last_document
        scenes_since_flashback = self.current_scene - self.last_flashback
        
        return {
            "pov_shift": scenes_since_pov >= 8,  # Every 8 scenes
            "document": scenes_since_doc >= 5,  # Every 5 scenes
            "flashback": scenes_since_flashback >= 10,  # Every 10 scenes
        }
    
    def get_narrator_guidance(self) -> str:
        """Generate variety guidance for narrator."""
        sections = []
        variety_due = self.should_vary_narrative()
        
        if any(variety_due.values()):
            sections.append("<narrative_variety>")
            sections.append("CONSIDER VARYING NARRATIVE PRESENTATION:")
            
            if variety_due["pov_shift"]:
                sections.append("  - POV SHIFT: Brief interlude from another character's perspective")
                sections.append("    Purpose: Reveal hidden information or build tension")
            
            if variety_due["document"]:
                sections.append("  - DOCUMENT INSERT: Ship log, message, or report")
                sections.append("    Purpose: Worldbuilding or information delivery")
            
            if variety_due["flashback"]:
                sections.append("  - FLASHBACK: Triggered memory from the past")
                sections.append("    Purpose: Character development or backstory reveal")
            
            sections.append("</narrative_variety>")
        
        return "\n".join(sections) if sections else ""
    
    def advance_scene(self):
        """Move to next scene."""
        self.current_scene += 1
    
    def to_dict(self) -> dict:
        return {
            "pov_shifts": [s.to_dict() for s in self.pov_shifts],
            "documents": [d.to_dict() for d in self.documents],
            "flashbacks": [f.to_dict() for f in self.flashbacks],
            "current_scene": self.current_scene,
            "_shift_counter": self._shift_counter,
            "_document_counter": self._document_counter,
            "_flashback_counter": self._flashback_counter,
            "last_pov_shift": self.last_pov_shift,
            "last_document": self.last_document,
            "last_flashback": self.last_flashback,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NarrativeVariety":
        variety = cls()
        variety.current_scene = data.get("current_scene", 0)
        variety._shift_counter = data.get("_shift_counter", 0)
        variety._document_counter = data.get("_document_counter", 0)
        variety._flashback_counter = data.get("_flashback_counter", 0)
        variety.last_pov_shift = data.get("last_pov_shift", -10)
        variety.last_document = data.get("last_document", -10)
        variety.last_flashback = data.get("last_flashback", -10)
        
        for sdata in data.get("pov_shifts", []):
            variety.pov_shifts.append(POVShift.from_dict(sdata))
        
        for ddata in data.get("documents", []):
            variety.documents.append(DocumentInsert.from_dict(ddata))
        
        for fdata in data.get("flashbacks", []):
            variety.flashbacks.append(Flashback.from_dict(fdata))
        
        return variety
