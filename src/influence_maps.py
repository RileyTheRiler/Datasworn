"""
Infinite-Resolution Influence Maps.
Mathematical field-based spatial reasoning for AI.

Instead of grid tiles, influence radiates as mathematical functions.
Supports gradient queries for tactical positioning.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import math


# ============================================================================
# Influence Types
# ============================================================================

class InfluenceType(Enum):
    """Types of influence that can be tracked."""
    THREAT = "threat"  # Danger from enemies
    SAFETY = "safety"  # Safe areas
    COVER = "cover"  # Cover positions
    VISIBILITY = "visibility"  # How visible a position is
    NOISE = "noise"  # Sound propagation
    PATROL = "patrol"  # Patrol routes
    INTEREST = "interest"  # Points of interest
    TERRITORY = "territory"  # Controlled areas


class FalloffType(Enum):
    """How influence decays with distance."""
    LINEAR = "linear"
    QUADRATIC = "quadratic"  # Inverse square
    GAUSSIAN = "gaussian"
    CONSTANT = "constant"  # No falloff within range


# ============================================================================
# Influence Source
# ============================================================================

@dataclass
class Position:
    """A position in 2D or 3D space."""
    x: float
    y: float
    z: float = 0.0
    
    def distance_to(self, other: "Position") -> float:
        """Calculate distance to another position."""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass
class InfluenceSource:
    """A source of influence in the world."""
    id: str
    position: Position
    influence_type: InfluenceType
    strength: float = 1.0  # Base influence strength
    radius: float = 10.0  # Maximum influence range
    falloff: FalloffType = FalloffType.LINEAR
    is_active: bool = True
    
    def get_influence_at(self, pos: Position) -> float:
        """Calculate influence at a given position."""
        if not self.is_active:
            return 0.0
        
        distance = self.position.distance_to(pos)
        
        # Out of range
        if distance > self.radius:
            return 0.0
        
        # Calculate falloff
        if self.falloff == FalloffType.CONSTANT:
            return self.strength
        elif self.falloff == FalloffType.LINEAR:
            t = distance / self.radius
            return self.strength * (1.0 - t)
        elif self.falloff == FalloffType.QUADRATIC:
            t = distance / self.radius
            return self.strength * (1.0 - t*t)
        elif self.falloff == FalloffType.GAUSSIAN:
            # Gaussian centered at source
            sigma = self.radius / 3.0  # 99.7% within radius
            return self.strength * math.exp(-(distance*distance) / (2*sigma*sigma))
        
        return 0.0
    
    def get_gradient_at(self, pos: Position, epsilon: float = 0.1) -> tuple[float, float, float]:
        """
        Calculate the gradient (direction of steepest ascent) at a position.
        Used for gradient ascent/descent queries.
        """
        # Sample influence at nearby points
        val_center = self.get_influence_at(pos)
        val_x = self.get_influence_at(Position(pos.x + epsilon, pos.y, pos.z))
        val_y = self.get_influence_at(Position(pos.x, pos.y + epsilon, pos.z))
        val_z = self.get_influence_at(Position(pos.x, pos.y, pos.z + epsilon))
        
        # Partial derivatives
        dx = (val_x - val_center) / epsilon
        dy = (val_y - val_center) / epsilon
        dz = (val_z - val_center) / epsilon
        
        return (dx, dy, dz)


# ============================================================================
# Influence Map
# ============================================================================

class InfluenceMap:
    """
    An infinite-resolution influence map using mathematical fields.
    Queries any point in space without grid resolution limits.
    """
    
    def __init__(self):
        self.sources: dict[str, InfluenceSource] = {}
        self.type_sources: dict[InfluenceType, list[str]] = {}  # type -> source_ids
    
    def add_source(self, source: InfluenceSource) -> None:
        """Add an influence source."""
        self.sources[source.id] = source
        
        if source.influence_type not in self.type_sources:
            self.type_sources[source.influence_type] = []
        self.type_sources[source.influence_type].append(source.id)
    
    def remove_source(self, source_id: str) -> None:
        """Remove an influence source."""
        if source_id in self.sources:
            source = self.sources[source_id]
            if source.influence_type in self.type_sources:
                if source_id in self.type_sources[source.influence_type]:
                    self.type_sources[source.influence_type].remove(source_id)
            del self.sources[source_id]
    
    def get_influence_at(
        self,
        pos: Position,
        influence_type: InfluenceType | None = None,
    ) -> float:
        """Get total influence at a position."""
        total = 0.0
        
        if influence_type:
            # Only sum specified type
            source_ids = self.type_sources.get(influence_type, [])
            for sid in source_ids:
                if sid in self.sources:
                    total += self.sources[sid].get_influence_at(pos)
        else:
            # Sum all sources
            for source in self.sources.values():
                total += source.get_influence_at(pos)
        
        return total
    
    def get_gradient_at(
        self,
        pos: Position,
        influence_type: InfluenceType | None = None,
    ) -> tuple[float, float, float]:
        """Get combined gradient at a position."""
        dx, dy, dz = 0.0, 0.0, 0.0
        
        sources = self.sources.values()
        if influence_type:
            source_ids = self.type_sources.get(influence_type, [])
            sources = [self.sources[sid] for sid in source_ids if sid in self.sources]
        
        for source in sources:
            grad = source.get_gradient_at(pos)
            dx += grad[0]
            dy += grad[1]
            dz += grad[2]
        
        return (dx, dy, dz)
    
    def find_local_maximum(
        self,
        start: Position,
        influence_type: InfluenceType,
        step_size: float = 0.5,
        max_steps: int = 100,
    ) -> Position:
        """
        Find local maximum using gradient ascent.
        Returns best position near start.
        """
        current = Position(start.x, start.y, start.z)
        
        for _ in range(max_steps):
            gradient = self.get_gradient_at(current, influence_type)
            magnitude = math.sqrt(gradient[0]**2 + gradient[1]**2 + gradient[2]**2)
            
            if magnitude < 0.01:
                break  # Converged
            
            # Normalize and step
            current.x += (gradient[0] / magnitude) * step_size
            current.y += (gradient[1] / magnitude) * step_size
            current.z += (gradient[2] / magnitude) * step_size
        
        return current
    
    def find_local_minimum(
        self,
        start: Position,
        influence_type: InfluenceType,
        step_size: float = 0.5,
        max_steps: int = 100,
    ) -> Position:
        """
        Find local minimum using gradient descent.
        Useful for finding safest spots (minimum threat).
        """
        current = Position(start.x, start.y, start.z)
        
        for _ in range(max_steps):
            gradient = self.get_gradient_at(current, influence_type)
            magnitude = math.sqrt(gradient[0]**2 + gradient[1]**2 + gradient[2]**2)
            
            if magnitude < 0.01:
                break
            
            # Descend (move opposite to gradient)
            current.x -= (gradient[0] / magnitude) * step_size
            current.y -= (gradient[1] / magnitude) * step_size
            current.z -= (gradient[2] / magnitude) * step_size
        
        return current
    
    def get_tactical_assessment(self, pos: Position) -> dict:
        """Get tactical assessment of a position."""
        threat = self.get_influence_at(pos, InfluenceType.THREAT)
        safety = self.get_influence_at(pos, InfluenceType.SAFETY)
        cover = self.get_influence_at(pos, InfluenceType.COVER)
        visibility = self.get_influence_at(pos, InfluenceType.VISIBILITY)
        
        # Calculate overall rating
        tactical_value = safety + cover - threat - (visibility * 0.5)
        
        return {
            "threat": threat,
            "safety": safety,
            "cover": cover,
            "visibility": visibility,
            "tactical_value": tactical_value,
            "assessment": self._tactical_description(threat, cover, visibility),
        }
    
    def _tactical_description(
        self,
        threat: float,
        cover: float,
        visibility: float,
    ) -> str:
        """Generate tactical description."""
        if threat > 2.0:
            danger = "EXTREMELY DANGEROUS"
        elif threat > 1.0:
            danger = "HIGH THREAT"
        elif threat > 0.5:
            danger = "MODERATE RISK"
        else:
            danger = "LOW THREAT"
        
        if cover > 1.0:
            cover_desc = "good cover available"
        elif cover > 0.5:
            cover_desc = "some cover"
        else:
            cover_desc = "exposed position"
        
        if visibility > 1.0:
            vis_desc = "highly visible"
        elif visibility > 0.5:
            vis_desc = "moderately visible"
        else:
            vis_desc = "concealed"
        
        return f"{danger} - {cover_desc}, {vis_desc}"
    
    def get_narrator_context(self, player_pos: Position) -> str:
        """Generate context for narrator about tactical situation."""
        assessment = self.get_tactical_assessment(player_pos)
        
        lines = ["[TACTICAL ANALYSIS]"]
        lines.append(f"Threat Level: {assessment['threat']:.1f}")
        lines.append(f"Cover Available: {assessment['cover']:.1f}")
        lines.append(f"Visibility: {assessment['visibility']:.1f}")
        lines.append(f"Assessment: {assessment['assessment']}")
        
        # Find safest nearby position
        if assessment["threat"] > 0.5:
            safe_pos = self.find_local_minimum(player_pos, InfluenceType.THREAT)
            direction = self._get_direction(player_pos, safe_pos)
            lines.append(f"Safest direction: {direction}")
        
        return "\n".join(lines)
    
    def _get_direction(self, from_pos: Position, to_pos: Position) -> str:
        """Get cardinal direction from one position to another."""
        dx = to_pos.x - from_pos.x
        dy = to_pos.y - from_pos.y
        
        if abs(dx) > abs(dy):
            return "east" if dx > 0 else "west"
        else:
            return "north" if dy > 0 else "south"
    
    def to_dict(self) -> dict:
        return {
            "sources": {
                sid: {
                    "id": s.id,
                    "position": s.position.to_tuple(),
                    "influence_type": s.influence_type.value,
                    "strength": s.strength,
                    "radius": s.radius,
                    "falloff": s.falloff.value,
                    "is_active": s.is_active,
                }
                for sid, s in self.sources.items()
            },
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "InfluenceMap":
        imap = cls()
        
        for sid, sdata in data.get("sources", {}).items():
            pos_tuple = sdata.get("position", (0, 0, 0))
            source = InfluenceSource(
                id=sdata.get("id", sid),
                position=Position(*pos_tuple),
                influence_type=InfluenceType(sdata.get("influence_type", "threat")),
                strength=sdata.get("strength", 1.0),
                radius=sdata.get("radius", 10.0),
                falloff=FalloffType(sdata.get("falloff", "linear")),
                is_active=sdata.get("is_active", True),
            )
            imap.add_source(source)
        
        return imap


# ============================================================================
# Convenience Functions
# ============================================================================

def create_influence_map() -> InfluenceMap:
    """Create a new influence map."""
    return InfluenceMap()


def add_enemy_threat(
    imap: InfluenceMap,
    enemy_id: str,
    x: float,
    y: float,
    threat_level: float = 1.0,
    radius: float = 15.0,
) -> None:
    """Add an enemy as a threat source."""
    source = InfluenceSource(
        id=f"threat_{enemy_id}",
        position=Position(x, y),
        influence_type=InfluenceType.THREAT,
        strength=threat_level,
        radius=radius,
        falloff=FalloffType.QUADRATIC,
    )
    imap.add_source(source)


def add_cover_point(
    imap: InfluenceMap,
    cover_id: str,
    x: float,
    y: float,
    quality: float = 1.0,
) -> None:
    """Add a cover position."""
    source = InfluenceSource(
        id=f"cover_{cover_id}",
        position=Position(x, y),
        influence_type=InfluenceType.COVER,
        strength=quality,
        radius=3.0,
        falloff=FalloffType.GAUSSIAN,
    )
    imap.add_source(source)


def quick_tactical_check(
    enemies: list[tuple[float, float, float]],  # (x, y, threat)
    player_pos: tuple[float, float],
) -> str:
    """Quick tactical assessment."""
    imap = create_influence_map()
    
    for i, (x, y, threat) in enumerate(enemies):
        add_enemy_threat(imap, f"enemy_{i}", x, y, threat)
    
    pos = Position(player_pos[0], player_pos[1])
    return imap.get_narrator_context(pos)
