"""
Theme Engine - Thematic Consistency & Symbolic Resonance

Ensures the story explores core themes consistently and uses
symbolic imagery to reinforce thematic elements.

Key Systems:
1. Theme Tracker - Define and monitor core themes
2. Symbolic Resonance - Recurring imagery tied to themes
3. Moral Dilemma Escalation - Track ethical choice stakes
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class ThemeCategory(Enum):
    """Common theme categories for sci-fi narratives."""
    IDENTITY = "identity"  # Who am I?
    TRUST = "trust"  # Who can I rely on?
    SACRIFICE = "sacrifice"  # What am I willing to lose?
    SURVIVAL = "survival"  # What does it take to endure?
    HUMANITY = "humanity"  # What makes us human?
    POWER = "power"  # Who has control?
    ISOLATION = "isolation"  # Alone in the void
    LEGACY = "legacy"  # What do we leave behind?


@dataclass
class Theme:
    """A core theme to explore throughout the story."""
    theme_id: str
    category: ThemeCategory
    description: str
    
    # Tracking
    scenes_explored: List[int] = field(default_factory=list)
    intensity_per_scene: Dict[int, float] = field(default_factory=dict)  # Scene -> 0-1
    
    # Guidance
    target_frequency: int = 4  # Explore every N scenes
    associated_symbols: List[str] = field(default_factory=list)
    key_questions: List[str] = field(default_factory=list)
    
    def scenes_since_last(self, current_scene: int) -> int:
        """Scenes since theme was last explored."""
        if not self.scenes_explored:
            return current_scene
        return current_scene - max(self.scenes_explored)
    
    def should_explore_soon(self, current_scene: int) -> bool:
        """Check if theme needs exploration."""
        return self.scenes_since_last(current_scene) >= self.target_frequency
    
    def mark_explored(self, scene: int, intensity: float = 0.5):
        """Record theme exploration."""
        if scene not in self.scenes_explored:
            self.scenes_explored.append(scene)
        self.intensity_per_scene[scene] = intensity
    
    def get_average_intensity(self) -> float:
        """Get average intensity of theme exploration."""
        if not self.intensity_per_scene:
            return 0.0
        return sum(self.intensity_per_scene.values()) / len(self.intensity_per_scene)
    
    def to_dict(self) -> dict:
        return {
            "theme_id": self.theme_id,
            "category": self.category.value,
            "description": self.description,
            "scenes_explored": self.scenes_explored,
            "intensity_per_scene": {str(k): v for k, v in self.intensity_per_scene.items()},
            "target_frequency": self.target_frequency,
            "associated_symbols": self.associated_symbols,
            "key_questions": self.key_questions,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        return cls(
            theme_id=data["theme_id"],
            category=ThemeCategory(data["category"]),
            description=data["description"],
            scenes_explored=data.get("scenes_explored", []),
            intensity_per_scene={int(k): v for k, v in data.get("intensity_per_scene", {}).items()},
            target_frequency=data.get("target_frequency", 4),
            associated_symbols=data.get("associated_symbols", []),
            key_questions=data.get("key_questions", []),
        )


@dataclass
class Symbol:
    """A recurring symbol tied to themes."""
    symbol_id: str
    description: str
    related_themes: List[str]  # Theme IDs
    
    # Appearances
    appearances: List[int] = field(default_factory=list)
    variations: List[str] = field(default_factory=list)
    
    # Guidance
    suggested_frequency: int = 3
    
    def should_appear(self, current_scene: int) -> bool:
        """Check if symbol should recur."""
        if not self.appearances:
            return False
        return current_scene - max(self.appearances) >= self.suggested_frequency
    
    def mark_appearance(self, scene: int):
        """Record symbol appearance."""
        if scene not in self.appearances:
            self.appearances.append(scene)
    
    def to_dict(self) -> dict:
        return {
            "symbol_id": self.symbol_id,
            "description": self.description,
            "related_themes": self.related_themes,
            "appearances": self.appearances,
            "variations": self.variations,
            "suggested_frequency": self.suggested_frequency,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Symbol":
        return cls(
            symbol_id=data["symbol_id"],
            description=data["description"],
            related_themes=data.get("related_themes", []),
            appearances=data.get("appearances", []),
            variations=data.get("variations", []),
            suggested_frequency=data.get("suggested_frequency", 3),
        )


@dataclass
class MoralDilemma:
    """An ethical choice with escalating stakes."""
    dilemma_id: str
    description: str
    core_conflict: str  # e.g., "safety vs. freedom"
    
    # Escalation
    first_appearance: int
    escalations: List[tuple[int, str]] = field(default_factory=list)  # (scene, description)
    
    # Stakes
    current_stakes: str = "personal"  # personal -> crew -> faction -> galaxy
    resolved: bool = False
    resolution_scene: Optional[int] = None
    
    def escalate(self, scene: int, new_stakes: str, description: str):
        """Escalate the dilemma."""
        self.escalations.append((scene, description))
        self.current_stakes = new_stakes
    
    def resolve(self, scene: int):
        """Mark dilemma as resolved."""
        self.resolved = True
        self.resolution_scene = scene
    
    def to_dict(self) -> dict:
        return {
            "dilemma_id": self.dilemma_id,
            "description": self.description,
            "core_conflict": self.core_conflict,
            "first_appearance": self.first_appearance,
            "escalations": self.escalations,
            "current_stakes": self.current_stakes,
            "resolved": self.resolved,
            "resolution_scene": self.resolution_scene,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MoralDilemma":
        return cls(
            dilemma_id=data["dilemma_id"],
            description=data["description"],
            core_conflict=data["core_conflict"],
            first_appearance=data["first_appearance"],
            escalations=data.get("escalations", []),
            current_stakes=data.get("current_stakes", "personal"),
            resolved=data.get("resolved", False),
            resolution_scene=data.get("resolution_scene"),
        )


@dataclass
class ThemeEngine:
    """Master engine for thematic consistency."""
    
    themes: Dict[str, Theme] = field(default_factory=dict)
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    dilemmas: Dict[str, MoralDilemma] = field(default_factory=dict)
    
    current_scene: int = 0
    _theme_counter: int = 0
    _symbol_counter: int = 0
    _dilemma_counter: int = 0
    
    def add_theme(
        self,
        category: ThemeCategory,
        description: str,
        target_frequency: int = 4,
        key_questions: List[str] = None,
    ) -> str:
        """Add a core theme to track."""
        self._theme_counter += 1
        theme_id = f"theme_{self._theme_counter:03d}"
        
        theme = Theme(
            theme_id=theme_id,
            category=category,
            description=description,
            target_frequency=target_frequency,
            key_questions=key_questions or [],
        )
        
        self.themes[theme_id] = theme
        return theme_id
    
    def add_symbol(
        self,
        description: str,
        related_themes: List[str],
        variations: List[str] = None,
        suggested_frequency: int = 3,
    ) -> str:
        """Add a recurring symbol."""
        self._symbol_counter += 1
        symbol_id = f"symbol_{self._symbol_counter:03d}"
        
        symbol = Symbol(
            symbol_id=symbol_id,
            description=description,
            related_themes=related_themes,
            variations=variations or [],
            suggested_frequency=suggested_frequency,
        )
        
        self.symbols[symbol_id] = symbol
        return symbol_id
    
    def introduce_dilemma(
        self,
        description: str,
        core_conflict: str,
    ) -> str:
        """Introduce a moral dilemma."""
        self._dilemma_counter += 1
        dilemma_id = f"dilemma_{self._dilemma_counter:03d}"
        
        dilemma = MoralDilemma(
            dilemma_id=dilemma_id,
            description=description,
            core_conflict=core_conflict,
            first_appearance=self.current_scene,
        )
        
        self.dilemmas[dilemma_id] = dilemma
        return dilemma_id
    
    def get_themes_due(self) -> List[Theme]:
        """Get themes that need exploration."""
        return [
            t for t in self.themes.values()
            if t.should_explore_soon(self.current_scene)
        ]
    
    def get_symbols_due(self) -> List[Symbol]:
        """Get symbols that should appear."""
        return [
            s for s in self.symbols.values()
            if s.should_appear(self.current_scene)
        ]
    
    def get_active_dilemmas(self) -> List[MoralDilemma]:
        """Get unresolved dilemmas."""
        return [d for d in self.dilemmas.values() if not d.resolved]
    
    def get_narrator_guidance(self) -> str:
        """Generate thematic guidance for narrator."""
        sections = []
        
        # Themes to explore
        themes_due = self.get_themes_due()
        if themes_due:
            sections.append("<thematic_guidance>")
            sections.append("THEMES TO EXPLORE:")
            for theme in themes_due[:2]:  # Top 2
                sections.append(f"  - [{theme.category.value.upper()}] {theme.description}")
                if theme.key_questions:
                    sections.append(f"    Key Question: {theme.key_questions[0]}")
                if theme.associated_symbols:
                    sections.append(f"    Symbols: {', '.join(theme.associated_symbols)}")
            sections.append("</thematic_guidance>")
        
        # Symbols to weave in
        symbols_due = self.get_symbols_due()
        if symbols_due:
            sections.append("\n<symbolic_resonance>")
            sections.append("SYMBOLS TO INCORPORATE:")
            for symbol in symbols_due[:2]:
                sections.append(f"  - {symbol.description}")
                if symbol.variations:
                    sections.append(f"    Variations: {', '.join(symbol.variations[:2])}")
            sections.append("</symbolic_resonance>")
        
        # Active dilemmas
        dilemmas = self.get_active_dilemmas()
        if dilemmas:
            sections.append("\n<moral_dilemmas>")
            sections.append("ACTIVE ETHICAL CONFLICTS:")
            for dilemma in dilemmas:
                sections.append(f"  - {dilemma.core_conflict}: {dilemma.description}")
                sections.append(f"    Current stakes: {dilemma.current_stakes}")
                if len(dilemma.escalations) < 3:
                    sections.append(f"    Consider escalating the stakes")
            sections.append("</moral_dilemmas>")
        
        return "\n".join(sections) if sections else ""
    
    def advance_scene(self):
        """Move to next scene."""
        self.current_scene += 1
    
    def to_dict(self) -> dict:
        return {
            "themes": {tid: t.to_dict() for tid, t in self.themes.items()},
            "symbols": {sid: s.to_dict() for sid, s in self.symbols.items()},
            "dilemmas": {did: d.to_dict() for did, d in self.dilemmas.items()},
            "current_scene": self.current_scene,
            "_theme_counter": self._theme_counter,
            "_symbol_counter": self._symbol_counter,
            "_dilemma_counter": self._dilemma_counter,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ThemeEngine":
        engine = cls()
        engine.current_scene = data.get("current_scene", 0)
        engine._theme_counter = data.get("_theme_counter", 0)
        engine._symbol_counter = data.get("_symbol_counter", 0)
        engine._dilemma_counter = data.get("_dilemma_counter", 0)
        
        for tid, tdata in data.get("themes", {}).items():
            engine.themes[tid] = Theme.from_dict(tdata)
        
        for sid, sdata in data.get("symbols", {}).items():
            engine.symbols[sid] = Symbol.from_dict(sdata)
        
        for did, ddata in data.get("dilemmas", {}).items():
            engine.dilemmas[did] = MoralDilemma.from_dict(ddata)
        
        return engine


# =============================================================================
# Preset Theme Collections
# =============================================================================

def create_starforged_themes() -> ThemeEngine:
    """Create default themes for Starforged setting."""
    engine = ThemeEngine()
    
    # Core themes
    engine.add_theme(
        ThemeCategory.TRUST,
        "In the void, who can you trust when everyone has secrets?",
        key_questions=["Who is hiding something?", "Can I rely on them when it matters?"],
    )
    
    engine.add_theme(
        ThemeCategory.ISOLATION,
        "The crushing loneliness of deep space and the fragility of human connection.",
        key_questions=["What keeps us human when we're alone?", "Is connection worth the risk?"],
    )
    
    engine.add_theme(
        ThemeCategory.SURVIVAL,
        "The cost of survival in an unforgiving universe.",
        key_questions=["What am I willing to sacrifice to survive?", "Is survival enough?"],
    )
    
    # Symbols
    engine.add_symbol(
        "The viewport - window to the void",
        related_themes=["theme_001", "theme_002"],  # Trust, Isolation
        variations=["staring into the black", "the stars beyond the glass", "the infinite dark"],
    )
    
    engine.add_symbol(
        "Recycled air - artificial life support",
        related_themes=["theme_003"],  # Survival
        variations=["the taste of recycled oxygen", "stale air", "the hum of life support"],
    )
    
    return engine
