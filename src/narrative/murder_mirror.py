"""
The Murder Solution Mirror.
Handles the logic for the final confrontation with Yuki, where the player's understanding of the murder
mirrors their own psychological wound.
"""

from typing import Dict, TypedDict
from src.character_identity import WoundType

class MirrorContent(TypedDict):
    what_mirror_shows: str
    parallel: str
    revelation_moment: str
    question_for_player: str

# Defined mirror content for each archetype based on the design doc
MIRROR_DATA: Dict[WoundType, MirrorContent] = {
    WoundType.CONTROLLER: {
        "what_mirror_shows": "Yuki killed because she couldn't tolerate the uncertainty of an uncontrolled outcome.",
        "parallel": "The player has been trying to control every variable of the investigation and the crew.",
        "revelation_moment": (
            "You understand control, don't you? The need to make sure nothing surprises you. That every variable is accounted for. "
            "I've watched you this whole investigation. You didn't just want the truth—you wanted to own it. "
            "You wanted to decide what happened next. I was the same.\n\n"
            "The captain gave me a choice: confess and let the crew decide, or he'd expose me at port. "
            "Maria used to tell him he was too controlling—always trying to save people they didn't ask to be saved. "
            "I couldn't let them decide. I couldn't accept the uncertainty. So I ended it. "
            "I controlled his death, and now... I control nothing. Can you let go, Captain? Or do you need to control this judgment too?"
        ),
        "question_for_player": "Can you let go of control now? Can you let the crew decide Yuki's fate—or must you impose your own certainty?"
    },
    WoundType.JUDGE: {
        "what_mirror_shows": "Yuki's 'monster' status is a mask created by years of corporate enforcement.",
        "parallel": "The player has been using moral judgment as a shield against their own complexity.",
        "revelation_moment": (
            "Go ahead. Condemn me. That's what you do, isn't it? Put people in boxes. Guilty, innocent. Monster, victim.\n\n"
            "I was the system's weapon for twelve years. I know the shape of monsters because I was one for the people who pay the credits. "
            "The captain saw through that. He saw a person. And that terrified me more than any prison. "
            "I killed him because he made me feel human, and I didn't know how to be that anymore.\n\n"
            "You want a simple monster to judge? I can be that for you. But you know it's more complicated. You just don't want to admit it."
        ),
        "question_for_player": "Can you judge the human underneath the crime? Or do you need her to be a monster to keep your own world simple?"
    },
    WoundType.GHOST: {
        "what_mirror_shows": "Yuki killed to maintain her emotional isolation.",
        "parallel": "The player has been keeping everyone at arm's length to avoid the pain of connection.",
        "revelation_moment": (
            "You keep your distance too. I see it. The way you walk through these halls like you're already gone. "
            "You think distance is safety. You think if you don't belong to them, they can't hurt you when you lose them.\n\n"
            "I was a Ghost for Helix for twelve years. I ghosted my way right into this murder. "
            "I couldn't let him in. I couldn't let anyone get close enough to see the cracks. "
            "And look where it ends. Total isolation. You're halfway there already. Is that what you want? "
            "To be so safe that you're practically dead?"
        ),
        "question_for_player": "Are you willing to be seen, with all your cracks? Or will you finish the journey I started?"
    },
    WoundType.FUGITIVE: {
        "what_mirror_shows": "Yuki killed to keep her past as a corporate enforcer buried.",
        "parallel": "The player is running from their own history and identity.",
        "revelation_moment": (
            "I spent three years as 'Yuki Tanaka', pretending the corporate enforcer named Sato was dead. "
            "The captain looked at me and saw both. He knew about the blacklisting, the way I was discarded by the system. "
            "He wanted me to face what I'd done. He wanted the running to stop. 'Settle your accounts, Yuki,' he said. 'Before the systems decide for you.'\n\n"
            "I couldn't face it. I couldn't stand there while everyone learned who I really was. "
            "So I killed the witness. I killed the only one who saw the truth.\n\n"
            "But you can't kill the truth, can you? It's still there, waiting. Under your skin, just like mine. "
            "We're both fugitives. The difference is I got caught."
        ),
        "question_for_player": "Can you stop running? Can you face the person you were before you stepped onto this ship?"
    },
    WoundType.CYNIC: {
        "what_mirror_shows": "Yuki killed because she couldn't believe the captain's offer of mercy was genuine.",
        "parallel": "The player assumes the worst of everyone to protect themselves from betrayal.",
        "revelation_moment": (
            "You expect betrayal. From everyone. You've been waiting for the knife since you stepped on this ship. "
            "I was the same. When the captain offered me a second chance—a way out of the corporate shadow—I didn't see mercy.\n\n"
            "I saw a cage. I saw a trap. I thought he was using my past to control me. So I struck first.\n\n"
            "And now... I'll never know if he was telling the truth. I killed the only person who actually believed I could be more than a weapon. "
            "That's the price of being right, isn't it? You get to be right, and you get to be alone."
        ),
        "question_for_player": "What if you're wrong? What if the person you're suspecting actually cares about you?"
    },
    WoundType.SAVIOR: {
        "what_mirror_shows": "Yuki couldn't let anyone help her. The captain tried. She killed him for it.",
        "parallel": "The player has been trying to save everyone. Yuki shows that you can't save someone who won't be saved.",
        "revelation_moment": (
            "The captain wanted to save me. Redeem me. Give me a chance at a new life. Noble, right? "
            "He thought if he could save a corporate monster like Sato, he could finally prove Maria wrong—that people save people, "
            "not the systems. Not even the captain's own 'system' of second chances.\n\n"
            "But I didn't ask to be saved. I didn't want his mercy. And when he forced it on me anyway—forced me to choose confession or exposure—I chose a third option.\n\n"
            "[Looks at the player]\n\n"
            "You've been trying to save everyone too. Kai. That kid, Ember. Even me, maybe. "
            "But here's the truth: we don't all want to be saved. And sometimes, trying to save someone is just another way of controlling them."
        ),
        "question_for_player": "Can you let people save themselves? Can you step back and trust others to find their own way?"
    },
    WoundType.DESTROYER: {
        "what_mirror_shows": "Yuki destroyed her chance at redemption. She burned the bridge the captain was building.",
        "parallel": "The player has been expressing anger through destruction. Yuki shows what pure destruction leads to.",
        "revelation_moment": (
            "I was so angry. At the company. At the captain for threatening me. At myself for what I'd done. "
            "The anger was the only thing that felt real.\n\n"
            "So I used it. I burned everything down—the captain, my chance at a new life, any hope of belonging here.\n\n"
            "[Pause]\n\n"
            "You're angry too. I can see it under everything you do. But anger doesn't build anything. It just clears the ground. "
            "What are you going to do when there's nothing left to destroy?"
        ),
        "question_for_player": "Can you channel the anger into something other than destruction? Can you build instead of burn?"
    },
    WoundType.IMPOSTOR: {
        "what_mirror_shows": "Yuki had been pretending to be someone else for years. Rather than be exposed, she killed.",
        "parallel": "The player has been performing identity—different faces for different NPCs. Yuki shows the terror of exposure.",
        "revelation_moment": (
            "I built a new identity. New name, new story, new person. Three years of pretending. "
            "And then the captain looked at me one day and said, 'I know who you really are.'\n\n"
            "I couldn't let the mask come off. I couldn't let them see... whatever's underneath. I'm not even sure I know anymore.\n\n"
            "[Looks at the player]\n\n"
            "You do the same thing. Different smile for Torres than for Ember. Different voice for Vasquez than for Kai. "
            "How many versions of you are there? Which one is real? What happens when someone sees through all of them?"
        ),
        "question_for_player": "Who are you when you stop performing? Is there someone underneath the masks?"
    },
    WoundType.PARANOID: {
        "what_mirror_shows": "Yuki was certain the crew would turn on her. She killed to prevent a betrayal that might never have happened.",
        "parallel": "The player has been seeing threats everywhere, trusting no one. Yuki shows where paranoia leads.",
        "revelation_moment": (
            "I knew they'd turn on me. The moment they found out what I did for the company, they'd throw me out the airlock "
            "or hand me over to whoever wanted me dead. I was sure of it.\n\n"
            "So I struck first. Eliminated the threat before it could eliminate me.\n\n"
            "[Pause]\n\n"
            "Funny thing is, I'll never know if I was right. Maybe Torres would have understood... Maybe Kai wouldn't have cared... "
            "I'll never know because I was so sure I was in danger that I made sure I was.\n\n"
            "You're doing the same thing. Seeing enemies everywhere. How many allies have you pushed away because you were certain they'd betray you?"
        ),
        "question_for_player": "What if the danger is mostly in your head? What if you're creating the isolation you fear?"
    },
    WoundType.NARCISSIST: {
        "what_mirror_shows": "Yuki couldn't bear the shame of exposure. Her self-image was more important than another person's life.",
        "parallel": "The player has been protecting their image, requiring admiration. Yuki shows the extreme: killing to preserve the illusion.",
        "revelation_moment": (
            "I couldn't let them see me as a failure. A monster. Everything I built—the respect, the competence, the image—would have crumbled. "
            "I would rather kill than be seen as who I really am.\n\n"
            "[Pause]\n\n"
            "Don't look at me like you're different. I've seen how you need people to see you a certain way. "
            "The moment someone sees through you, you discard them. You can't stand being ordinary. Being flawed. Being human.\n\n"
            "I just took it further than you have. Yet."
        ),
        "question_for_player": "What would it cost to be seen as you really are? Is the image worth more than connection?"
    },
    WoundType.COWARD: {
        "what_mirror_shows": "Yuki acted—violently, wrongly, but she acted. The player has been avoiding hard moments.",
        "parallel": "Yuki is a dark mirror: she's what happens when someone acts from fear instead of running from it.",
        "revelation_moment": (
            "You want to judge me? At least I did something. I made a choice. A terrible one, but a choice.\n\n"
            "You've been running from every hard moment since you got here. Avoiding confrontations. "
            "Letting others take risks. Hoping someone else will solve this.\n\n"
            "We're both afraid. The difference is I let my fear drive me to action. You let yours drive you to nothing."
        ),
        "question_for_player": "When are you going to stop running and choose—even if the choice is hard?"
    }
}

class MirrorSystem:
    @staticmethod
    def generate_revelation(player_wound: WoundType) -> Dict:
        """
        Generates the full revelation content for the murder mystery resolution
        based on the player's psychological wound.
        """
        
        # Fallback to Controller if archetype not specifically implemented or is Unknown
        if player_wound not in MIRROR_DATA:
            content = MIRROR_DATA[WoundType.CONTROLLER]
            # If it's a known archetype but we just haven't implemented specific text yet
            # we might want to log it, but for now we fallback gracefully.
        else:
            content = MIRROR_DATA[player_wound]
            
        return {
            "phases": [
                {
                    "phase_id": 1,
                    "name": "The Facts",
                    "description": "The player presents evidence. Yuki doesn't deny it.",
                    "narrative_beat": "You lay it all out. The timeline. The motive. The weapon. Yuki listens, her face unreadable. When you finish, she simply nods."
                },
                {
                    "phase_id": 2,
                    "name": "The Why",
                    "description": "Yuki explains her reasoning.",
                    "narrative_beat": "He gave me a choice. Confess and let them decide, or he'd expose me at port. I couldn't let them decide."
                },
                {
                    "phase_id": 3,
                    "name": "The Complication",
                    "description": "Dr. Okonkwo's revelation: the captain was dying.",
                    "narrative_beat": "Dr. Okonkwo steps forward, voice trembling. 'Yuki... he knew. He was dying. Marcus had a terminal neuro-degenerative condition. Three weeks, maybe four. He wasn't threatening you. He was trying to give you a chance to clear your conscience before he was gone. He called it \"settling accounts.\"'",
                    "discovery_highlight": "Marcus Reyes didn't just want the truth—he wanted to see if the people he chose for this crew were who he believed they could be. He was testing his legacy."
                },
                {
                    "phase_id": 4,
                    "name": "The Mirror",
                    "description": "Yuki turns it on the player.",
                    "dialogue": content["revelation_moment"]
                },
                {
                    "phase_id": 5,
                    "name": "The Question",
                    "description": "The final moral question.",
                    "question": content["question_for_player"]
                }
            ],
            "captain_reflection": (
                "Reyes's final journal entry flashes through your mind: 'I've lived a good life. Made mistakes. "
                "Hurt people, even when I was trying to help. But I tried. I tried to give people second chances. "
                "That has to count for something... Maria, I'll see you soon.'"
            ),
            "meta_analysis": {
                "what_mirror_shows": content["what_mirror_shows"],
                "parallel": content["parallel"]
            }
        }
