"""
Scene Templates System.

Provides structural templates for three types of scenes:
- Crisis Moments: High tension, stakes revealed, decisions under pressure
- Quiet Moments: Intimacy, connection, vulnerability
- Revelation Moments: Truth surfaces, archetype confronted

Each template includes:
- Purpose and trigger conditions
- 5-beat structure
- Archetype integration
- NPC-specific variations
- Example implementations
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from src.character_identity import WoundType

class SceneType(str, Enum):
    CRISIS_SYSTEM_FAILURE = "crisis_system_failure"
    CRISIS_CONFRONTATION = "crisis_confrontation"
    CRISIS_ACCUSATION = "crisis_accusation"
    QUIET_SHARED_SILENCE = "quiet_shared_silence"
    QUIET_CONFESSION = "quiet_confession"
    QUIET_QUESTION = "quiet_question"
    REVELATION_MIRROR = "revelation_mirror"
    REVELATION_COST = "revelation_cost"
    REVELATION_NAMING = "revelation_naming"

@dataclass
class SceneBeat:
    """A single beat in a scene's structure."""
    beat_number: int
    beat_name: str
    description: str
    narrative_text: str
    archetype_variations: Dict[WoundType, str] = field(default_factory=dict)

@dataclass
class SceneChoice:
    """A choice available to the player during a scene."""
    id: str
    text: str
    archetype_signal: Optional[WoundType] = None
    consequence: str = ""
    next_beat: Optional[int] = None
    relationship_change: float = 0.0
    is_growth_choice: bool = False

@dataclass
class SceneTemplate:
    """Complete scene template with all beats and variations."""
    scene_type: SceneType
    name: str
    purpose: str
    trigger_conditions: List[str]
    beats: List[SceneBeat]
    npc_variations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    archetype_integration: Dict[WoundType, str] = field(default_factory=dict)

# ============================================================================
# CRISIS MOMENT TEMPLATES
# ============================================================================

CRISIS_SYSTEM_FAILURE = SceneTemplate(
    scene_type=SceneType.CRISIS_SYSTEM_FAILURE,
    name="System Failure",
    purpose="Force decisions under pressure. Reveal character through action. Test trust.",
    trigger_conditions=[
        "Mid-game (40-60% progress)",
        "Relationships have formed (positive or negative)",
        "Need to force interaction between player and specific NPC"
    ],
    beats=[
        SceneBeat(
            beat_number=1,
            beat_name="ALARM",
            description="Something goes wrong - immediate danger established",
            narrative_text="[ALARM BLARES] The ship's systems flash red. Something critical has failed.",
            archetype_variations={
                WoundType.CONTROLLER: "Your first instinct: assess all variables, take control.",
                WoundType.GHOST: "Your first instinct: emotional distance, focus on survival.",
                WoundType.SAVIOR: "Your first instinct: who needs help? Who can you save?"
            }
        ),
        SceneBeat(
            beat_number=2,
            beat_name="STAKES",
            description="Consequences made clear - time pressure established",
            narrative_text="Kai's voice crackles over comms: 'We have 20 minutes before the reactor goes critical. Maybe less.'",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=3,
            beat_name="CHOICE POINT",
            description="Player must delegate or act - requires trusting an NPC",
            narrative_text="Multiple solutions present themselves. Each requires relying on someone. No option is risk-free.",
            archetype_variations={
                WoundType.CONTROLLER: "Can you delegate? Can you trust others to handle this?",
                WoundType.JUDGE: "Will you blame someone for the failure, or focus on solving it?",
                WoundType.GHOST: "Will you be present for the crew, or emotionally check out?"
            }
        ),
        SceneBeat(
            beat_number=4,
            beat_name="EXECUTION",
            description="Player's choice plays out - success or failure based on relationships",
            narrative_text="Your decision unfolds. The outcome depends on trust, competence, and timing.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=5,
            beat_name="AFTERMATH",
            description="Crisis resolved - relationships altered by player's handling",
            narrative_text="The immediate danger passes. But how you handled it will be remembered.",
            archetype_variations={}
        )
    ],
    npc_variations={
        "kai": {
            "alarm_text": "Kai (panicked): 'The primary injector is failing. We've got maybe fifteen minutes before the reaction goes critical.'",
            "stakes_text": "Torres: 'Can you fix it?' Kai: 'Maybe. But I need someone in the crawlspace manually holding the bypass while I recalibrate. It's a two-person job.'",
            "choices": [
                SceneChoice(
                    id="direct_involvement",
                    text="I'll do it. Tell me what to hold.",
                    consequence="Player and Kai bond through crisis. Success likely.",
                    relationship_change=0.2
                ),
                SceneChoice(
                    id="delegation",
                    text="Torres, you help him. I'll coordinate from here.",
                    archetype_signal=WoundType.CONTROLLER,
                    consequence="Torres and Kai bond. Player seen as leader. Success depends on their relationship.",
                    relationship_change=0.1
                ),
                SceneChoice(
                    id="avoidance",
                    text="Kai, you're the engineer. Handle it.",
                    archetype_signal=WoundType.GHOST,
                    consequence="Kai feels abandoned. Success possible but relationship damaged.",
                    relationship_change=-0.2
                ),
                SceneChoice(
                    id="blame",
                    text="How did this happen? Who was supposed to maintain this?",
                    archetype_signal=WoundType.JUDGE,
                    consequence="Precious time wasted. Lower success chance. Everyone frustrated.",
                    relationship_change=-0.3
                )
            ]
        },
        "torres": {
            "alarm_text": "Torres (urgent): 'Navigation is offline. We're drifting toward the asteroid field.'",
            "stakes_text": "Torres: 'I can reroute through auxiliary systems, but I need someone to manually align the sensor array from outside the ship. In a vac suit. In five minutes.'",
            "choices": [
                SceneChoice(
                    id="volunteer",
                    text="I'll suit up. Walk me through it.",
                    consequence="Direct action. Torres respects courage. High risk, high reward.",
                    relationship_change=0.2
                ),
                SceneChoice(
                    id="delegate_vasquez",
                    text="Vasquez has EVA experience. Vasquez, suit up.",
                    consequence="Vasquez handles it. Success depends on his competence and willingness.",
                    relationship_change=0.0
                )
            ]
        }
    },
    archetype_integration={
        WoundType.CONTROLLER: "Crisis highlights: Can they delegate? Can they trust others? Trap: Trying to do everything themselves fails. Growth: Success comes from trusting the crew.",
        WoundType.JUDGE: "Crisis highlights: Do they blame someone for the failure? Trap: Spending time on blame instead of solving. Growth: Accepting that fault doesn't matter right now.",
        WoundType.GHOST: "Crisis highlights: Will they be present for the crew? Trap: Emotionally checking out when people need them. Growth: Staying engaged, visible, leading.",
        WoundType.SAVIOR: "Crisis highlights: Can they let others take risks? Trap: Trying to save everyone personally. Growth: Trusting others to save themselves.",
        WoundType.CYNIC: "Crisis highlights: Do they expect failure? Trap: Cynicism becomes self-fulfilling prophecy. Growth: Choosing to believe in the crew's competence."
    }
)

CRISIS_CONFRONTATION = SceneTemplate(
    scene_type=SceneType.CRISIS_CONFRONTATION,
    name="Confrontation Escalation",
    purpose="Two NPCs in conflict. Player must intervene or let it explode.",
    trigger_conditions=[
        "Any time after 30% progress",
        "Two NPCs with existing tension",
        "Player's archetype will be tested by the conflict"
    ],
    beats=[
        SceneBeat(
            beat_number=1,
            beat_name="DISCOVERY",
            description="Player finds/hears argument in progress",
            narrative_text="You hear raised voices from the corridor. Torres and Kai are in heated confrontation.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=2,
            beat_name="ESCALATION",
            description="One NPC says something they can't take back",
            narrative_text="The argument reaches a breaking point. Words that will leave scars.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=3,
            beat_name="INTERVENTION",
            description="Player chooses how (or whether) to engage",
            narrative_text="They look to you. Or ignore you. Either way, you must choose.",
            archetype_variations={
                WoundType.JUDGE: "Do you pick a side? On what basis?",
                WoundType.SAVIOR: "Can you let people fight their own battles?",
                WoundType.CYNIC: "Do you expect the worst from both?"
            }
        ),
        SceneBeat(
            beat_number=4,
            beat_name="RESOLUTION",
            description="Immediate outcome of intervention",
            narrative_text="Your choice has immediate consequences. The confrontation ends... one way or another.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=5,
            beat_name="ECHO",
            description="Later consequences of the confrontation",
            narrative_text="Later, NPCs reference how you handled it. The memory lingers.",
            archetype_variations={}
        )
    ],
    npc_variations={
        "torres_vs_kai": {
            "discovery_text": "Torres has discovered Kai's been skimming fuel. She's furious.",
            "escalation_text": "Torres: 'You've been stealing from the ship. From all of us.' Kai: 'I had to! You don't understand—I owe people. Dangerous people.' Torres: 'So your debts are more important than our survival?' Torres's hand moves toward her sidearm.",
            "choices": [
                SceneChoice(
                    id="de_escalate",
                    text="Torres, stand down. This isn't helping.",
                    consequence="Immediate de-escalation. Both NPCs respect authority but issue unresolved.",
                    relationship_change=0.0
                ),
                SceneChoice(
                    id="investigate",
                    text="Kai, is this true? How much did you take?",
                    archetype_signal=WoundType.CONTROLLER,
                    consequence="Investigation mode. Torres feels unsupported. Kai feels interrogated.",
                    relationship_change=-0.1
                ),
                SceneChoice(
                    id="judge_kai",
                    text="He's an addict and a thief. Torres is right.",
                    archetype_signal=WoundType.JUDGE,
                    consequence="Kai is condemned. Torres gains trust. Kai loses all trust. Relationship damaged permanently.",
                    relationship_change=-0.5
                ),
                SceneChoice(
                    id="let_them_fight",
                    text="[Say nothing. Let them sort it out.]",
                    archetype_signal=WoundType.GHOST,
                    consequence="Avoidance. Both NPCs feel abandoned. Conflict escalates.",
                    relationship_change=-0.2
                ),
                SceneChoice(
                    id="pragmatic",
                    text="We'll figure out the debts later. Right now we need to survive.",
                    consequence="Pragmatic de-escalation. Issue deferred but not resolved.",
                    relationship_change=0.1
                ),
                SceneChoice(
                    id="vulnerable",
                    text="I've made mistakes too. We all have.",
                    archetype_signal=WoundType.SAVIOR,
                    is_growth_choice=True,
                    consequence="Vulnerability creates space for resolution. Both NPCs soften.",
                    relationship_change=0.2
                )
            ]
        }
    },
    archetype_integration={
        WoundType.JUDGE: "Trap: Declaring someone 'right' and someone 'wrong'. Growth: Finding the complexity in both positions.",
        WoundType.SAVIOR: "Trap: Inserting themselves unnecessarily. Growth: Recognizing when to step back.",
        WoundType.CYNIC: "Trap: Making cynical comments that inflame the situation. Growth: Recognizing genuine grievance under the conflict."
    }
)

CRISIS_ACCUSATION = SceneTemplate(
    scene_type=SceneType.CRISIS_ACCUSATION,
    name="The Accusation",
    purpose="Someone accuses someone else of the murder. Wrongly or rightly.",
    trigger_conditions=[
        "After significant investigation progress (50%+)",
        "Player has formed opinion about suspects",
        "Need to force player to defend or condemn"
    ],
    beats=[
        SceneBeat(
            beat_number=1,
            beat_name="THE CHARGE",
            description="An NPC publicly accuses another of the murder",
            narrative_text="Torres calls everyone to the common area. She has evidence. She has a suspect.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=2,
            beat_name="THE DEFENSE",
            description="Accused responds - denial, explanation, or silence",
            narrative_text="The accused responds. The crew watches. The tension is unbearable.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=3,
            beat_name="THE ARBITER",
            description="Player must respond - no neutral ground",
            narrative_text="All eyes turn to you. Silence is a choice. What do you decide?",
            archetype_variations={
                WoundType.JUDGE: "This is your moment. But are you judging evidence or people?",
                WoundType.CONTROLLER: "You want all the facts. But there's no time for perfect information.",
                WoundType.SAVIOR: "Can you save both the accused and the truth?"
            }
        ),
        SceneBeat(
            beat_number=4,
            beat_name="THE VERDICT",
            description="Whatever player decides, consequences follow",
            narrative_text="Your decision is made. The crew reacts. There's no taking it back.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=5,
            beat_name="THE RECKONING",
            description="Later scenes reveal consequences",
            narrative_text="Days later, the truth emerges. Were you right? Were you wrong? Either way, you'll live with it.",
            archetype_variations={}
        )
    ],
    npc_variations={
        "torres_accuses_yuki": {
            "charge_text": "Torres (in the common area, with crew present): 'I saw you. The night the captain died. Coming from his quarters. 0300. You want to explain that?' Yuki (very still): 'I don't have to explain anything to you.' Torres: 'You do if you want to keep breathing on this ship.'",
            "choices": [
                SceneChoice(
                    id="defend_yuki",
                    text="That's not evidence. Proximity isn't guilt.",
                    consequence="Defense of Yuki. Torres feels betrayed. Yuki notes the support.",
                    relationship_change=0.2
                ),
                SceneChoice(
                    id="prosecute_yuki",
                    text="Torres is right. What were you doing there?",
                    archetype_signal=WoundType.JUDGE,
                    consequence="Prosecution. Torres gains trust. Yuki becomes defensive or confesses.",
                    relationship_change=-0.3
                ),
                SceneChoice(
                    id="process",
                    text="Everyone calm down. We need to investigate, not lynch.",
                    consequence="Process-focused. Buys time. No immediate resolution.",
                    relationship_change=0.0
                ),
                SceneChoice(
                    id="alliance_torres",
                    text="I've suspected her too. What else do you have?",
                    archetype_signal=WoundType.CONTROLLER,
                    consequence="Alliance with Torres. Investigation intensifies. Yuki isolated.",
                    relationship_change=-0.4
                ),
                SceneChoice(
                    id="observe",
                    text="[Say nothing. Let it play out.]",
                    archetype_signal=WoundType.GHOST,
                    consequence="Observation. Crew sees you as weak or calculating. Consequences vary.",
                    relationship_change=-0.1
                )
            ]
        }
    },
    archetype_integration={
        WoundType.JUDGE: "This is your archetype's domain. But judgment without wisdom is cruelty.",
        WoundType.CONTROLLER: "You want all the data. But leadership sometimes means deciding with incomplete information.",
        WoundType.SAVIOR: "Can you save the accused? Can you save the truth? Can you save both?"
    }
)

# ============================================================================
# QUIET MOMENT TEMPLATES
# ============================================================================

QUIET_SHARED_SILENCE = SceneTemplate(
    scene_type=SceneType.QUIET_SHARED_SILENCE,
    name="The Shared Silence",
    purpose="Two characters together in comfortable silence. Words not required.",
    trigger_conditions=[
        "After crisis or confrontation",
        "Relationship has reached a threshold",
        "Player has demonstrated capacity for presence"
    ],
    beats=[
        SceneBeat(
            beat_number=1,
            beat_name="PROXIMITY",
            description="Player and NPC find themselves in the same space",
            narrative_text="You find Ember on the observation deck, looking at the stars. She doesn't turn around.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=2,
            beat_name="PRESENCE",
            description="If player stays, nothing needs to happen - the staying IS the point",
            narrative_text="Ember: 'You can stay if you want. I don't mind.' Long silence. The hum of the ship. The stars.",
            archetype_variations={
                WoundType.GHOST: "This scene TYPE is the test. Can you be present without fleeing?",
                WoundType.CONTROLLER: "The silence is uncomfortable—nothing to DO. Can you just... be?"
            }
        ),
        SceneBeat(
            beat_number=3,
            beat_name="THE CRACK",
            description="Eventually, one speaks - something small",
            narrative_text="Ember (eventually): 'The captain used to come here too. We'd sit. Sometimes for hours. Not talking.' Pause. 'I didn't understand what we were doing. Just... sitting. But now I think I do.'",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=4,
            beat_name="RECIPROCITY",
            description="If player engages, connection deepens",
            narrative_text="Your response matters. Or your continued silence. Both are communication.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=5,
            beat_name="RETURN",
            description="Scene ends naturally - something has changed, quietly",
            narrative_text="Eventually, one of you leaves. Or you both stay. Either way, something has shifted.",
            archetype_variations={}
        )
    ],
    npc_variations={
        "ember": {
            "proximity_text": "You find Ember on the observation deck, looking at the stars. She doesn't turn around.",
            "presence_text": "Ember: 'You can stay if you want. I don't mind.'",
            "choices": [
                SceneChoice(
                    id="stay_silent",
                    text="[Stay silent. Be present.]",
                    is_growth_choice=True,
                    consequence="+Connection, +Resilient signal. Ember feels seen.",
                    relationship_change=0.3
                ),
                SceneChoice(
                    id="engage",
                    text="What do you think you were doing?",
                    consequence="Engagement. Allows her to explain. Connection maintained.",
                    relationship_change=0.1
                ),
                SceneChoice(
                    id="leave",
                    text="I should probably get back to the investigation.",
                    archetype_signal=WoundType.GHOST,
                    consequence="-Connection, +Ghost signal. Ember notes the pattern.",
                    relationship_change=-0.2
                ),
                SceneChoice(
                    id="interrogate",
                    text="Tell me what you've observed about the crew.",
                    archetype_signal=WoundType.CONTROLLER,
                    consequence="-Connection, +Controller signal. Ember feels used.",
                    relationship_change=-0.3
                )
            ]
        }
    },
    archetype_integration={
        WoundType.GHOST: "Success: Staying reveals capacity for connection. Failure: Leaving confirms the pattern.",
        WoundType.CONTROLLER: "The silence is uncomfortable—nothing to DO. Learning that presence is enough is growth."
    }
)

QUIET_CONFESSION = SceneTemplate(
    scene_type=SceneType.QUIET_CONFESSION,
    name="The Confession",
    purpose="An NPC shares something true. Vulnerability offered.",
    trigger_conditions=[
        "High relationship with specific NPC",
        "Player has demonstrated trustworthiness",
        "Appropriate story beat for NPC's arc"
    ],
    beats=[
        SceneBeat(
            beat_number=1,
            beat_name="APPROACH",
            description="NPC seeks out the player",
            narrative_text="Dr. Okonkwo finds you in the med bay. Something in her manner indicates weight. 'Can we talk?'",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=2,
            beat_name="HESITATION",
            description="NPC circles the truth - testing",
            narrative_text="She circles the truth. Small talk, deflection, testing whether you're safe.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=3,
            beat_name="THE REVEAL",
            description="NPC shares something true - vulnerability exposed",
            narrative_text="She tells the story. The impossible choice. The child. The administrator. The career destroyed. 'I've carried this for fourteen years. The weight of it.'",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=4,
            beat_name="RESPONSE",
            description="Player's reaction matters enormously",
            narrative_text="She's watching you. Waiting. This moment will be remembered.",
            archetype_variations={
                WoundType.JUDGE: "Trap: Responding to confession with evaluation. Growth: Receiving without judging.",
                WoundType.SAVIOR: "Trap: Immediately trying to fix what was shared. Growth: Letting the sharing BE the healing."
            }
        ),
        SceneBeat(
            beat_number=5,
            beat_name="AFTERMATH",
            description="The relationship is changed",
            narrative_text="The conversation ends. But the trust—or the distance—remains.",
            archetype_variations={}
        )
    ],
    npc_variations={
        "okonkwo": {
            "reveal_text": "Dr. Okonkwo: 'I want to tell you something. I've never... not since it happened.' She tells the story of the impossible choice. The child. The administrator. The career destroyed. 'Everyone says I made the right choice—medically, ethically. But the child died anyway. Two days later. So what was it for? What did I sacrifice everything for?'",
            "choices": [
                SceneChoice(
                    id="compassion",
                    text="You did what you thought was right. That's all anyone can do.",
                    is_growth_choice=True,
                    consequence="Compassion. Deep connection. Okonkwo trusts you.",
                    relationship_change=0.4
                ),
                SceneChoice(
                    id="empathy",
                    text="That must have been incredibly difficult. I'm sorry.",
                    is_growth_choice=True,
                    consequence="Empathy. Connection deepens. Okonkwo feels heard.",
                    relationship_change=0.3
                ),
                SceneChoice(
                    id="justice",
                    text="The board was wrong to punish you.",
                    archetype_signal=WoundType.JUDGE,
                    consequence="Justice focus. Okonkwo appreciates it but it misses the emotional point.",
                    relationship_change=0.1
                ),
                SceneChoice(
                    id="savior",
                    text="What can I do to help?",
                    archetype_signal=WoundType.SAVIOR,
                    consequence="Savior response. May or may not be appropriate. Okonkwo wanted witness, not rescue.",
                    relationship_change=0.0
                ),
                SceneChoice(
                    id="deflect",
                    text="Why are you telling me this?",
                    archetype_signal=WoundType.GHOST,
                    consequence="Deflection. Okonkwo retreats. Trust damaged.",
                    relationship_change=-0.3
                )
            ]
        }
    },
    archetype_integration={
        WoundType.JUDGE: "Trap: Responding to confession with evaluation. Growth: Receiving without judging.",
        WoundType.SAVIOR: "Trap: Immediately trying to fix what was shared. Growth: Letting the sharing BE the healing.",
        WoundType.GHOST: "Trap: Deflecting vulnerability. Growth: Receiving it with presence."
    }
)

QUIET_QUESTION = SceneTemplate(
    scene_type=SceneType.QUIET_QUESTION,
    name="The Question",
    purpose="An NPC asks something real. The player must answer truthfully or deflect.",
    trigger_conditions=[
        "Relationship has developed",
        "Player has received but not given vulnerability",
        "NPC tests reciprocity"
    ],
    beats=[
        SceneBeat(
            beat_number=1,
            beat_name="SETUP",
            description="Casual conversation or quiet moment",
            narrative_text="After a late-night repair, Kai lingers. The work is done but he's not leaving.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=2,
            beat_name="THE ASK",
            description="NPC asks something personal",
            narrative_text="Kai: 'Can I ask you something? You don't have to answer.' Pause. 'Why are you here? On this ship. Really.'",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=3,
            beat_name="THE CHOICE",
            description="Player can answer honestly, deflect, or lie",
            narrative_text="He's watching you. Genuinely curious. Not accusatory. This is a test of your capacity for vulnerability.",
            archetype_variations={
                WoundType.GHOST: "Can you let someone in? Or will you deflect?",
                WoundType.CONTROLLER: "Can you share something you don't control?",
                WoundType.FUGITIVE: "Can you share your 'before'?"
            }
        ),
        SceneBeat(
            beat_number=4,
            beat_name="NPC RESPONSE",
            description="If honest: deeper connection. If deflected: NPC understands but notes pattern",
            narrative_text="Kai responds to your answer. Or your non-answer. Both tell him something.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=5,
            beat_name="INTEGRATION",
            description="The exchange is recorded in NPC memory",
            narrative_text="The conversation ends. But Kai will remember this moment.",
            archetype_variations={}
        )
    ],
    npc_variations={
        "kai": {
            "ask_text": "Kai: 'Can I ask you something? You don't have to answer.' 'Why are you here? On this ship. Really.' 'Everyone has a \"before.\" Torres has her court-martial. I have my... everything. Even Vasquez has something he's running from.' 'What's yours?'",
            "choices": [
                SceneChoice(
                    id="share_truth",
                    text="[Share something true about your past]",
                    is_growth_choice=True,
                    consequence="Vulnerability. Deep connection. Kai shares more in return.",
                    relationship_change=0.4
                ),
                SceneChoice(
                    id="deflect_investigation",
                    text="I'm here because I want to find out what happened to the captain.",
                    archetype_signal=WoundType.GHOST,
                    consequence="Deflection. Kai notes the pattern. Connection stalls.",
                    relationship_change=0.0
                ),
                SceneChoice(
                    id="reject",
                    text="That's not really your business.",
                    archetype_signal=WoundType.CONTROLLER,
                    consequence="Rejection. Kai retreats. Trust damaged.",
                    relationship_change=-0.3
                ),
                SceneChoice(
                    id="counter_question",
                    text="What makes you think I'm running from something?",
                    consequence="Counter-question. Deflection but not hostile. Neutral.",
                    relationship_change=0.0
                ),
                SceneChoice(
                    id="defer",
                    text="I'll tell you. But not tonight.",
                    consequence="Deferral. Creates promise. Kai accepts. Connection maintained.",
                    relationship_change=0.1
                )
            ]
        }
    },
    archetype_integration={
        WoundType.GHOST: "Can you let someone in? Or will you deflect? This tests your capacity for vulnerability.",
        WoundType.CONTROLLER: "Can you share something you don't control? Something uncertain?",
        WoundType.FUGITIVE: "Can you share your 'before'? Or is it too dangerous?"
    }
)

# ============================================================================
# REVELATION MOMENT TEMPLATES
# ============================================================================

REVELATION_MIRROR = SceneTemplate(
    scene_type=SceneType.REVELATION_MIRROR,
    name="The Mirror",
    purpose="Player sees their pattern reflected in someone else.",
    trigger_conditions=[
        "Archetype confidence above threshold",
        "Appropriate story progress (25%)",
        "Setup scenes have occurred"
    ],
    beats=[
        SceneBeat(
            beat_number=1,
            beat_name="CONTEXT",
            description="Player observing or participating in scene",
            narrative_text="You're reading the captain's logs. Or watching an interaction. Focus on another character.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=2,
            beat_name="THE PATTERN",
            description="The character exhibits the player's archetype pattern",
            narrative_text="The character's behavior is familiar. Too familiar. You've seen this before.",
            archetype_variations={
                WoundType.CONTROLLER: "The captain's obsessive need to control everything. To know everything. To manage every variable.",
                WoundType.JUDGE: "Torres's harsh judgment without nuance. Weak is weak. No excuse changes that.",
                WoundType.GHOST: "Dr. Okonkwo's professional detachment. Keep your distance, and the losses are manageable."
            }
        ),
        SceneBeat(
            beat_number=3,
            beat_name="RECOGNITION (OPTIONAL)",
            description="If player is perceptive, they may notice the mirror",
            narrative_text="Do you see it? The pattern? The reflection?",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=4,
            beat_name="AFTERMATH",
            description="The observed behavior has consequences",
            narrative_text="The pattern has consequences. For them. And maybe... for you.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=5,
            beat_name="SEED PLANTED",
            description="Foreshadowing for later explicit revelation",
            narrative_text="The seed is planted. Later, Ember will ask: 'Did you see yourself?'",
            archetype_variations={}
        )
    ],
    npc_variations={
        "reyes_controller": {
            "pattern_text": "Captain's Log: 'Torres made a decision I disagreed with today. She didn't consult me. I know I should trust her judgment—she's qualified—but I needed to know. I needed to understand. I went through the nav records afterward. Just to check.' Later: 'I'm doing it again. The thing Maria always warned me about. Needing to control everything. \"You can't hold water in your fists,\" she used to say. But what else can I do?'"
        },
        "torres_judge": {
            "pattern_text": "You witness Torres confronting Kai: 'Again? This is pathetic. You're an addict who can't control himself. That makes you a liability. The captain should have left you at the last port.' Kai: 'You don't know what it's like.' Torres: 'I know enough. Weak is weak. No excuse changes that.'"
        }
    },
    archetype_integration={
        WoundType.CONTROLLER: "See the captain's control obsession. Later: 'Did you see yourself in those logs?'",
        WoundType.JUDGE: "See Torres's harsh judgment. Later: 'You saw how Torres talked to Kai. You do the same thing. Just quieter.'",
        WoundType.GHOST: "See Dr. Okonkwo's detachment. Later: 'Dr. Okonkwo never lets anyone in. You do that too—I can tell.'"
    }
)

REVELATION_COST = SceneTemplate(
    scene_type=SceneType.REVELATION_COST,
    name="The Cost",
    purpose="Player's pattern directly harms someone.",
    trigger_conditions=[
        "Player has exhibited archetype behavior consistently",
        "An NPC has been affected",
        "Time for consequences to materialize"
    ],
    beats=[
        SceneBeat(
            beat_number=1,
            beat_name="CONSEQUENCE ARRIVES",
            description="An NPC is hurt - the harm is traceable to player's behavior",
            narrative_text="Torres approaches you in the corridor. Her expression is cold.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=2,
            beat_name="CONFRONTATION",
            description="The harmed NPC confronts the player",
            narrative_text="Torres: 'I'm not talking to you anymore. About the investigation or anything else.' You: 'What? Why?' Torres: 'You know why.'",
            archetype_variations={
                WoundType.CONTROLLER: "Torres: 'You went through my quarters. You read my personal files. Things I've never shared with anyone. I was starting to trust you. But you couldn't wait. You couldn't just ask.'",
                WoundType.JUDGE: "Kai: 'You looked at me like I was already dead. Like I was worthless. And I started to believe it.'",
                WoundType.GHOST: "Ember: 'I told you real things. About my life. My fears. Every time, you nod. And then you leave. It's like you can't be present.'"
            }
        ),
        SceneBeat(
            beat_number=3,
            beat_name="DENIAL OR ACCEPTANCE",
            description="Player can accept responsibility or deflect",
            narrative_text="How do you respond? With acknowledgment? Justification? Silence?",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=4,
            beat_name="REVERB",
            description="Other NPCs react - the pattern has been made visible",
            narrative_text="Word spreads. Other crew members have noticed too. The pattern is visible now.",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=5,
            beat_name="FORK POINT",
            description="This moment matters for Hero/Tragedy fork",
            narrative_text="This is a crucial moment. Accept and grow? Or justify and continue?",
            archetype_variations={}
        )
    ],
    npc_variations={
        "torres_controller": {
            "confrontation_text": "Torres: 'You went through my quarters. You read my personal files—the court-martial documents. Things I've never shared with anyone. I was starting to trust you. I was going to tell you what I saw that night. But you couldn't wait. You couldn't just ask. You had to control everything, take everything, know everything. Now you know my secrets. And you'll never know what I saw.'",
            "choices": [
                SceneChoice(
                    id="apologize",
                    text="Torres, wait—I'm sorry.",
                    is_growth_choice=True,
                    consequence="Acknowledgment. May or may not work. Hero signal.",
                    relationship_change=0.1
                ),
                SceneChoice(
                    id="justify",
                    text="I did what I had to for the investigation.",
                    archetype_signal=WoundType.CONTROLLER,
                    consequence="Justification. +Controller. Tragedy signal.",
                    relationship_change=-0.3
                ),
                SceneChoice(
                    id="accept",
                    text="[Let her go. Accept the consequence.]",
                    is_growth_choice=True,
                    consequence="Acceptance of consequence. Hero signal.",
                    relationship_change=0.0
                ),
                SceneChoice(
                    id="deflect",
                    text="Everyone has secrets. You would have done the same.",
                    archetype_signal=WoundType.CYNIC,
                    consequence="Deflection. Tragedy signal.",
                    relationship_change=-0.4
                )
            ]
        }
    },
    archetype_integration={
        WoundType.CONTROLLER: "Control costs trust. Someone you needed has been driven away by your need to know everything.",
        WoundType.JUDGE: "Judgment costs connection. Someone you judged has internalized your verdict.",
        WoundType.GHOST: "Absence costs relationship. Someone who reached out has given up."
    }
)

REVELATION_NAMING = SceneTemplate(
    scene_type=SceneType.REVELATION_NAMING,
    name="The Naming (Ember)",
    purpose="Ember speaks the truth the player cannot see.",
    trigger_conditions=[
        "Late in the revelation ladder (70%)",
        "Ember has sufficient relationship with player",
        "Pattern is clear enough to name"
    ],
    beats=[
        SceneBeat(
            beat_number=1,
            beat_name="APPROACH",
            description="Ember finds the player - something in her manner is different",
            narrative_text="Observation deck. Night cycle. Ember is waiting. 'Can I tell you something?'",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=2,
            beat_name="OBSERVATION",
            description="Ember describes what she's seen - without judgment",
            narrative_text="Ember: 'I've been trying to figure you out. Since you got here.' Pause. 'At first I thought you were just private. Some people are. That's okay. But it's more than that, isn't it?'",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=3,
            beat_name="THE NAME",
            description="Ember gives the pattern a name",
            narrative_text="Ember names what she sees. Not clinical. Personal. Specific. The truth spoken aloud.",
            archetype_variations={
                WoundType.GHOST: "Ember: 'You're not really here. You're... somewhere else. Already gone. Planning your exit. I've told you real things. Every time, you nod. And then you leave. It's like you can't be present. Like presence is dangerous.'",
                WoundType.CONTROLLER: "Ember: 'You need to know everything. Control everything. But the tighter you hold, the more slips away. I've watched you push people away by pulling them too close.'",
                WoundType.JUDGE: "Ember: 'You sort people. Good and bad. Worthy and unworthy. But people aren't that simple. And neither are you.'"
            }
        ),
        SceneBeat(
            beat_number=4,
            beat_name="THE QUESTION",
            description="Ember asks why - or asks if the player sees it too",
            narrative_text="Ember: 'Why? What are you so afraid of?'",
            archetype_variations={}
        ),
        SceneBeat(
            beat_number=5,
            beat_name="RESPONSE",
            description="Player can engage, deflect, or attack - crucial fork moment",
            narrative_text="This is a crucial fork moment. How you respond determines your path.",
            archetype_variations={}
        )
    ],
    npc_variations={
        "ember_ghost": {
            "naming_text": "Ember: 'You're not really here. You're... somewhere else. Already gone. Planning your exit. I've told you real things. About my life. My fears. Every time, you nod. And then you leave. Or change the subject. Or ask about the investigation. It's like you can't be present. Like presence is dangerous. Why? What are you so afraid of?'",
            "choices": [
                SceneChoice(
                    id="accept",
                    text="You're right. I don't know how to stay.",
                    is_growth_choice=True,
                    consequence="Acceptance. Hero signal. Path to growth opens.",
                    relationship_change=0.4
                ),
                SceneChoice(
                    id="deflect",
                    text="I'm here now, aren't I?",
                    archetype_signal=WoundType.GHOST,
                    consequence="Deflection. Ghost signal. Tragedy path.",
                    relationship_change=-0.2
                ),
                SceneChoice(
                    id="rationalize",
                    text="I'm focused on finding the truth. Everything else is distraction.",
                    archetype_signal=WoundType.CONTROLLER,
                    consequence="Rationalization. Tragedy signal.",
                    relationship_change=-0.3
                ),
                SceneChoice(
                    id="attack",
                    text="You're a kid. You don't understand anything.",
                    consequence="Rejection. Strong tragedy signal. Relationship severely damaged.",
                    relationship_change=-0.5
                ),
                SceneChoice(
                    id="vulnerable",
                    text="There was someone. Before. I lost them.",
                    is_growth_choice=True,
                    consequence="Vulnerability. Hero signal. Deep connection.",
                    relationship_change=0.5
                )
            ]
        }
    },
    archetype_integration={
        WoundType.GHOST: "Ember names the absence. The emotional distance. The inability to be present.",
        WoundType.CONTROLLER: "Ember names the need to control. The inability to trust. The fear of uncertainty.",
        WoundType.JUDGE: "Ember names the judgment. The sorting. The inability to see complexity."
    }
)

# ============================================================================
# SCENE REGISTRY AND HELPER FUNCTIONS
# ============================================================================

SCENE_REGISTRY: Dict[SceneType, SceneTemplate] = {
    SceneType.CRISIS_SYSTEM_FAILURE: CRISIS_SYSTEM_FAILURE,
    SceneType.CRISIS_CONFRONTATION: CRISIS_CONFRONTATION,
    SceneType.CRISIS_ACCUSATION: CRISIS_ACCUSATION,
    SceneType.QUIET_SHARED_SILENCE: QUIET_SHARED_SILENCE,
    SceneType.QUIET_CONFESSION: QUIET_CONFESSION,
    SceneType.QUIET_QUESTION: QUIET_QUESTION,
    SceneType.REVELATION_MIRROR: REVELATION_MIRROR,
    SceneType.REVELATION_COST: REVELATION_COST,
    SceneType.REVELATION_NAMING: REVELATION_NAMING
}

def get_scene_template(scene_type: SceneType) -> Optional[SceneTemplate]:
    """Get a specific scene template."""
    return SCENE_REGISTRY.get(scene_type)

def list_scene_types() -> List[Dict[str, Any]]:
    """List all available scene types with metadata."""
    return [
        {
            "scene_type": st.value,
            "name": template.name,
            "purpose": template.purpose,
            "category": st.value.split("_")[0]  # crisis, quiet, or revelation
        }
        for st, template in SCENE_REGISTRY.items()
    ]

def generate_scene_instance(
    scene_type: SceneType,
    player_archetype: WoundType,
    npc_id: Optional[str] = None,
    story_progress: float = 0.5,
    relationship_score: float = 0.0
) -> Dict[str, Any]:
    """
    Generate a specific scene instance based on current game state.
    
    Args:
        scene_type: Type of scene to generate
        player_archetype: Player's current dominant archetype
        npc_id: Optional specific NPC for NPC-variant scenes
        story_progress: Current story progress (0.0 to 1.0)
        relationship_score: Relationship score with relevant NPC
        
    Returns:
        Fully instantiated scene with dialogue, choices, and consequences
    """
    template = get_scene_template(scene_type)
    if not template:
        return {"error": "Scene type not found"}
    
    # Build the scene instance
    scene_instance = {
        "scene_type": scene_type.value,
        "name": template.name,
        "purpose": template.purpose,
        "player_archetype": player_archetype.value,
        "story_progress": story_progress,
        "beats": []
    }
    
    # Add beats with archetype-specific variations
    for beat in template.beats:
        beat_data = {
            "beat_number": beat.beat_number,
            "beat_name": beat.beat_name,
            "description": beat.description,
            "narrative_text": beat.narrative_text
        }
        
        # Add archetype-specific variation if available
        if player_archetype in beat.archetype_variations:
            beat_data["archetype_note"] = beat.archetype_variations[player_archetype]
        
        scene_instance["beats"].append(beat_data)
    
    # Add NPC-specific variation if requested and available
    if npc_id and npc_id in template.npc_variations:
        npc_var = template.npc_variations[npc_id]
        scene_instance["npc_variation"] = npc_id
        scene_instance["npc_data"] = npc_var
        
        # Add choices if available
        if "choices" in npc_var:
            scene_instance["choices"] = [
                {
                    "id": choice.id,
                    "text": choice.text,
                    "archetype_signal": choice.archetype_signal.value if choice.archetype_signal else None,
                    "consequence": choice.consequence,
                    "relationship_change": choice.relationship_change,
                    "is_growth_choice": choice.is_growth_choice
                }
                for choice in npc_var["choices"]
            ]
    
    # Add archetype integration notes
    if player_archetype in template.archetype_integration:
        scene_instance["archetype_guidance"] = template.archetype_integration[player_archetype]
    
    return scene_instance
