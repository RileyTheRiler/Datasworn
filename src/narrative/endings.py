"""
Hero/Tragedy Fork System

This module manages the final narrative fork of the game, determining the ending
based on the player's archetype and their moral decision (Accept or Reject).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, List

class EndingType(str, Enum):
    HERO = "hero"
    TRAGEDY = "tragedy"

class EndingStage(str, Enum):
    DECISION = "decision"
    TEST = "test"  # Growth (Hero) or Doubling Down (Tragedy)
    RESOLUTION = "resolution"  # Resolution (Hero) or Catastrophe (Tragedy)
    WISDOM = "wisdom"
    FINAL_SCENE = "final_scene"

@dataclass
class EndingScenario:
    """container for the narrative beats of a specific ending path."""
    moral_question: str
    decision_options: Dict[str, str]  # e.g., {"accept": "Description...", "reject": "Description..."}
    
    # Hero Path
    hero_decision: str
    hero_test: str
    hero_resolution: str
    hero_wisdom: str
    hero_final_scene: str
    
    # Tragedy Path
    tragedy_decision: str
    tragedy_doubling_down: str
    tragedy_catastrophe: str
    tragedy_wisdom: str
    tragedy_final_scene: str

class EndingOrchestrator:
    """Orchestrates the ending sequence based on archetype and choice."""
    
    def __init__(self):
        self.scenarios = self._initialize_scenarios()
        
    def get_decision_prompt(self, archetype: str) -> dict:
        """Returns the moral decision prompt for the given archetype."""
        scenario = self.scenarios.get(archetype.lower())
        if not scenario:
            return self._get_fallback_decision()
            
        return {
            "question": scenario.moral_question,
            "options": scenario.decision_options
        }
        
    def process_decision(self, archetype: str, choice: str) -> EndingType:
        """
        Determines the ending type based on the player's choice.
        'choice' should be the key from decision_options (e.g. 'accept', 'reject', 'partial').
        """
        if choice.lower() in ["accept", "hero", "growth"]:
            return EndingType.HERO
        return EndingType.TRAGEDY

    def get_narrative_beat(self, archetype: str, ending_type: EndingType, stage: EndingStage) -> str:
        """Returns the specific text for a stage of the ending."""
        scenario = self.scenarios.get(archetype.lower())
        if not scenario:
            return f"Generic {ending_type.value} ending for {archetype} at {stage.value}."
            
        if ending_type == EndingType.HERO:
            if stage == EndingStage.DECISION: return scenario.hero_decision
            if stage == EndingStage.TEST: return scenario.hero_test
            if stage == EndingStage.RESOLUTION: return scenario.hero_resolution
            if stage == EndingStage.WISDOM: return scenario.hero_wisdom
            if stage == EndingStage.FINAL_SCENE: return scenario.hero_final_scene
            
        else: # TRAGEDY
            if stage == EndingStage.DECISION: return scenario.tragedy_decision
            if stage == EndingStage.TEST: return scenario.tragedy_doubling_down
            if stage == EndingStage.RESOLUTION: return scenario.tragedy_catastrophe
            if stage == EndingStage.WISDOM: return scenario.tragedy_wisdom
            if stage == EndingStage.FINAL_SCENE: return scenario.tragedy_final_scene
            
        return ""

    def _get_fallback_decision(self) -> dict:
        return {
            "question": "The Final Choice",
            "options": {
                "accept": "Accept the truth and grow.",
                "reject": "Reject the truth and remain the same."
            }
        }

    def to_dict(self) -> dict:
        """Serialize state (stateless for now, but good practice)."""
        return {}

    @classmethod
    def from_dict(cls, data: dict) -> "EndingOrchestrator":
        return cls()

    def _initialize_scenarios(self) -> Dict[str, EndingScenario]:
        return {
            "controller": EndingScenario(
                moral_question="What happens to Yuki?",
                decision_options={
                    "accept": "Let the crew decide together (Surrender control)",
                    "reject": "Impose your own judgment (Maintain control)",
                    "avoid": "Give Yuki to authorities (Avoid decision)"
                },
                hero_decision="You choose to let the crew decide together. You present the evidence and step back, honoring Reyes's belief that 'people save people, not systems.'",
                hero_test="The crew argues. Torres wants punishment. Dr. Okonkwo advocates for mercy. Kai is uncertain. You must sit with the discomfort of not controlling the outcome, just as Marcus had to when he invited this crew aboard.",
                hero_resolution="The crew reaches a decision—imperfect, human, but theirs. You realize: the outcome wasn't what you would have chosen, but it was right because it was collective. You've honored the captain's legacy of second chances.",
                hero_wisdom="I am not the law that judges; I am the mirror that must be clean to see the truth. The outcome wasn't what I would have chosen, but it was right because it was collective. Control was a distance I kept from the living. Marcus knew: we only survive if we trust each other to hold the line.",
                hero_final_scene="The ship's reactor hums rhythmically, a sound you once found aggravating but now find comforting. You sit with the crew, no longer watching them for protocol violations. You look at the captain's empty chair and finally understand—he didn't leave a vacancy, he left a family.",
                tragedy_decision="You impose your own judgment—you become the 'system' Marcus tried to escape. You decide Yuki's fate without the crew.",
                tragedy_doubling_down="The crew resists. Torres challenges: 'Who made you the judge? You're acting just like the corporate systems Marcus hated.' The player insists. They need this to be decided their way.",
                tragedy_catastrophe="The forced outcome creates fractures. The crew turns on each other. You've technicaly 'solved' the murder, but you've destroyed the crew Marcus built. You are the captain of an empty ship.",
                tragedy_wisdom="I held everything so tight. The investigation. The judgment. The outcome. And when I squeezed, it shattered. Marcus tried to tell me: systems don't save people. I tried to be the system. I failed them. I failed him.",
                tragedy_final_scene="You stand over consequences you created. The crew won't look at you. You are alone in the command chair, surrounded by metrics and certainty, and absolutely nothing else."
            ),
            "judge": EndingScenario(
                moral_question="Can you forgive Yuki?",
                decision_options={
                    "accept": "Advocate for mercy/understanding (Accept complexity)",
                    "reject": "Condemn without reservation (Maintain binary morality)",
                    "demand": "Demand Yuki justify herself (Seek understanding via judgment)"
                },
                hero_decision="You advocate for understanding. Not forgiveness exactly, but humanity. You acknowledge Yuki's crime while seeing her as a person.",
                hero_test="Torres challenges: 'She's a murderer.' You must articulate why complexity matters—not to excuse, but to understand. You believed in justice. Now you must believe in something more nuanced.",
                hero_resolution="The crew doesn't forgive Yuki, but they don't demonize her either. She's confined, but treated humanely. You realize: mercy isn't weakness. It's the hardest kind of strength.",
                hero_wisdom="I wanted a monster. Someone I could condemn without doubt. But there are no monsters. Only humans who made terrible choices. Justice isn't about sorting people into boxes. It's about seeing them clearly—and choosing compassion anyway.",
                hero_final_scene="You visit Yuki in confinement. Not to condemn or forgive. Just to see her. To acknowledge her humanity. Yuki looks up. 'I didn't expect you.' 'Neither did I.'",
                tragedy_decision="You condemn Yuki absolutely. No nuance. No mercy. She is guilty, she is evil, she must be punished.",
                tragedy_doubling_down="You push for harsh punishment. Torres is uncomfortable. Ember asks: 'What if it was me?' You dismiss the doubts. Justice must be served.",
                tragedy_catastrophe="In pushing for condemnation, a secret emerges: your own past crime. Vasquez exposes it. 'You want to condemn Yuki? Let's talk about what you did.' Your moral authority collapses.",
                tragedy_wisdom="I built a world of monsters and victims. I was the righteous judge. But I was lying. The monster I was hunting was always inside me. I condemned Yuki. But I was condemning myself all along.",
                tragedy_final_scene="The crew knows your secret now. The moral high ground is gone. You stand alone, judged by the same standard you applied to everyone else. You wanted a world of clear categories. You got one. And you're on the wrong side of it."
            ),
            "ghost": EndingScenario(
                moral_question="Will you stay?",
                decision_options={
                    "accept": "Stay with the crew (Accept attachment)",
                    "reject": "Leave at port (Continue the pattern)",
                    "distance": "Stay but maintain distance (Half-measure)"
                },
                hero_decision="You choose to stay. Not because it's safe—it isn't. But because these people matter.",
                hero_test="Ember asks: 'You're staying? Really?' You must say yes. And mean it. Which means risking everything you've been avoiding.",
                hero_resolution="You allow connection to happen. You share something real with Ember. You sit with Kai. You will lose some of these people eventually. But you will have had them.",
                hero_wisdom="I've been leaving before anyone could leave me. But distance isn't protection. It's just slower death. These people—broken, flawed, temporary—they're alive. And for the first time in years, so am I.",
                hero_final_scene="You sit with Ember watching the stars. Not talking about anything important. Just being present. The ship continues into the unknown. But you're not alone.",
                tragedy_decision="You leave at port. New ship, new crew, continue the pattern.",
                tragedy_doubling_down="Ember asks you to stay. Kai says they need you. Even Torres admits you belong here. You leave anyway. It's easier. Safer.",
                tragedy_catastrophe="Time passes. You hear news: Kai overdosed. Without the connection, he spiraled. Ember was with him at the end. She's closed off now. You created another ghost.",
                tragedy_wisdom="I left to protect myself from loss. But I didn't prevent loss. I caused it. I was running so fast I didn't notice I was the someone they needed. I died slowly to avoid dying all at once. And I took them with me.",
                tragedy_final_scene="You are on a new ship. New faces. New crew. Already planning the exit. You are surrounded by people. You are completely alone. The ghost continues."
            ),
            "fugitive": EndingScenario(
                moral_question="Will you confess?",
                decision_options={
                    "accept": "Confess to the crew (Stop running)",
                    "reject": "Keep the secret (Continue running)",
                    "partial": "Confess to one person only (Half-measure)"
                },
                hero_decision="You confess. To the whole crew, or to the one person who matters most. You tell the truth about who you were, what you did.",
                hero_test="The crew reacts. Some with anger. Some with understanding. Torres: 'I've got my own past.' You must endure the judgment without running.",
                hero_resolution="You're not forgiven immediately. But you're not destroyed. The truth is out. The running stops. You can finally start to build something.",
                hero_wisdom="I ran for so long I forgot what I was running from. It was always me. But shame can't be outrun. It can only be faced. I stopped. I turned around. And the monster was just... a person who made a mistake.",
                hero_final_scene="You walk the corridors. You pass Ember, who nods. Torres, who grunts acknowledgment. Dr. Okonkwo asks, 'How do you feel?' '...Light.'",
                tragedy_decision="You keep the secret. Let Yuki take the spotlight. Stay hidden.",
                tragedy_doubling_down="Secrets leak. Vasquez knows something. Or your behavior reveals you. The truth starts to surface despite your efforts.",
                tragedy_catastrophe="The secret comes out through exposure, not confession. The crew feels betrayed by the lying. Ember: 'You judged Yuki for lying. You did the same thing.' You lose everything.",
                tragedy_wisdom="I ran so far I forgot what I was running from. It caught up anyway. And now I've lost not just my past, but my future. The only thing worse than facing the truth is refusing to—and having it find you anyway.",
                tragedy_final_scene="You pack your bag. You're leaving—again. But this time there's no relief in it. Just more running. The past will catch up again. It always does."
            ),
            "cynic": EndingScenario(
                moral_question="Will you trust?",
                decision_options={
                    "accept": "Accept the trust (Believe in connection)",
                    "reject": "Reject it (Maintain defenses)",
                    "test": "Test it (Demand proof)"
                },
                hero_decision="You accept the offered connection. You believe it. You let someone in.",
                hero_test="The vulnerability feels dangerous. Your instincts scream: find the angle, protect yourself. But you sit with it. You trust.",
                hero_resolution="The person doesn't betray you. The connection holds. It's fragile, imperfect, but real. You learn: not everyone betrays. Trust is a choice, and it can be rewarded.",
                hero_wisdom="I spent so long waiting for betrayal that I couldn't see anything else. I built walls so high I couldn't see over them. The walls weren't keeping danger out—they were keeping me in. Someone offered their hand. I took it. And I didn't fall.",
                hero_final_scene="You sit with Ember or Vasquez. Talking. Laughing, maybe. The conversation isn't special. But it's real. And for the first time in years, you aren't waiting for the other shoe to drop.",
                tragedy_decision="You reject the offered trust. Assume the angle. Push away.",
                tragedy_doubling_down="The person tries again. You push harder. Insult, accuse, create distance. Eventually, the person stops trying.",
                tragedy_catastrophe="Later, you discover: the person was genuine. There was no angle. But by then, it's too late. The connection is damaged. You were right to expect betrayal—because you created it.",
                tragedy_wisdom="I was right about everyone. I made sure of it. Every hand extended, I slapped away. And now I'm alone. Safe. Right. But being right doesn't keep you warm. I built this cage myself. And I'll die in it.",
                tragedy_final_scene="You sit alone in your quarters. The ship is full of people. Laughter elsewhere. You hear it through the walls. You are completely, perfectly alone."
            ),
            "savior": EndingScenario(
                moral_question="Will you let them save themselves?",
                decision_options={"accept": "Let go", "reject": "Hold on"},
                hero_decision="You let Kai and Ember face their own demons. You handle the fear of them failing.",
                hero_test="Sitting with helplessness. Supporting without fixing.",
                hero_resolution="They grow stronger independently. You learn to walk beside them, not carry them.",
                hero_wisdom="I can't save everyone. I can only walk beside them.",
                hero_final_scene="You watch them handle a problem without looking at you for approval.",
                tragedy_decision="You intervene. You keep 'saving' them against their will.",
                tragedy_doubling_down="You insist you know what's best. You disable their agency.",
                tragedy_catastrophe="They become dependent or resentful. You've made them weak to feel strong.",
                tragedy_wisdom="I needed them to need me. I made them weak to feel strong.",
                tragedy_final_scene="They look to you for everything. You are exhausted and they are hollow."
            ),
            "destroyer": EndingScenario(
                moral_question="Will you build or burn?",
                decision_options={"accept": "Protect", "reject": "Burn"},
                hero_decision="You channel your anger into protection, not destruction.",
                hero_test="The urge to lash out arises. You defend someone instead of attacking.",
                hero_resolution="Anger becomes purpose. You become a guardian.",
                hero_wisdom="Anger can fuel building, not just burning.",
                hero_final_scene="You stand guard. The fire inside keeps them warm, not burnt.",
                tragedy_decision="You continue burning. It's all you know.",
                tragedy_doubling_down="You destroy one more thing. A relationship. A hope.",
                tragedy_catastrophe="There is nothing left to destroy but yourself.",
                tragedy_wisdom="I made rubble of everything. Nothing grows in ash.",
                tragedy_final_scene="You stand amidst the ashes of your connections."
            ),
            "impostor": EndingScenario(
                moral_question="Will you show your real self?",
                decision_options={"accept": "Reveal", "reject": "Mask"},
                hero_decision="You show the real self to someone. No performance.",
                hero_test="Being seen without the mask. The terror of being 'found out'.",
                hero_resolution="Someone sees the real you and stays. The exhaustion ends.",
                hero_wisdom="I am enough without the performance.",
                hero_final_scene="You are silent with someone, and it's comfortable.",
                tragedy_decision="You maintain the mask. The role is safer.",
                tragedy_doubling_down="You double down on the performance. You become the role completely.",
                tragedy_catastrophe="The mask becomes a prison. You forget who you were underneath.",
                tragedy_wisdom="I became everyone's version. There was no one underneath.",
                tragedy_final_scene="Everyone applauds the performance. You are not there to hear it."
            ),
            "paranoid": EndingScenario(
                moral_question="Will you lower your shield?",
                decision_options={"accept": "Trust", "reject": "Strike"},
                hero_decision="You trust someone despite the fear.",
                hero_test="Vulnerability with a suspected person. Waiting for the knife that doesn't come.",
                hero_resolution="They didn't betray. Trust builds. The world becomes less hostile.",
                hero_wisdom="Not everyone is a threat. Fear made them seem so.",
                hero_final_scene="You sleep without one eye open.",
                tragedy_decision="You preemptively strike against an imagined threat.",
                tragedy_doubling_down="You create the danger you feared.",
                tragedy_catastrophe="They become an enemy because you made them one.",
                tragedy_wisdom="I saw enemies everywhere. In the end, I made them all.",
                tragedy_final_scene="You are safe, armed, and surrounded by enemies of your own making."
            ),
            "perfectionist": EndingScenario(
                moral_question="Can you accept the broken pieces?",
                decision_options={"accept": "Accept", "reject": "Perfect"},
                hero_decision="You accept an imperfect solution.",
                hero_test="Letting something be 'good enough'. Tolerating the flaw.",
                hero_resolution="You find beauty in the flaws. You find peace.",
                hero_wisdom="Perfect is the enemy of real.",
                hero_final_scene="You look at the patched ship/crew. It's ugly. It's beautiful.",
                tragedy_decision="You demand the impossible. It must be right.",
                tragedy_doubling_down="You destroy what's adequate seeking what's perfect.",
                tragedy_catastrophe="Nothing meets the standard. You are left with nothing.",
                tragedy_wisdom="I made perfection a god. I sacrificed everyone at its altar.",
                tragedy_final_scene="You sit in a perfect, empty room."
            )
        }

# Backward compatibility alias
EndingPreparationSystem = EndingOrchestrator
