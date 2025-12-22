"""
Specific Interrogation Scenes.

Features:
- Torres: Requires respect/patience.
- Vasquez: Requires seeing through charm/misdirection.
- Kai: Requires gentle approach/safety.
- Dr. Okonkwo: Requires ethical maturity.
- Ember: Requires genuine connection/listening.
- Yuki: The final confrontation.
"""

from src.narrative.interrogation import (
    InterrogationScene, InterrogationNode, InterrogationChoice, InterrogationSignal
)

# --- IMPORT PROFILES ---
from src.npc.crew_profiles import CREW_PROFILES

# --- TORRES INTERROGATION ---
class TorresInterrogation(InterrogationScene):
    def __init__(self):
        super().__init__()
        self.npc_id = "pilot" # Correctly mapped to Pilot/Torres
        self.start_node_id = "start"
        self.profile = CREW_PROFILES["torres"]
        
    def build_graph(self):
        # Nodes
        self.nodes["start"] = InterrogationNode(
            id="start",
            npc_text=f"[Torres is running diagnostics on the bridge.]\n\n'Something you need? I'm busy.'",
            choices=[
                InterrogationChoice(
                    id="demanding",
                    text="I need to know what you saw. Don't deny it.",
                    next_node_id="shut_down",
                    signals=[InterrogationSignal.CONTROLLER],
                    trust_change=-0.2
                ),
                InterrogationChoice(
                    id="manipulative",
                    text="Torres, you're the most observant person here. Help me out.",
                    next_node_id="seen_through",
                    signals=[InterrogationSignal.MANIPULATOR],
                    trust_change=-0.1
                ),
                InterrogationChoice(
                    id="transactional",
                    text="I'm trying to find out what happened. What would it take for you to talk?",
                    next_node_id="transaction",
                    signals=[InterrogationSignal.PRAGMATIC],
                    trust_change=0.0
                ),
                InterrogationChoice(
                    id="vulnerable",
                    text="I'm out of my depth. I don't know who to trust.",
                    next_node_id="crack_open",
                    signals=[InterrogationSignal.RESILIENT, InterrogationSignal.GROWTH],
                    trust_change=0.1
                )
            ]
        )
        
        self.nodes["shut_down"] = InterrogationNode(
            id="shut_down",
            npc_text="'You want info? Earn it. Don't demand it.'",
            is_terminal=True
        )
        
        self.nodes["seen_through"] = InterrogationNode(
            id="seen_through",
            npc_text="'Flattery? Really? I've been manipulated by pros. Try again.'",
            is_terminal=True
        )

        self.nodes["transaction"] = InterrogationNode(
            id="transaction",
            npc_text=f"'{self.profile.moral_profile.central_problem_answer} Show me who you are with actions.'",
            is_terminal=True
        )
        
        self.nodes["crack_open"] = InterrogationNode(
            id="crack_open",
            npc_text=f"'That's... surprisingly honest. {self.profile.moral_profile.strong_but_flawed_argument}'",
            is_terminal=True
        )

# --- VASQUEZ INTERROGATION ---
class VasquezInterrogation(InterrogationScene):
    def __init__(self):
        super().__init__()
        self.npc_id = "cargo" # Correctly mapped to Vasquez/Cargo
        self.start_node_id = "start"
        self.profile = CREW_PROFILES["vasquez"]

    def build_graph(self):
        self.nodes["start"] = InterrogationNode(
            id="start",
            npc_text=f"[Vasquez is in the cargo bay.]\n\n'Well, look who's visiting. Come to admire my organizational skills?'",
            choices=[
                InterrogationChoice(
                    id="direct",
                    text="Cut the charm. What's in the crate?",
                    next_node_id="deflection",
                    signals=[InterrogationSignal.CONTROLLER],
                    trust_change=-0.1
                ),
                InterrogationChoice(
                    id="play_along",
                    text="You've got the best read on the crew. What's your take?",
                    next_node_id="misdirection",
                    signals=[InterrogationSignal.MANIPULATOR],
                    trust_change=0.0
                )
            ]
        )

        self.nodes["deflection"] = InterrogationNode(
            id="deflection",
            npc_text="'Wow, straight to accusations. It's ship supplies.' [He gestures to the wrong crate.]",
            is_terminal=True
        )

        self.nodes["misdirection"] = InterrogationNode(
            id="misdirection",
            npc_text=f"'Smart question. {self.profile.moral_profile.strong_but_flawed_argument}'",
            is_terminal=True
        )

# --- KAI INTERROGATION ---
class KaiInterrogation(InterrogationScene):
    def __init__(self):
        super().__init__()
        self.npc_id = "engineer"
        self.start_node_id = "start"
        self.profile = CREW_PROFILES["kai"]
    
    def build_graph(self):
        self.nodes["start"] = InterrogationNode(
            id="start",
            npc_text="[Kai jumps when you enter.] 'Oh—hey. You need something?'",
            choices=[
                InterrogationChoice(
                    id="accusatory",
                    text="You were on duty. What happened?",
                    next_node_id="shut_down",
                    signals=[InterrogationSignal.JUDGE],
                    trust_change=-0.2
                ),
                InterrogationChoice(
                    id="sympathetic",
                    text="Kai, you look exhausted. Is everything okay?",
                    next_node_id="opening",
                    signals=[InterrogationSignal.SAVIOR],
                    trust_change=0.1
                )
            ]
        )
        
        self.nodes["shut_down"] = InterrogationNode(
            id="shut_down",
            npc_text=f"'Nothing went wrong! {self.profile.moral_profile.central_problem_answer}'",
            is_terminal=True
        )

        self.nodes["opening"] = InterrogationNode(
            id="opening",
            npc_text=f"'I... no. {self.profile.moral_profile.strong_but_flawed_argument}'",
            is_terminal=True
        )

# --- DR. OKONKWO INTERROGATION ---
class OkonkwoInterrogation(InterrogationScene):
    def __init__(self):
        super().__init__()
        self.npc_id = "medic"
        self.start_node_id = "start"
        self.profile = CREW_PROFILES["okonkwo"]

    def build_graph(self):
        self.nodes["start"] = InterrogationNode(
            id="start",
            npc_text="'Can I help you with something medical? Or is this about the captain?'",
            choices=[
                InterrogationChoice(
                    id="demand_autopsy",
                    text="I need the full autopsy report. Unredacted.",
                    next_node_id="refusal",
                    signals=[InterrogationSignal.CONTROLLER],
                    trust_change=-0.1
                ),
                InterrogationChoice(
                    id="ethics",
                    text="Someone killed him. Don't you think he deserves justice?",
                    next_node_id="testing",
                    signals=[InterrogationSignal.JUDGE],
                    trust_change=0.0
                )
            ]
        )

        self.nodes["refusal"] = InterrogationNode(
            id="refusal",
            npc_text=f"'{self.profile.moral_profile.central_problem_answer} Give me a better reason.'",
            is_terminal=True
        )

        self.nodes["testing"] = InterrogationNode(
            id="testing",
            npc_text=f"'{self.profile.moral_profile.strong_but_flawed_argument}'",
            is_terminal=True
        )

# --- EMBER INTERROGATION ---
class EmberInterrogation(InterrogationScene):
    def __init__(self):
        super().__init__()
        self.npc_id = "apprentice" # Correctly mapped to Ember
        self.start_node_id = "start"
        self.profile = CREW_PROFILES["ember"]
    
    def build_graph(self):
        self.nodes["start"] = InterrogationNode(
            id="start",
            npc_text="[Ember is watching the stars.] 'Did you ever wonder what's out there?'",
            choices=[
                InterrogationChoice(
                    id="business",
                    text="Ember, I need to ask you questions.",
                    next_node_id="fail",
                    signals=[InterrogationSignal.CONTROLLER],
                    trust_change=0.0
                ),
                InterrogationChoice(
                    id="join",
                    text="[Sit quietly] The nothing. Yeah.",
                    next_node_id="connection",
                    signals=[InterrogationSignal.RESILIENT],
                    trust_change=0.1
                )
            ]
        )

        self.nodes["fail"] = InterrogationNode(
            id="fail",
            npc_text=f"'Oh. That's what this is. {self.profile.moral_profile.strong_but_flawed_argument}'",
            is_terminal=True
        )

        self.nodes["connection"] = InterrogationNode(
            id="connection",
            npc_text=f"[She smiles.] '{self.profile.moral_profile.central_problem_answer}'",
            is_terminal=True
        )


# --- YUKI CONFRONTATION ---
class YukiConfrontation(InterrogationScene):
    def __init__(self):
        super().__init__()
        self.npc_id = "security" # Correctly mapped to Yuki
        self.start_node_id = "start"
        self.profile = CREW_PROFILES["yuki"]

    def build_graph(self):
        self.nodes["start"] = InterrogationNode(
            id="start",
            npc_text="[Yuki listens to your evidence.] 'Do you? Do you really know what I did?'",
            choices=[
                InterrogationChoice(
                    id="confront_moral",
                    text="You killed a dying man. Why?",
                    next_node_id="confession",
                    signals=[InterrogationSignal.JUDGE],
                    trust_change=0.0
                )
            ]
        )

        self.nodes["confession"] = InterrogationNode(
            id="confession",
            npc_text=f"'Yes. I killed him. {self.profile.moral_profile.strong_but_flawed_argument}'",
            choices=[
                InterrogationChoice(
                    id="decision_hero",
                    text="Turn yourself in. It's the only way to make this right.",
                    next_node_id="end_hero",
                    signals=[InterrogationSignal.JUDGE, InterrogationSignal.SAVIOR],
                    trust_change=0.0
                ),
                InterrogationChoice(
                    id="decision_tragedy",
                    text="We can keep this secret. The crew doesn't need to know.",
                    next_node_id="end_tragedy",
                    signals=[InterrogationSignal.MANIPULATOR, InterrogationSignal.GHOST],
                    trust_change=0.0
                )
            ]
        )
        
        self.nodes["end_hero"] = InterrogationNode(
            id="end_hero",
            npc_text="'Maybe you're right. Maybe it's time to stop running.'",
            is_terminal=True
        )

        self.nodes["end_tragedy"] = InterrogationNode(
            id="end_tragedy",
            npc_text="'A pact, then. Silence for silence. But this will eat at you.'",
            is_terminal=True
        )

# Factory to get them easily
def get_interrogation_scene(scene_name: str) -> InterrogationScene:
    mapping = {
        "torres": TorresInterrogation(),
        "vasquez": VasquezInterrogation(),
        "kai": KaiInterrogation(),
        "okonkwo": OkonkwoInterrogation(),
        "ember": EmberInterrogation(),
        "yuki": YukiConfrontation()
    }
    return mapping.get(scene_name.lower())
