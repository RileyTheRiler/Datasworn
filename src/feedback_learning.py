"""
Feedback Learning System - Self-Improving AI Game Master

This module implements a feedback loop that learns from player accept/reject
decisions to continuously improve narrative quality for each specific player.

Key Systems:
1. Example Library - Store accepted/rejected paragraphs with context
2. Preference Extraction - Analyze patterns in player decisions
3. Seed Quality Scoring - Track which narrative seeds land well
4. Few-Shot Retrieval - Find similar good examples for prompting
5. Prompt Modification - Automatically adjust narrator instructions

The more you play, the better it gets - specifically for YOU.
"""

import sqlite3
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from pathlib import Path
import hashlib
import re
from uuid import uuid4
from collections import defaultdict, Counter


# =============================================================================
# DATA SCHEMA
# =============================================================================

@dataclass
class GeneratedParagraph:
    """A single generated paragraph with feedback."""
    paragraph_id: str
    text: str
    accepted: bool
    
    # Context when generated
    pacing: str = "standard"  # slow, standard, fast
    tone: str = "neutral"     # tense, melancholic, hopeful, etc.
    scene_type: str = "general"  # action, dialogue, description, introspection
    npcs_present: List[str] = field(default_factory=list)
    location: str = ""
    
    # Oracle/game context
    oracle_result: str = ""
    move_triggered: str = ""
    
    # Hidden state influence
    seeds_activated: List[str] = field(default_factory=list)
    consequences_triggered: List[str] = field(default_factory=list)
    
    # Metadata
    session_number: int = 0
    timestamp: str = ""
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.word_count:
            self.word_count = len(self.text.split())
        if not self.sentence_count:
            self.sentence_count = len(re.split(r'[.!?]+', self.text))
        if self.sentence_count > 0:
            self.avg_sentence_length = self.word_count / self.sentence_count


@dataclass
class NarrativeSeed:
    """A planted narrative seed with quality tracking."""
    seed_id: str
    content: str
    seed_type: str  # mystery, chekhov_gun, character_secret, etc.
    
    planted_session: int
    activated_session: Optional[int] = None
    
    # Player reaction when activated
    paragraphs_accepted: int = 0
    paragraphs_rejected: int = 0
    player_continued_thread: bool = False
    
    # Calculated quality
    quality_score: float = 0.0
    
    # Metadata
    connected_npcs: List[str] = field(default_factory=list)
    connected_locations: List[str] = field(default_factory=list)


@dataclass
class PreferenceProfile:
    """Extracted player preferences from feedback patterns."""
    
    # Sentence patterns
    preferred_sentence_length: Tuple[float, float] = (8.0, 15.0)  # min, max avg
    action_sentence_length: float = 8.0
    description_sentence_length: float = 12.0
    
    # Vocabulary
    forbidden_words: List[str] = field(default_factory=list)
    preferred_words: List[str] = field(default_factory=list)
    
    # Structure
    max_paragraph_words: int = 150
    preferred_ending_style: str = "question"  # question, action, image
    
    # NPC-specific voice
    npc_voice_preferences: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Tone accuracy
    tone_accuracy: Dict[str, float] = field(default_factory=dict)
    
    # Seed preferences
    preferred_seed_types: List[str] = field(default_factory=list)
    avoided_seed_types: List[str] = field(default_factory=list)
    
    # Last updated
    last_analysis: str = ""
    total_decisions_analyzed: int = 0


# =============================================================================
# DATABASE MANAGER
# =============================================================================

class FeedbackDatabase:
    """SQLite database for feedback storage."""
    
    def __init__(self, db_path: str = "feedback_learning.db"):
        self.db_path = db_path
        self._is_memory = db_path == ":memory:"
        self._conn = None
        
        # For in-memory databases, keep a single connection open
        if self._is_memory:
            self._conn = sqlite3.connect(":memory:")
            self._init_tables(self._conn)
        else:
            # For file databases, just ensure tables exist
            conn = sqlite3.connect(db_path)
            self._init_tables(conn)
            conn.close()
    
    def _get_conn(self):
        """Get a database connection."""
        if self._is_memory:
            return self._conn
        return sqlite3.connect(self.db_path)
    
    def _close_conn(self, conn):
        """Close connection (unless in-memory)."""
        if not self._is_memory:
            conn.close()
    
    def _init_tables(self, conn):
        """Initialize database tables."""
        cursor = conn.cursor()
        
        # Paragraphs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paragraphs (
                paragraph_id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                accepted INTEGER NOT NULL,
                pacing TEXT,
                tone TEXT,
                scene_type TEXT,
                npcs_present TEXT,
                location TEXT,
                oracle_result TEXT,
                move_triggered TEXT,
                seeds_activated TEXT,
                consequences_triggered TEXT,
                session_number INTEGER,
                timestamp TEXT,
                word_count INTEGER,
                sentence_count INTEGER,
                avg_sentence_length REAL
            )
        """)
        
        # Seeds table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seeds (
                seed_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                seed_type TEXT,
                planted_session INTEGER,
                activated_session INTEGER,
                paragraphs_accepted INTEGER DEFAULT 0,
                paragraphs_rejected INTEGER DEFAULT 0,
                player_continued_thread INTEGER DEFAULT 0,
                quality_score REAL DEFAULT 0.0,
                connected_npcs TEXT,
                connected_locations TEXT
            )
        """)
        
        # Preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY,
                profile_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
    
    def save_paragraph(self, para: GeneratedParagraph):
        """Save a paragraph to the database."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO paragraphs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            para.paragraph_id,
            para.text,
            1 if para.accepted else 0,
            para.pacing,
            para.tone,
            para.scene_type,
            json.dumps(para.npcs_present),
            para.location,
            para.oracle_result,
            para.move_triggered,
            json.dumps(para.seeds_activated),
            json.dumps(para.consequences_triggered),
            para.session_number,
            para.timestamp,
            para.word_count,
            para.sentence_count,
            para.avg_sentence_length
        ))
        
        conn.commit()
        self._close_conn(conn)
    
    def query_paragraphs(
        self,
        accepted: Optional[bool] = None,
        pacing: Optional[str] = None,
        tone: Optional[str] = None,
        scene_type: Optional[str] = None,
        limit: int = 100,
        recent_first: bool = True
    ) -> List[GeneratedParagraph]:
        """Query paragraphs with filters."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        query = "SELECT * FROM paragraphs WHERE 1=1"
        params = []
        
        if accepted is not None:
            query += " AND accepted = ?"
            params.append(1 if accepted else 0)
        if pacing:
            query += " AND pacing = ?"
            params.append(pacing)
        if tone:
            query += " AND tone = ?"
            params.append(tone)
        if scene_type:
            query += " AND scene_type = ?"
            params.append(scene_type)
        
        query += " ORDER BY timestamp " + ("DESC" if recent_first else "ASC")
        query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        self._close_conn(conn)
        
        paragraphs = []
        for row in rows:
            paragraphs.append(GeneratedParagraph(
                paragraph_id=row[0],
                text=row[1],
                accepted=bool(row[2]),
                pacing=row[3],
                tone=row[4],
                scene_type=row[5],
                npcs_present=json.loads(row[6]) if row[6] else [],
                location=row[7],
                oracle_result=row[8],
                move_triggered=row[9],
                seeds_activated=json.loads(row[10]) if row[10] else [],
                consequences_triggered=json.loads(row[11]) if row[11] else [],
                session_number=row[12],
                timestamp=row[13],
                word_count=row[14],
                sentence_count=row[15],
                avg_sentence_length=row[16]
            ))
        
        return paragraphs
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM paragraphs")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM paragraphs WHERE accepted = 1")
        accepted = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT session_number) FROM paragraphs")
        sessions = cursor.fetchone()[0]
        
        self._close_conn(conn)
        
        return {
            "total_paragraphs": total,
            "accepted": accepted,
            "rejected": total - accepted,
            "accept_rate": accepted / total if total > 0 else 0,
            "sessions": sessions
        }
    
    def save_seed(self, seed: NarrativeSeed):
        """Save a seed to the database."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO seeds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            seed.seed_id,
            seed.content,
            seed.seed_type,
            seed.planted_session,
            seed.activated_session,
            seed.paragraphs_accepted,
            seed.paragraphs_rejected,
            1 if seed.player_continued_thread else 0,
            seed.quality_score,
            json.dumps(seed.connected_npcs),
            json.dumps(seed.connected_locations)
        ))
        
        conn.commit()
        self._close_conn(conn)
    
    def save_preferences(self, profile: PreferenceProfile):
        """Save preference profile."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        profile_dict = asdict(profile)
        cursor.execute("""
            INSERT INTO preferences (profile_json, created_at) VALUES (?, ?)
        """, (json.dumps(profile_dict), datetime.now().isoformat()))
        
        conn.commit()
        self._close_conn(conn)
    
    def get_latest_preferences(self) -> Optional[PreferenceProfile]:
        """Get most recent preference profile."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT profile_json FROM preferences ORDER BY id DESC LIMIT 1
            """)
            row = cursor.fetchone()
            self._close_conn(conn)
            
            if row:
                data = json.loads(row[0])
                return PreferenceProfile(**data)
        except sqlite3.OperationalError:
            pass  # Table doesn't exist yet
        return None



# =============================================================================
# PREFERENCE ANALYZER
# =============================================================================

class PreferenceAnalyzer:
    """Analyzes feedback patterns to extract player preferences."""
    
    def __init__(self, db: FeedbackDatabase):
        self.db = db
    
    def analyze_all_preferences(self, min_samples: int = 20) -> PreferenceProfile:
        """Run full preference analysis."""
        
        accepted = self.db.query_paragraphs(accepted=True, limit=500)
        rejected = self.db.query_paragraphs(accepted=False, limit=500)
        
        if len(accepted) + len(rejected) < min_samples:
            return PreferenceProfile()  # Not enough data
        
        profile = PreferenceProfile()
        profile.total_decisions_analyzed = len(accepted) + len(rejected)
        profile.last_analysis = datetime.now().isoformat()
        
        # Analyze sentence length
        profile.preferred_sentence_length = self._analyze_sentence_length(accepted, rejected)
        
        # Analyze vocabulary
        profile.forbidden_words = self._find_forbidden_words(accepted, rejected)
        profile.preferred_words = self._find_preferred_words(accepted, rejected)
        
        # Analyze paragraph length
        profile.max_paragraph_words = self._analyze_paragraph_length(accepted, rejected)
        
        # Analyze ending style
        profile.preferred_ending_style = self._analyze_endings(accepted)
        
        # Analyze NPC voices
        profile.npc_voice_preferences = self._analyze_npc_voices(accepted, rejected)
        
        # Analyze tone accuracy
        profile.tone_accuracy = self._analyze_tone_accuracy(accepted, rejected)
        
        return profile
    
    def _analyze_sentence_length(
        self,
        accepted: List[GeneratedParagraph],
        rejected: List[GeneratedParagraph]
    ) -> Tuple[float, float]:
        """Find preferred sentence length range."""
        
        accepted_lengths = [p.avg_sentence_length for p in accepted if p.avg_sentence_length > 0]
        rejected_lengths = [p.avg_sentence_length for p in rejected if p.avg_sentence_length > 0]
        
        if not accepted_lengths:
            return (8.0, 15.0)
        
        # Find sweet spot
        avg_accepted = sum(accepted_lengths) / len(accepted_lengths)
        
        # Standard deviation for range
        variance = sum((x - avg_accepted) ** 2 for x in accepted_lengths) / len(accepted_lengths)
        std_dev = variance ** 0.5
        
        return (max(5, avg_accepted - std_dev), avg_accepted + std_dev)
    
    def _find_forbidden_words(
        self,
        accepted: List[GeneratedParagraph],
        rejected: List[GeneratedParagraph]
    ) -> List[str]:
        """Find words that appear much more often in rejected paragraphs."""
        
        accepted_words = Counter()
        rejected_words = Counter()
        
        for p in accepted:
            accepted_words.update(p.text.lower().split())
        for p in rejected:
            rejected_words.update(p.text.lower().split())
        
        forbidden = []
        
        # Words that appear in rejected but rarely in accepted
        for word, count in rejected_words.most_common(100):
            if len(word) < 4:
                continue
            
            accepted_count = accepted_words.get(word, 0)
            rejected_rate = count / len(rejected) if rejected else 0
            accepted_rate = accepted_count / len(accepted) if accepted else 0
            
            # Word appears 3x more often in rejected
            if rejected_rate > accepted_rate * 3 and count >= 3:
                forbidden.append(word)
        
        # Common problematic words to check
        KNOWN_PROBLEMATIC = ["suddenly", "very", "really", "just", "basically"]
        for word in KNOWN_PROBLEMATIC:
            if word in rejected_words and rejected_words[word] > accepted_words.get(word, 0) * 2:
                if word not in forbidden:
                    forbidden.append(word)
        
        return forbidden[:10]
    
    def _find_preferred_words(
        self,
        accepted: List[GeneratedParagraph],
        rejected: List[GeneratedParagraph]
    ) -> List[str]:
        """Find words that appear much more often in accepted paragraphs."""
        
        accepted_words = Counter()
        rejected_words = Counter()
        
        for p in accepted:
            accepted_words.update(p.text.lower().split())
        for p in rejected:
            rejected_words.update(p.text.lower().split())
        
        preferred = []
        
        for word, count in accepted_words.most_common(100):
            if len(word) < 4:
                continue
            
            rejected_count = rejected_words.get(word, 0)
            accepted_rate = count / len(accepted) if accepted else 0
            rejected_rate = rejected_count / len(rejected) if rejected else 0
            
            # Word appears 3x more often in accepted
            if accepted_rate > rejected_rate * 3 and count >= 3:
                preferred.append(word)
        
        return preferred[:10]
    
    def _analyze_paragraph_length(
        self,
        accepted: List[GeneratedParagraph],
        rejected: List[GeneratedParagraph]
    ) -> int:
        """Find preferred maximum paragraph length."""
        
        accepted_lengths = [p.word_count for p in accepted]
        rejected_lengths = [p.word_count for p in rejected]
        
        if not accepted_lengths:
            return 150
        
        # Find the 90th percentile of accepted lengths
        sorted_lengths = sorted(accepted_lengths)
        idx = int(len(sorted_lengths) * 0.9)
        return sorted_lengths[idx] if idx < len(sorted_lengths) else 150
    
    def _analyze_endings(self, accepted: List[GeneratedParagraph]) -> str:
        """Analyze what ending style is preferred."""
        
        endings = {"question": 0, "action": 0, "image": 0, "statement": 0}
        
        for p in accepted:
            text = p.text.strip()
            if text.endswith("?"):
                endings["question"] += 1
            elif text.endswith("..."):
                endings["image"] += 1
            elif any(verb in text[-50:].lower() for verb in ["you", "move", "reach", "step", "turn"]):
                endings["action"] += 1
            else:
                endings["statement"] += 1
        
        return max(endings, key=endings.get)
    
    def _analyze_npc_voices(
        self,
        accepted: List[GeneratedParagraph],
        rejected: List[GeneratedParagraph]
    ) -> Dict[str, Dict[str, float]]:
        """Analyze accept rates per NPC."""
        
        npc_stats = defaultdict(lambda: {"accepted": 0, "rejected": 0})
        
        for p in accepted:
            for npc in p.npcs_present:
                npc_stats[npc]["accepted"] += 1
        
        for p in rejected:
            for npc in p.npcs_present:
                npc_stats[npc]["rejected"] += 1
        
        result = {}
        for npc, stats in npc_stats.items():
            total = stats["accepted"] + stats["rejected"]
            if total >= 5:  # Minimum sample size
                result[npc] = {
                    "accept_rate": stats["accepted"] / total,
                    "total_samples": total
                }
        
        return result
    
    def _analyze_tone_accuracy(
        self,
        accepted: List[GeneratedParagraph],
        rejected: List[GeneratedParagraph]
    ) -> Dict[str, float]:
        """Analyze accept rate per requested tone."""
        
        tone_stats = defaultdict(lambda: {"accepted": 0, "rejected": 0})
        
        for p in accepted:
            if p.tone:
                tone_stats[p.tone]["accepted"] += 1
        
        for p in rejected:
            if p.tone:
                tone_stats[p.tone]["rejected"] += 1
        
        result = {}
        for tone, stats in tone_stats.items():
            total = stats["accepted"] + stats["rejected"]
            if total >= 3:
                result[tone] = stats["accepted"] / total
        
        return result


# =============================================================================
# FEW-SHOT RETRIEVER
# =============================================================================

class ExampleRetriever:
    """Retrieves similar examples for few-shot prompting."""
    
    def __init__(self, db: FeedbackDatabase):
        self.db = db
    
    def get_positive_examples(
        self,
        context: Dict[str, Any],
        n: int = 3
    ) -> List[str]:
        """Get similar accepted paragraphs."""
        
        # Query with context filtering
        candidates = self.db.query_paragraphs(
            accepted=True,
            pacing=context.get("pacing"),
            tone=context.get("tone"),
            scene_type=context.get("scene_type"),
            limit=n * 3,
            recent_first=True
        )
        
        if len(candidates) < n:
            # Fallback to any accepted
            candidates = self.db.query_paragraphs(
                accepted=True,
                limit=n * 2,
                recent_first=True
            )
        
        # Return top n
        return [c.text for c in candidates[:n]]
    
    def get_negative_examples(
        self,
        context: Dict[str, Any],
        n: int = 2
    ) -> List[str]:
        """Get similar rejected paragraphs to avoid."""
        
        candidates = self.db.query_paragraphs(
            accepted=False,
            pacing=context.get("pacing"),
            tone=context.get("tone"),
            scene_type=context.get("scene_type"),
            limit=n * 2,
            recent_first=True
        )
        
        return [c.text for c in candidates[:n]]
    
    def build_few_shot_prompt(
        self,
        context: Dict[str, Any],
        n_positive: int = 3,
        n_negative: int = 2
    ) -> str:
        """Build a few-shot prompt from examples."""
        
        positive = self.get_positive_examples(context, n_positive)
        negative = self.get_negative_examples(context, n_negative)
        
        if not positive:
            return ""
        
        prompt = "<learned_style>\n"
        prompt += "EXAMPLES THE PLAYER LOVED:\n"
        for i, ex in enumerate(positive, 1):
            prompt += f"  Example {i}: \"{ex[:200]}...\"\n" if len(ex) > 200 else f"  Example {i}: \"{ex}\"\n"
        
        if negative:
            prompt += "\nPATTERNS THE PLAYER REJECTED (avoid these):\n"
            for i, ex in enumerate(negative, 1):
                # Only show the problematic pattern, not full text
                prompt += f"  Anti-example {i}: \"{ex[:100]}...\"\n"
        
        prompt += "</learned_style>\n"
        return prompt


# =============================================================================
# PROMPT MODIFIER
# =============================================================================

class PromptModifier:
    """Generates automatic prompt modifications from preferences."""
    
    def __init__(self, profile: PreferenceProfile):
        self.profile = profile
    
    def generate_modifications(self) -> str:
        """Generate prompt modifications from preference profile."""
        
        mods = []
        
        # Sentence length
        min_len, max_len = self.profile.preferred_sentence_length
        mods.append(f"Target sentence length: {min_len:.0f}-{max_len:.0f} words")
        
        # Forbidden words
        if self.profile.forbidden_words:
            mods.append(f"Never use: {', '.join(self.profile.forbidden_words[:5])}")
        
        # Paragraph length
        if self.profile.max_paragraph_words < 150:
            mods.append(f"Keep paragraphs under {self.profile.max_paragraph_words} words")
        
        # Ending style
        ending_guidance = {
            "question": "End on unanswered questions to maintain tension",
            "action": "End with the player in motion or making a choice",
            "image": "End with a striking visual or sensory image",
            "statement": "End with declarative statements"
        }
        mods.append(ending_guidance.get(self.profile.preferred_ending_style, ""))
        
        # NPC-specific
        for npc, stats in self.profile.npc_voice_preferences.items():
            if stats["accept_rate"] < 0.5 and stats["total_samples"] >= 5:
                mods.append(f"Warning: {npc} dialogue needs work (only {stats['accept_rate']:.0%} accepted)")
        
        # Tone accuracy
        weak_tones = [t for t, acc in self.profile.tone_accuracy.items() if acc < 0.5]
        if weak_tones:
            mods.append(f"Improve: {', '.join(weak_tones)} tone (currently underperforming)")
        
        if not mods:
            return ""
        
        return f"""<learned_preferences>
PLAYER-SPECIFIC STYLE RULES (from {self.profile.total_decisions_analyzed} decisions):
{chr(10).join('  - ' + m for m in mods if m)}
</learned_preferences>
"""


# =============================================================================
# MASTER FEEDBACK ENGINE
# =============================================================================

class FeedbackLearningEngine:
    """Master engine for the self-improving feedback system."""
    
    def __init__(self, db_path: str = "feedback_learning.db"):
        self.db = FeedbackDatabase(db_path)
        self.analyzer = PreferenceAnalyzer(self.db)
        self.retriever = ExampleRetriever(self.db)
        self.current_profile: Optional[PreferenceProfile] = None
        
        # Load existing preferences
        self.current_profile = self.db.get_latest_preferences()
    
    def record_feedback(
        self,
        text: str,
        accepted: bool,
        context: Dict[str, Any]
    ) -> str:
        """Record player feedback on a generated paragraph."""
        
        # Generate unique ID to preserve all samples, even repeated text
        para_id = uuid4().hex
        
        paragraph = GeneratedParagraph(
            paragraph_id=para_id,
            text=text,
            accepted=accepted,
            pacing=context.get("pacing", "standard"),
            tone=context.get("tone", "neutral"),
            scene_type=context.get("scene_type", "general"),
            npcs_present=context.get("npcs_present", []),
            location=context.get("location", ""),
            oracle_result=context.get("oracle_result", ""),
            move_triggered=context.get("move_triggered", ""),
            seeds_activated=context.get("seeds_activated", []),
            consequences_triggered=context.get("consequences_triggered", []),
            session_number=context.get("session_number", 0)
        )
        
        self.db.save_paragraph(paragraph)
        return para_id
    
    def run_preference_analysis(self) -> PreferenceProfile:
        """Run preference analysis and update profile."""
        self.current_profile = self.analyzer.analyze_all_preferences()
        self.db.save_preferences(self.current_profile)
        return self.current_profile

    # Backwards-compatible alias expected by tests/legacy callers
    def analyze_preferences(self) -> PreferenceProfile:
        return self.run_preference_analysis()
    
    def get_learning_guidance(self, context: Dict[str, Any]) -> str:
        """Get all learning-based guidance for narrator prompt."""
        
        sections = []
        
        # Few-shot examples from library
        examples = self.retriever.build_few_shot_prompt(context)
        if examples:
            sections.append(examples)
        
        # Preference-based modifications
        if self.current_profile:
            modifier = PromptModifier(self.current_profile)
            mods = modifier.generate_modifications()
            if mods:
                sections.append(mods)
        
        if not sections:
            return ""
        
        return f"""
<feedback_learning_system>
=== LEARNED FROM YOUR PREFERENCES ===
{chr(10).join(sections)}
</feedback_learning_system>
"""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning system statistics."""
        stats = self.db.get_statistics()
        
        if self.current_profile:
            stats["preferences_analyzed"] = True
            stats["decisions_in_profile"] = self.current_profile.total_decisions_analyzed
            stats["last_analysis"] = self.current_profile.last_analysis
            stats["forbidden_words"] = self.current_profile.forbidden_words
            stats["weak_tones"] = [t for t, acc in self.current_profile.tone_accuracy.items() if acc < 0.5]
        else:
            stats["preferences_analyzed"] = False
        
        return stats
    
    def get_improvement_report(self) -> str:
        """Generate a human-readable improvement report."""
        
        stats = self.get_statistics()
        
        report = f"""
# Feedback Learning Report

## Overview
- Total decisions recorded: {stats['total_paragraphs']}
- Accept rate: {stats['accept_rate']:.1%}
- Sessions played: {stats['sessions']}
"""
        
        if self.current_profile:
            report += f"""
## Learned Preferences

**Sentence Length:** {self.current_profile.preferred_sentence_length[0]:.0f}-{self.current_profile.preferred_sentence_length[1]:.0f} words
**Max Paragraph:** {self.current_profile.max_paragraph_words} words
**Preferred Endings:** {self.current_profile.preferred_ending_style}

**Words to Avoid:**
{', '.join(self.current_profile.forbidden_words) if self.current_profile.forbidden_words else 'None identified yet'}

**Tone Accuracy:**
"""
            for tone, acc in sorted(self.current_profile.tone_accuracy.items(), key=lambda x: -x[1]):
                status = "✓" if acc >= 0.7 else "⚠" if acc >= 0.5 else "✗"
                report += f"  {status} {tone}: {acc:.0%}\n"
            
            report += f"""
**NPC Voice Quality:**
"""
            for npc, data in sorted(
                self.current_profile.npc_voice_preferences.items(), 
                key=lambda x: -x[1]["accept_rate"]
            ):
                status = "✓" if data["accept_rate"] >= 0.7 else "⚠" if data["accept_rate"] >= 0.5 else "✗"
                report += f"  {status} {npc}: {data['accept_rate']:.0%} ({data['total_samples']} samples)\n"
        
        return report
    
    def to_dict(self) -> dict:
        return {
            "db_path": self.db.db_path,
            "has_profile": self.current_profile is not None,
            "stats": self.get_statistics()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FeedbackLearningEngine":
        db_path = data.get("db_path", "feedback_learning.db")
        return cls(db_path)


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FEEDBACK LEARNING SYSTEM - TEST")
    print("=" * 60)
    
    # Use in-memory database for testing
    engine = FeedbackLearningEngine(":memory:")
    
    # Simulate some feedback
    test_paragraphs = [
        ("The airlock cycles. Red light. Green light. You move.", True, "action"),
        ("Torres watches you with cold, calculating eyes.", True, "dialogue"),
        ("Suddenly, without warning, the ship lurched violently forward into the void!", False, "action"),
        ("You feel very angry about the situation.", False, "introspection"),
        ("The corridor stretches ahead, dark and silent.", True, "description"),
    ]
    
    for text, accepted, scene_type in test_paragraphs:
        engine.record_feedback(text, accepted, {
            "scene_type": scene_type,
            "pacing": "fast" if scene_type == "action" else "standard",
            "tone": "tense"
        })
    
    print("\n--- STATISTICS ---")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n--- LEARNING GUIDANCE ---")
    guidance = engine.get_learning_guidance({"scene_type": "action", "pacing": "fast"})
    print(guidance[:1000] if guidance else "Not enough data yet")
    
    print("\n✓ Feedback Learning System operational!")
