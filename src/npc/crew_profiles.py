"""
Crew Profiles for the NPC Mirroring System.
Defines the 6 main crew members with their deep moral arguments and psychological profiles.
"""

from src.psych_profile import NPCPsyche, MoralProfile, EmotionalState
from src.character_identity import WoundType

def create_yuki_profile() -> NPCPsyche:
    return NPCPsyche(
        name="Yuki Tanaka",
        dominant_trait="ruthless pragmatism",
        current_emotion=EmotionalState.DETERMINED,
        description="Security Officer (37). Professional, quiet, and reliable. Formerly a Corporate Enforcer for Helix Dynamics.",
        moral_profile=MoralProfile(
            central_problem_answer="There is no redemption, only what I can control.",
            strong_but_flawed_argument="Doing the right thing gets you destroyed. The system punishes honesty. I controlled the captain's death because I couldn't let his 'mercy' destroy the peace I spent three years building.",
            psychological_wound="Born on a Helix Dynamics colony; her father was destroyed by the system for being honest. She became the system's weapon before breaking after a whistleblower's suicide.",
            mirrors=[WoundType.CONTROLLER.value, WoundType.GHOST.value, WoundType.FUGITIVE.value, WoundType.CYNIC.value, WoundType.PARANOID.value],
            challenges=[WoundType.JUDGE.value, WoundType.SAVIOR.value],
            archetype_interactions={
                WoundType.CONTROLLER.value: "You understand control, don't you? The need to make sure nothing surprises you. I controlled his death. And now I control nothing. Funny how that works.",
                WoundType.GHOST.value: "You keep your distance too. You're always half-gone because close meant vulnerable, and vulnerable meant death. That's where your path leads. Total isolation.",
                WoundType.CYNIC.value: "You expect betrayal. I was like that. The captain said he wanted to help me, and I couldn't believe him. So I struck first. Now I'll never know if he was telling the truth.",
                WoundType.FUGITIVE.value: "We're both fugitives. The difference is I got caught. I tried to be Yuki Tanaka for three years. But Yuki Sato was always waiting under the skin.",
                WoundType.JUDGE.value: "You've decided about me already. But you don't even know why I did it. You want a monster? I've been one for twelve years. I know the shape of them better than you ever will."
            }
        )
    )

def create_torres_profile() -> NPCPsyche:
    return NPCPsyche(
        name="Torres",
        dominant_trait="skepticism",
        current_emotion=EmotionalState.SUSPICIOUS,
        description="The Pilot. Former military, court-martialed for disobeying orders to save lives. Reyes saw himself in her.",
        moral_profile=MoralProfile(
            central_problem_answer="Trust must be earned through action, not words. Most people fail.",
            strong_but_flawed_argument="I don't trust easily because trust gets people killed. You want me to open up? Show me you're worth it.",
            psychological_wound="Court-martialed for saving her squad against orders; Reyes gave her a second chance when the military abandoned her.",
            mirrors=[WoundType.CONTROLLER.value, WoundType.JUDGE.value, WoundType.CYNIC.value],
            challenges=[WoundType.MANIPULATOR.value, WoundType.NARCISSIST.value, WoundType.FLATTERER.value if hasattr(WoundType, 'FLATTERER') else "flatterer"],
            archetype_interactions={
                WoundType.CONTROLLER.value: "You need control. The captain needed it too. He couldn't leave anyone behind. That's what people loved about him. And that's what killed him.",
                WoundType.MANIPULATOR.value: "Save the speech. I don't care what you say. I care what you do.",
                WoundType.PARANOID.value: "You're checking the logs again? I checked them twice. If you don't trust my work, fly the ship yourself."
            }
        )
    )

def create_vasquez_profile() -> NPCPsyche:
    return NPCPsyche(
        name="Vasquez",
        dominant_trait="charm",
        current_emotion=EmotionalState.CONFIDENT,
        description="The Cargo Master. Criminal past; needed to disappear. Reyes believed in redemption for everyone.",
        moral_profile=MoralProfile(
            central_problem_answer="Connection is a tool. Be what people need you to be.",
            strong_but_flawed_argument="Everyone's selling something. I'm just honest about it. You need a friend on this ship? I can be that. What do you need?",
            psychological_wound="Abandoned as a child; learned that love is conditional on usefulness. Reyes was the first to offer a place without conditions.",
            mirrors=[WoundType.IMPOSTOR.value, WoundType.MANIPULATOR.value, WoundType.NARCISSIST.value],
            challenges=[WoundType.CYNIC.value, WoundType.GHOST.value, WoundType.JUDGE.value],
            archetype_interactions={
                WoundType.CYNIC.value: "You look like you're expecting a knife in the back. Relax, friend. I only stab people who don't pay.",
                WoundType.FUGITIVE.value: "We're all running from something, right? I can help you hide yours if you help me hide mine."
            }
        )
    )

def create_kai_profile() -> NPCPsyche:
    return NPCPsyche(
        name="Kai",
        dominant_trait="evasiveness",
        current_emotion=EmotionalState.ANXIOUS,
        description="Chief Engineer. Addiction issues; Reyes hoped the ship's structure would help him recover.",
        moral_profile=MoralProfile(
            central_problem_answer="Connection hurts too much. Escape the pain however you can.",
            strong_but_flawed_argument="You think I don't know I'm killing myself? I know. But you don't understand what it's like in here. The only peace I get is when I'm not feeling anything.",
            psychological_wound="Brilliant engineer blacklisted elsewhere; Reyes was the only one who'd hire him despite the addiction.",
            mirrors=[WoundType.FUGITIVE.value, WoundType.HEDONIST.value, WoundType.COWARD.value],
            challenges=[WoundType.JUDGE.value, WoundType.SAVIOR.value, WoundType.PERFECTIONIST.value],
            archetype_interactions={
                WoundType.SAVIOR.value: "The captain used to do that. Try to fix me. But some things aren't broken, they're just... empty.",
                WoundType.JUDGE.value: "Yeah, I screwed up. I always screw up. Put it in the report."
            }
        )
    )

def create_okonkwo_profile() -> NPCPsyche:
    return NPCPsyche(
        name="Dr. Okonkwo",
        dominant_trait="professional detachment",
        current_emotion=EmotionalState.TIRED,
        description="The Medic. Past medical scandal; Reyes offered her a second chance. She knew he was dying.",
        moral_profile=MoralProfile(
            central_problem_answer="Some truths must be kept to protect others. Distance is kindness.",
            strong_but_flawed_argument="You want to know everything? Some things break people. I've seen it. Sometimes mercy is silence.",
            psychological_wound="Lost her license in a scandal; Reyes didn't care about her past, only her skills. She was the one who diagnosed him.",
            mirrors=[WoundType.GHOST.value, WoundType.MARTYR.value, WoundType.CONTROLLER.value],
            challenges=[WoundType.PEDANT.value, WoundType.CONTROLLER.value, WoundType.FUGITIVE.value],
            archetype_interactions={
                WoundType.CONTROLLER.value: "I saw it in Marcus. The need to settle everything before the end. You can't control the outcome, even if you know the diagnosis.",
                WoundType.PEDANT.value: "Life isn't a textbook case. Diagnosis is easy. Living with the treatment is the hard part.",
                WoundType.FUGITIVE.value: "You have that look. The one that says 'I shouldn't be here.' What happened before you came aboard?"
            }
        )
    )

def create_ember_profile() -> NPCPsyche:
    return NPCPsyche(
        name="Ember",
        dominant_trait="observant authenticity",
        current_emotion=EmotionalState.HOPEFUL,
        description="The Apprentice. Stowaway runaway; Reyes would have mentored her if he'd lived.",
        moral_profile=MoralProfile(
            central_problem_answer="Connection is the only thing that matters. Everything else is just waiting to die.",
            strong_but_flawed_argument="I don't understand why everyone lies so much. Not big lies. Just... constant little ones. What are you all so afraid of?",
            psychological_wound="Escaped indentured servitude; Reyes saved her from the docks and gave her a home. She heard him talking to Maria's memory.",
            mirrors=[], # Ember doesn't mirror, she reveals
            challenges=[t.value for t in WoundType], # She challenges ALL archetypes
            archetype_interactions={
                WoundType.CONTROLLER.value: "The Captain collected us like broken parts. But he always knew how we fit together. Do you?",
                WoundType.JUDGE.value: "You decided about Yuki already. But you don't even know why she did it.",
                WoundType.GHOST.value: "You never talk about yourself. It's like you're not really here.",
                WoundType.FUGITIVE.value: "What happened before you came here? You never say.",
                WoundType.CYNIC.value: "You expect everyone to be bad. Doesn't that get exhausting?",
                WoundType.IMPOSTOR.value: "You're different with everyone. Which one is you?"
            }
        )
    )

CREW_PROFILES = {
    "yuki": create_yuki_profile(),
    "torres": create_torres_profile(),
    "vasquez": create_vasquez_profile(),
    "kai": create_kai_profile(),
    "okonkwo": create_okonkwo_profile(),
    "ember": create_ember_profile()
}
