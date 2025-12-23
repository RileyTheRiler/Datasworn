"""
Vow Tracker - Prominent vow visibility and progress tracking for players.
Provides helpers for UI to display active vows with progress bars and guidance.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum

from src.logging_config import get_logger

logger = get_logger("vow_tracker")


class VowRank(str, Enum):
    """Vow difficulty ranks with progress increments."""
    TROUBLESOME = "troublesome"  # 3 progress per mark
    DANGEROUS = "dangerous"      # 2 progress per mark
    FORMIDABLE = "formidable"    # 1 progress per mark
    EXTREME = "extreme"          # 2 ticks per mark (half box)
    EPIC = "epic"                # 1 tick per mark (quarter box)


# Progress per mark for each rank (in ticks, where 4 ticks = 1 box)
PROGRESS_PER_MARK = {
    VowRank.TROUBLESOME: 12,  # 3 boxes
    VowRank.DANGEROUS: 8,     # 2 boxes
    VowRank.FORMIDABLE: 4,    # 1 box
    VowRank.EXTREME: 2,       # half box
    VowRank.EPIC: 1,          # quarter box
}

# Max progress is 10 boxes = 40 ticks
MAX_PROGRESS = 40


@dataclass
class VowDisplay:
    """Formatted vow for UI display."""
    name: str
    rank: str
    progress_percent: float
    progress_boxes: int  # 0-10
    progress_ticks: int  # remaining ticks in current box (0-3)
    is_fulfilled: bool
    is_forsaken: bool
    phase: str  # "establishing", "developing", "approaching_climax", "ready_to_fulfill"
    suggested_action: str
    dramatic_tension: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "rank": self.rank,
            "progress_percent": self.progress_percent,
            "progress_boxes": self.progress_boxes,
            "progress_ticks": self.progress_ticks,
            "is_fulfilled": self.is_fulfilled,
            "is_forsaken": self.is_forsaken,
            "phase": self.phase,
            "suggested_action": self.suggested_action,
            "dramatic_tension": self.dramatic_tension,
        }


def get_vow_phase(progress_percent: float) -> tuple[str, str, str]:
    """
    Determine vow phase and provide guidance.

    Returns:
        Tuple of (phase_name, suggested_action, dramatic_tension)
    """
    if progress_percent < 0.25:
        return (
            "establishing",
            "Gather information. Make connections. Understand the stakes.",
            "The path ahead is unclear. Every choice shapes the journey."
        )
    elif progress_percent < 0.50:
        return (
            "developing",
            "Face dangers. Secure advantages. Build momentum.",
            "Obstacles emerge. The cost becomes clearer."
        )
    elif progress_percent < 0.75:
        return (
            "approaching_climax",
            "Confront major challenges. Allies and enemies reveal themselves.",
            "The decisive moment draws near. Stakes are rising."
        )
    else:
        return (
            "ready_to_fulfill",
            "Consider Fulfill Your Vow. Prepare for the final confrontation.",
            "Everything has led to this. Success or failure will be legendary."
        )


def format_vow_for_display(
    name: str,
    rank: str,
    ticks: int,
    completed: bool = False,
    forsaken: bool = False,
) -> VowDisplay:
    """
    Format a vow for UI display with progress visualization.

    Args:
        name: Vow name/description
        rank: VowRank value
        ticks: Current progress in ticks (0-40)
        completed: Whether the vow has been fulfilled
        forsaken: Whether the vow has been abandoned

    Returns:
        VowDisplay with all formatted information
    """
    ticks = max(0, min(ticks, MAX_PROGRESS))
    progress_boxes = ticks // 4
    progress_ticks = ticks % 4
    progress_percent = ticks / MAX_PROGRESS

    phase, suggested_action, dramatic_tension = get_vow_phase(progress_percent)

    if completed:
        phase = "fulfilled"
        suggested_action = "This vow is complete. The oath is honored."
        dramatic_tension = "What was sworn has been achieved."
    elif forsaken:
        phase = "forsaken"
        suggested_action = "This vow was abandoned. Its weight remains."
        dramatic_tension = "Some oaths cannot be kept. The cost echoes."

    return VowDisplay(
        name=name,
        rank=rank,
        progress_percent=round(progress_percent * 100, 1),
        progress_boxes=progress_boxes,
        progress_ticks=progress_ticks,
        is_fulfilled=completed,
        is_forsaken=forsaken,
        phase=phase,
        suggested_action=suggested_action,
        dramatic_tension=dramatic_tension,
    )


def get_all_vows_display(character) -> list[VowDisplay]:
    """
    Get all vows from character state formatted for display.

    Args:
        character: Character model with vows list

    Returns:
        List of VowDisplay objects sorted by progress
    """
    if not character or not hasattr(character, 'vows'):
        return []

    displays = []
    for vow in character.vows:
        display = format_vow_for_display(
            name=vow.name,
            rank=vow.rank,
            ticks=vow.ticks,
            completed=getattr(vow, 'completed', False),
            forsaken=getattr(vow, 'forsaken', False),
        )
        displays.append(display)

    # Sort: active vows by progress descending, then completed, then forsaken
    def sort_key(v: VowDisplay) -> tuple:
        if v.is_forsaken:
            return (2, 0)
        if v.is_fulfilled:
            return (1, 0)
        return (0, -v.progress_percent)

    displays.sort(key=sort_key)
    return displays


def get_primary_vow_display(character) -> Optional[VowDisplay]:
    """
    Get the primary active vow (highest progress, not completed/forsaken).

    Args:
        character: Character model with vows list

    Returns:
        VowDisplay for primary vow or None
    """
    displays = get_all_vows_display(character)
    for display in displays:
        if not display.is_fulfilled and not display.is_forsaken:
            return display
    return None


def generate_vow_reminder(vows: list[VowDisplay]) -> str:
    """
    Generate a narrative reminder about active vows for the narrator.

    Args:
        vows: List of VowDisplay objects

    Returns:
        Formatted reminder string for narrator injection
    """
    active_vows = [v for v in vows if not v.is_fulfilled and not v.is_forsaken]

    if not active_vows:
        return ""

    lines = ["[ACTIVE VOWS - Reference these in narrative when appropriate]"]

    for vow in active_vows[:3]:  # Top 3 vows
        progress_bar = "█" * vow.progress_boxes + "░" * (10 - vow.progress_boxes)
        lines.append(f"• {vow.name} [{progress_bar}] {vow.progress_percent:.0f}%")
        lines.append(f"  Phase: {vow.phase.replace('_', ' ').title()}")
        if vow.phase == "ready_to_fulfill":
            lines.append(f"  ⚠ READY FOR CLIMAX - Consider dramatic resolution")

    return "\n".join(lines)


def calculate_mark_progress(current_ticks: int, rank: str) -> dict[str, Any]:
    """
    Calculate what happens when marking progress on a vow.

    Args:
        current_ticks: Current progress in ticks
        rank: Vow rank

    Returns:
        Dict with new_ticks, boxes_filled, and milestone info
    """
    try:
        rank_enum = VowRank(rank.lower())
    except ValueError:
        rank_enum = VowRank.DANGEROUS

    progress_gain = PROGRESS_PER_MARK[rank_enum]
    new_ticks = min(current_ticks + progress_gain, MAX_PROGRESS)

    old_boxes = current_ticks // 4
    new_boxes = new_ticks // 4
    boxes_filled = new_boxes - old_boxes

    old_percent = current_ticks / MAX_PROGRESS
    new_percent = new_ticks / MAX_PROGRESS

    # Check for phase transitions
    milestones = []
    thresholds = [0.25, 0.50, 0.75]
    for threshold in thresholds:
        if old_percent < threshold <= new_percent:
            if threshold == 0.25:
                milestones.append("The path becomes clearer.")
            elif threshold == 0.50:
                milestones.append("Halfway there. The stakes are rising.")
            elif threshold == 0.75:
                milestones.append("The climax approaches. Prepare for the final push.")

    return {
        "new_ticks": new_ticks,
        "boxes_filled": boxes_filled,
        "progress_percent": round(new_percent * 100, 1),
        "milestones": milestones,
        "ready_to_fulfill": new_percent >= 0.75,
    }
