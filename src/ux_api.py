"""
UX API Endpoints - Player experience enhancement features.
Provides endpoints for vow tracking, consequences, move suggestions, and session continuity.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from src.logging_config import get_logger
from src.vow_tracker import (
    get_all_vows_display,
    get_primary_vow_display,
    generate_vow_reminder,
    calculate_mark_progress,
    format_vow_for_display,
)
from src.consequence_tracker import (
    ConsequenceTracker,
    ConsequenceType,
    ConsequenceSeverity,
    generate_consequence_reminder,
    generate_consequence_from_roll,
    get_consequence_display,
)
from src.move_suggester import (
    suggest_moves,
    get_move_help,
    format_suggestions_for_display,
    should_suggest_moves,
)
from src.session_continuity import (
    SessionTracker,
    generate_session_recap,
    generate_cliffhanger,
    generate_session_summary,
    format_session_end_screen,
)

logger = get_logger("ux_api")


# ============================================================================
# Request/Response Models
# ============================================================================

class VowProgressRequest(BaseModel):
    """Request to calculate vow progress."""
    current_ticks: int
    rank: str


class ConsequenceAddRequest(BaseModel):
    """Request to add a consequence."""
    description: str
    type: str = "complication"
    severity: str = "moderate"
    source: str = "unknown"
    related_npc: Optional[str] = None
    related_location: Optional[str] = None


class ConsequenceResolveRequest(BaseModel):
    """Request to resolve a consequence."""
    consequence_id: str
    resolution: str


class MoveSuggestionRequest(BaseModel):
    """Request for move suggestions."""
    player_input: str
    max_suggestions: int = 3


class SessionEventRequest(BaseModel):
    """Request to record a session event."""
    description: str
    event_type: str
    importance: float = 0.5
    related_entities: Optional[List[str]] = None


# ============================================================================
# Session-level trackers (keyed by session_id)
# ============================================================================

CONSEQUENCE_TRACKERS: Dict[str, ConsequenceTracker] = {}
SESSION_TRACKERS: Dict[str, SessionTracker] = {}


def get_consequence_tracker(session_id: str) -> ConsequenceTracker:
    """Get or create consequence tracker for session."""
    if session_id not in CONSEQUENCE_TRACKERS:
        CONSEQUENCE_TRACKERS[session_id] = ConsequenceTracker()
    return CONSEQUENCE_TRACKERS[session_id]


def get_session_tracker(session_id: str) -> SessionTracker:
    """Get or create session tracker for session."""
    if session_id not in SESSION_TRACKERS:
        SESSION_TRACKERS[session_id] = SessionTracker()
    return SESSION_TRACKERS[session_id]


# ============================================================================
# Route Registration
# ============================================================================

def register_ux_routes(app: FastAPI, sessions: Dict[str, Any]) -> None:
    """Register all UX enhancement routes."""

    # ========================================================================
    # Vow Tracking Endpoints
    # ========================================================================

    @app.get("/api/ux/vows/{session_id}")
    def get_vows(session_id: str):
        """Get all vows formatted for display."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        state = sessions[session_id]
        character = state.get("character")

        if not character:
            return {"vows": [], "primary": None}

        vows = get_all_vows_display(character)
        primary = get_primary_vow_display(character)

        return {
            "vows": [v.to_dict() for v in vows],
            "primary": primary.to_dict() if primary else None,
            "reminder": generate_vow_reminder(vows),
        }

    @app.post("/api/ux/vows/calculate-progress")
    def calculate_progress(req: VowProgressRequest):
        """Calculate what happens when marking progress."""
        result = calculate_mark_progress(req.current_ticks, req.rank)
        return result

    # ========================================================================
    # Consequence Tracking Endpoints
    # ========================================================================

    @app.get("/api/ux/consequences/{session_id}")
    def get_consequences(session_id: str):
        """Get all active consequences."""
        tracker = get_consequence_tracker(session_id)
        return {
            "consequences": get_consequence_display(tracker),
            "reminder": generate_consequence_reminder(tracker),
            "current_turn": tracker.current_turn,
        }

    @app.post("/api/ux/consequences/{session_id}/add")
    def add_consequence(session_id: str, req: ConsequenceAddRequest):
        """Add a new consequence."""
        tracker = get_consequence_tracker(session_id)

        try:
            c_type = ConsequenceType(req.type.lower())
        except ValueError:
            c_type = ConsequenceType.COMPLICATION

        try:
            severity = ConsequenceSeverity(req.severity.lower())
        except ValueError:
            severity = ConsequenceSeverity.MODERATE

        consequence = tracker.add_consequence(
            description=req.description,
            type=c_type,
            severity=severity,
            source=req.source,
            related_npc=req.related_npc,
            related_location=req.related_location,
        )

        return {"consequence": consequence.to_dict()}

    @app.post("/api/ux/consequences/{session_id}/resolve")
    def resolve_consequence(session_id: str, req: ConsequenceResolveRequest):
        """Resolve a consequence."""
        tracker = get_consequence_tracker(session_id)
        success = tracker.resolve_consequence(req.consequence_id, req.resolution)

        if not success:
            raise HTTPException(status_code=404, detail="Consequence not found")

        return {"resolved": True, "id": req.consequence_id}

    @app.post("/api/ux/consequences/{session_id}/advance-turn")
    def advance_consequence_turn(session_id: str):
        """Advance turn counter and check for escalations."""
        tracker = get_consequence_tracker(session_id)
        escalated = tracker.advance_turn()

        return {
            "current_turn": tracker.current_turn,
            "escalated": [c.to_dict() for c in escalated],
        }

    @app.post("/api/ux/consequences/suggest")
    def suggest_consequence(outcome: str, move_name: str, context: str = ""):
        """Suggest a consequence based on roll outcome."""
        suggestion = generate_consequence_from_roll(outcome, move_name, context)
        return {"suggestion": suggestion}

    # ========================================================================
    # Move Suggestion Endpoints
    # ========================================================================

    @app.post("/api/ux/moves/suggest")
    def get_move_suggestions(req: MoveSuggestionRequest):
        """Get move suggestions for player input."""
        suggestions = suggest_moves(req.player_input, req.max_suggestions)

        return {
            "suggestions": [s.to_dict() for s in suggestions],
            "formatted": format_suggestions_for_display(suggestions),
            "should_show": should_suggest_moves(req.player_input),
        }

    @app.get("/api/ux/moves/help/{move_name}")
    def get_move_details(move_name: str):
        """Get detailed help for a specific move."""
        help_data = get_move_help(move_name)

        if not help_data:
            raise HTTPException(status_code=404, detail="Move not found")

        return help_data

    @app.get("/api/ux/moves/list")
    def list_all_moves():
        """Get a list of all available moves."""
        from src.move_suggester import STARFORGED_MOVES

        moves = []
        for move_id, data in STARFORGED_MOVES.items():
            moves.append({
                "id": move_id,
                "name": data["name"],
                "stats": data["stats"],
                "trigger": data["trigger"],
            })

        return {"moves": moves}

    # ========================================================================
    # Session Continuity Endpoints
    # ========================================================================

    @app.get("/api/ux/session/{session_id}/recap")
    def get_session_recap(session_id: str):
        """Get 'Previously on...' recap."""
        tracker = get_session_tracker(session_id)
        recap = generate_session_recap(tracker)

        return {
            "recap": recap,
            "turn_count": tracker.current_turn,
            "npcs_encountered": tracker.npcs_encountered,
            "locations_visited": tracker.locations_visited,
        }

    @app.post("/api/ux/session/{session_id}/event")
    def record_session_event(session_id: str, req: SessionEventRequest):
        """Record a notable session event."""
        tracker = get_session_tracker(session_id)
        tracker.record_event(
            description=req.description,
            event_type=req.event_type,
            importance=req.importance,
            related_entities=req.related_entities,
        )

        return {"recorded": True, "total_events": len(tracker.events)}

    @app.post("/api/ux/session/{session_id}/advance-turn")
    def advance_session_turn(session_id: str):
        """Advance the session turn counter."""
        tracker = get_session_tracker(session_id)
        tracker.advance_turn()

        return {"current_turn": tracker.current_turn}

    @app.get("/api/ux/session/{session_id}/end")
    def get_session_end_screen(session_id: str):
        """Get the session end summary screen."""
        tracker = get_session_tracker(session_id)
        summary = generate_session_summary(tracker)

        return {
            "summary": summary.to_dict(),
            "formatted": format_session_end_screen(summary),
        }

    @app.post("/api/ux/session/{session_id}/record-roll")
    def record_roll_event(session_id: str, move_name: str, outcome: str, context: str = ""):
        """Record a dice roll for session tracking."""
        tracker = get_session_tracker(session_id)
        tracker.record_roll(move_name, outcome, context)

        return {"recorded": True}

    @app.post("/api/ux/session/{session_id}/record-npc")
    def record_npc_encounter(session_id: str, npc_name: str):
        """Record an NPC encounter."""
        tracker = get_session_tracker(session_id)
        tracker.record_npc_encounter(npc_name)

        return {"recorded": True, "npcs": tracker.npcs_encountered}

    @app.post("/api/ux/session/{session_id}/record-location")
    def record_location_visit(session_id: str, location: str):
        """Record visiting a location."""
        tracker = get_session_tracker(session_id)
        tracker.record_location_visit(location)

        return {"recorded": True, "locations": tracker.locations_visited}

    # ========================================================================
    # Combined Dashboard Endpoint
    # ========================================================================

    @app.get("/api/ux/dashboard/{session_id}")
    def get_ux_dashboard(session_id: str):
        """Get combined UX dashboard data."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        state = sessions[session_id]
        character = state.get("character")
        consequence_tracker = get_consequence_tracker(session_id)
        session_tracker = get_session_tracker(session_id)

        # Vows
        vows = get_all_vows_display(character) if character else []
        primary_vow = get_primary_vow_display(character) if character else None

        # Consequences
        consequences = get_consequence_display(consequence_tracker)

        # Session info
        recap = generate_session_recap(session_tracker)

        return {
            "vows": {
                "all": [v.to_dict() for v in vows],
                "primary": primary_vow.to_dict() if primary_vow else None,
            },
            "consequences": {
                "active": consequences,
                "count": len(consequences),
            },
            "session": {
                "turn": session_tracker.current_turn,
                "recap": recap,
                "npcs": session_tracker.npcs_encountered,
                "locations": session_tracker.locations_visited,
            },
        }

    logger.info("UX routes registered")
