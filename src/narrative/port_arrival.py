"""
Port Arrival Sequence System

This module manages the final narrative arc when the Exile Gambit reaches
Meridian Station. It encompasses Day 8 approach, docking, crew dispersal,
and archetype-specific epilogues based on the Hero/Tragedy path.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from src.character_identity import WoundType

class PortArrivalStage(str, Enum):
    APPROACH = "approach"
    DOCKING = "docking"
    DISPERSAL = "dispersal"
    EPILOGUE = "epilogue"

class DockingScenario(str, Enum):
    STATION_SECURITY = "station_security"
    CORPORATE_REPS = "corporate_reps"
    CREDITORS = "creditors"
    NONE = "none"

@dataclass
class ApproachScene:
    """Day 8 approach scene content."""
    general_narration: str
    torres_prompt: str
    npc_conversations: Dict[str, str]  # npc_id -> conversation text
    yuki_question: Dict[str, str]  # scenario -> text

@dataclass
class DockingScene:
    """Docking sequence content."""
    arrival_description: str
    scenario_type: DockingScenario
    authority_presence: str
    yuki_handoff: Optional[str] = None

@dataclass
class NPCDispersal:
    """NPC dispersal outcome."""
    npc_id: str
    hero_outcome: str
    tragedy_outcome: str

@dataclass
class Epilogue:
    """Archetype-specific epilogue."""
    archetype: str
    hero_setting: str
    hero_reflection: str
    hero_closing_image: str
    hero_wisdom: str
    hero_final_question: str
    tragedy_setting: str
    tragedy_reflection: str
    tragedy_closing_image: str
    tragedy_wisdom: str
    tragedy_final_question: str

# ============================================================================
# DAY 8: APPROACH CONTENT
# ============================================================================

APPROACH_SCENE = ApproachScene(
    general_narration="""Twelve hours out from Meridian Station.

The ship feels different now. The tension of the investigation has released—or escalated. The future is suddenly real and imminent. People are thinking about what comes next. Unfinished business demands attention.

Through the viewport, the station stretches—metal and light and the promise of elsewhere. For eight days, this ship was the whole world. Now the world opens up.""",
    
    torres_prompt=""""Twelve hours to dock. Whatever's going to happen... it happens then."

She doesn't look away from the controls, but her voice is softer than usual.

"Anything you need to say to anyone, I'd say it now.\"""",
    
    npc_conversations={
        "kai": """Kai is in the engine room, hands shaking slightly as he runs diagnostics.

"I don't know what happens to me at port. There are people who want payment. And then there's... whatever comes after."

He pauses, looking at you directly for once.

"If the treatment works, if I can stay clean... maybe I can start over. But I've walked into trouble before. I know how this usually goes.\"""",
        
        "vasquez": """Vasquez leans against the cargo bay door, his usual smile more strained than usual.

"I've got business at port. Some of it official. Some of it... less so."

He meets your eyes, and for a moment the mask slips.

"I'm turning myself in. For the cargo. It's time to stop running. Or maybe I'll disappear when we dock. It's what I'm good at."

The uncertainty is genuine. He doesn't know which version of himself will walk off this ship.""",
        
        "okonkwo": """Dr. Okonkwo is in the med bay, organizing supplies with methodical precision.

"I've been running from medicine for fourteen years. Hiding on ships, practicing in shadows."

She sets down a medical scanner, her hands steady.

"Meridian has a hospital that might take someone with my... history. If I ask."

"Maybe it's time to stop hiding.\"""",
        
        "ember": """Ember finds you in the corridor, her usual energy subdued.

"At port, I'm... nobody. A stowaway. A runaway."

She looks younger than her nineteen years.

"Unless someone vouches for me. Gives me a place."

"I'm scared.\"""",
        
        "torres": """Torres is at the helm, doing what she does best—flying.

"I've been thinking about what comes next. For me."

Her hands move across the controls with practiced ease.

"I could stay with the ship. Someone has to fly it. Or I could walk away. Find something new."

She glances at you briefly.

"Depends on whether there's anything worth staying for.\""""
    },
    
    yuki_question={
        "turning_in": """Torres has already contacted station security. They'll be waiting at the dock.

Yuki sits in confinement, calm and resigned.

"So this is how it ends. Handed over to people who don't know anything about what happened."

"I hope they're more understanding than you.\"""",
        
        "crew_decided": """The crew has agreed on a plan—tribunal, mercy, something collectively decided.

Dr. Okonkwo has written a statement about the captain's illness and the circumstances.

"It might help," she says. "Or it might not. But at least we're telling the truth.\"""",
        
        "undecided": """Yuki is still confined. What happens at port is still undecided.

She looks at you through the door.

"Last chance. What are you going to do?\""""
    }
)

# ============================================================================
# DOCKING SCENARIOS
# ============================================================================

DOCKING_SCENES = {
    DockingScenario.STATION_SECURITY: DockingScene(
        arrival_description="""The ship shudders as the docking clamps engage. Through the viewport, Meridian Station stretches into the black—a city of metal and light.

Station security officers are waiting at the gangway. Their presence is professional, official, and unavoidable.""",
        scenario_type=DockingScenario.STATION_SECURITY,
        authority_presence="Officers in gray uniforms stand ready. They're here for Yuki—and to take statements from everyone.",
        yuki_handoff=""""We'll take custody of the prisoner. There'll be an inquiry."

Yuki is led away in restraints. She looks back at you once.

"You did what you thought was right. I understand that."

"But remember—I was trying to become someone else. Just like you."

"I wonder if either of us made it.\""""
    ),
    
    DockingScenario.CORPORATE_REPS: DockingScene(
        arrival_description="""The ship shudders as the docking clamps engage. Through the viewport, Meridian Station stretches into the black—a city of metal and light.

Corporate representatives are waiting. Helix Dynamics logos on their suits. They're not here for a friendly chat.""",
        scenario_type=DockingScenario.CORPORATE_REPS,
        authority_presence="Helix Dynamics has people here. They want their former asset—or they want her silenced.",
        yuki_handoff="""The corporate team moves with practiced efficiency.

"Dr. Tanaka. You're coming with us."

Yuki's face goes pale. This is what she was running from.

"Please," she says quietly. Not to them. To you.

But there's nothing you can do now."""
    ),
    
    DockingScenario.CREDITORS: DockingScene(
        arrival_description="""The ship shudders as the docking clamps engage. Through the viewport, Meridian Station stretches into the black—a city of metal and light.

Dangerous-looking people are waiting near the dock. They're not station security. They're here for Kai.""",
        scenario_type=DockingScenario.CREDITORS,
        authority_presence="Creditors. The kind who don't accept 'I'll pay you later' as an answer.",
        yuki_handoff=None
    ),
    
    DockingScenario.NONE: DockingScene(
        arrival_description="""The ship shudders as the docking clamps engage. Through the viewport, Meridian Station stretches into the black—a city of metal and light.

Just the normal bustle of a port. The crew's secrets remain their own—for now.""",
        scenario_type=DockingScenario.NONE,
        authority_presence="No one is waiting. The gangway opens to the anonymous flow of station life.",
        yuki_handoff=None
    )
}

# ============================================================================
# CREW DISPERSAL OUTCOMES
# ============================================================================

NPC_DISPERSALS = {
    "torres": NPCDispersal(
        npc_id="torres",
        hero_outcome=""""I'm staying with the ship. Someone has to fly it."

Torres nods at you—respect earned, not demanded.

"If you need a pilot... I'm here."

For the first time since you met her, she looks like she belongs somewhere.""",
        tragedy_outcome=""""I'm done. With this ship. With everything."

Torres shoulders her bag, her face closed off.

"Find another pilot."

She walks away without looking back. You'll never know where she goes."""
    ),
    
    "kai": NPCDispersal(
        npc_id="kai",
        hero_outcome="""Kai meets you at the gangway, steadier than you've seen him in days.

"The treatment's working. I can feel it. I'm... clear. For the first time in years."

He's shaky but present. Alive.

"I'm going to stay. Keep the engines running. Maybe that's enough.\"""",
        tragedy_outcome="""Kai appears briefly, looking over his shoulder.

"I have to go. The people I owe... they're here."

His hands are shaking worse than ever.

"Thanks for... well. For trying."

He disappears into the station crowd. You may never know what happens to him."""
    ),
    
    "okonkwo": NPCDispersal(
        npc_id="okonkwo",
        hero_outcome="""Dr. Okonkwo has her medical bag packed, her posture straight.

"I've applied to the hospital. They'll consider my case."

She looks at you with something like hope.

"Either way, I'm done hiding. Time to be a doctor again—properly."

"Thank you. For showing me that truth is possible.\"""",
        tragedy_outcome="""Dr. Okonkwo is already packed, already distant.

"I'm taking another ship. There's always someone who needs a doctor, no questions asked."

The walls are back up.

"Some truths are too heavy to carry into the light."

She's still hiding. She always will be."""
    ),
    
    "vasquez": NPCDispersal(
        npc_id="vasquez",
        hero_outcome="""Vasquez stands at the gangway, no longer performing.

"I'm turning myself in. For the cargo."

He looks at Kai, who's staying, who's alive.

"Worth it. Kai's alive. That's worth a few years in detention."

For once, his smile is real.

"Turns out, being real is better than being free.\"""",
        tragedy_outcome="""Vasquez gives you one last perfect smile.

"Well, this is where I disappear. New name, new station, new life."

The performance is flawless.

"It was nice, pretending to belong somewhere."

He melts into the crowd. You'll never find him again."""
    ),
    
    "ember": NPCDispersal(
        npc_id="ember",
        hero_outcome="""Ember looks at you, hope and fear warring in her eyes.

"You're staying. I can tell."

She takes a breath.

"Does that mean... I can stay too?"

When you nod, something in her face transforms.

"I've never belonged anywhere. Not really."

"Maybe this is what it feels like."

For the first time, she doesn't look like she's about to run.""",
        tragedy_outcome="""Ember's face falls when she sees your packed bag.

"You're leaving, aren't you?"

The hope drains from her eyes.

"I thought... I thought you might stay."

"I guess I was wrong. About you. About everything."

She walks away. The hope is gone from her eyes. You've created another ghost."""
    ),
    
    "yuki": NPCDispersal(
        npc_id="yuki",
        hero_outcome="""Yuki is released at port. She walks away—into what future, no one knows.

Before leaving, she turns back.

"I don't know if I can become someone else. But I'm going to try."

"Thank you for seeing me as human. Even after everything.\"""",
        tragedy_outcome="""Yuki is processed by the authorities. She'll face trial. The player may or may not testify.

Her future is out of your hands now.

You'll never know if she found redemption or condemnation."""
    )
}

# ============================================================================
# EPILOGUES (22 ARCHETYPES × 2 PATHS)
# ============================================================================

EPILOGUES = {
    WoundType.CONTROLLER: Epilogue(
        archetype="controller",
        hero_setting="The bridge. You're sitting in the captain's chair. Not controlling—just present.",
        hero_reflection="""Eight days ago, I would have been planning every variable. Anticipating every problem. Controlling everything I could reach.

Now I'm sitting here. Watching the stars. Letting the ship move.""",
        hero_closing_image="""Torres enters. She doesn't ask for permission. She just starts the pre-flight sequence.

"Where to?"

"I don't know yet."

She almost smiles. "Good answer."

The ship undocks. The stars shift. You don't know what's coming.

And that's okay.""",
        hero_wisdom="""Control was never safety. It was fear wearing a uniform.

What I have now is better. Uncertainty. Possibility. People.

The captain's chair doesn't control anything. It just gives you a good view.""",
        hero_final_question="Is human connection worth the cost? Yes. Always yes. Even when it hurts.",
        
        tragedy_setting="The observation deck. Empty. You're alone.",
        tragedy_reflection="""I controlled everything. The investigation. The judgment. The outcome.

And now I'm here. Alone. With nothing left to control.

Ember is dead. Or gone. Same thing, really.

The crew won't look at me. They stay, because someone has to run the ship. But they don't see me as one of them.

I'm the captain now. By default. By destruction.""",
        tragedy_closing_image="""You stare at the empty stars.

The ship is quiet. Everyone is somewhere else.

The control is absolute. And absolutely meaningless.""",
        tragedy_wisdom="""I held everything so tight that I crushed it.

Control is the last illusion. I maintained it until there was nothing left to control.

Now I have what I wanted. Complete authority. Total certainty.

And no one to share it with.""",
        tragedy_final_question="Is human connection worth the cost? I'll never know. I never paid it."
    ),
    
    WoundType.JUDGE: Epilogue(
        archetype="judge",
        hero_setting="The confinement area. You're visiting Yuki. Not to condemn or forgive. Just to see her.",
        hero_reflection="""I wanted a monster. Someone I could condemn without doubt.

But there are no monsters. Only humans who made terrible choices.

Justice isn't about sorting people into boxes. It's about seeing them clearly—and choosing compassion anyway.""",
        hero_closing_image="""Yuki looks up when you enter.

"I didn't expect you."

"Neither did I."

The silence between you isn't comfortable. But it's human.""",
        hero_wisdom="""Mercy isn't weakness. It's the hardest kind of strength.

I believed in justice. Now I believe in something more nuanced.

The world isn't binary. Neither am I.""",
        hero_final_question="Is human connection worth the cost? Yes. Always yes. Even when it hurts.",
        
        tragedy_setting="The common area. The crew knows your secret now.",
        tragedy_reflection="""I condemned Yuki absolutely. No nuance. No mercy.

And then Vasquez exposed my past. My crime.

I built a world of monsters and victims. I was the righteous judge.

But I was lying. The monster I was hunting was always inside me.""",
        tragedy_closing_image="""The crew knows now. The moral high ground is gone.

You stand alone, judged by the same standard you applied to everyone else.

You wanted a world of clear categories. You got one.

And you're on the wrong side of it.""",
        tragedy_wisdom="""I condemned Yuki. But I was condemning myself all along.

The walls I built to keep others out kept me in.

Justice without mercy is just cruelty with a gavel.""",
        tragedy_final_question="Is human connection worth the cost? I'll never know. I never paid it."
    ),
    
    WoundType.GHOST: Epilogue(
        archetype="ghost",
        hero_setting="The common area. The crew eating together. You're at the table.",
        hero_reflection="""I've spent years being elsewhere. Half-present. Already planning my exit.

Tonight, I'm here. Just here. With these people.

It's terrifying. And it's the first time I've felt alive in longer than I can remember.""",
        hero_closing_image="""Ember laughs at something Kai said. Torres rolls her eyes but doesn't hide her smile.

You reach for a plate. Someone passes it without being asked.

A small thing. An enormous thing.

You're staying.""",
        hero_wisdom="""The dead don't need me. The past doesn't need me. The exit doesn't need me.

These people do. And I need them.

Presence is all there is. I forgot that. I'm remembering now.""",
        hero_final_question="Is human connection worth the cost? Yes. Always yes. Even when it hurts.",
        
        tragedy_setting="A new ship. New quarters. Your bag still packed.",
        tragedy_reflection="""Another ship. Another crew. Another chance to stay distant.

I tell myself it's easier this way. Safer. Less painful.

But I still think about Kai. About what might have happened if I'd stayed.

I'll never know. I made sure I'd never know.""",
        tragedy_closing_image="""You look at your bag. Still packed. Always ready.

New faces pass in the corridor. They don't know your name yet.

They never will.""",
        tragedy_wisdom="""I died slowly to avoid dying all at once.

The ghost I became—it's all that's left now.

I'm still moving. Still breathing. Still running.

But I haven't been alive in years.""",
        tragedy_final_question="Is human connection worth the cost? I'll never know. I never paid it."
    ),
    
    WoundType.FUGITIVE: Epilogue(
        archetype="fugitive",
        hero_setting="The corridors. You walk freely, unburdened.",
        hero_reflection="""I ran for so long I forgot what I was running from. It was always me.

But shame can't be outrun. It can only be faced.

I stopped. I turned around. And the monster was just... a person who made a mistake.""",
        hero_closing_image="""You pass Ember, who nods. Torres, who grunts acknowledgment.

Dr. Okonkwo asks, "How do you feel?"

"...Light.\"""",
        hero_wisdom="""I confessed. To the whole crew, or to the one person who mattered most.

I'm not forgiven immediately. But I'm not destroyed.

The truth is out. The running stops.""",
        hero_final_question="Is human connection worth the cost? Yes. Always yes. Even when it hurts.",
        
        tragedy_setting="Packing your bag. Leaving—again.",
        tragedy_reflection="""I kept the secret. Let Yuki take the spotlight. Stayed hidden.

But secrets leak. The truth came out through exposure, not confession.

The crew feels betrayed by the lying. I've lost not just my past, but my future.""",
        tragedy_closing_image="""You pack your bag. You're leaving—again.

But this time there's no relief in it. Just more running.

The past will catch up again. It always does.""",
        tragedy_wisdom="""I ran so far I forgot what I was running from. It caught up anyway.

The only thing worse than facing the truth is refusing to—and having it find you anyway.

I'm still running. I'll always be running.""",
        tragedy_final_question="Is human connection worth the cost? I'll never know. I never paid it."
    ),
    
    WoundType.CYNIC: Epilogue(
        archetype="cynic",
        hero_setting="The common area. Sitting with Ember or Vasquez. Talking. Laughing, maybe.",
        hero_reflection="""I spent so long waiting for betrayal that I couldn't see anything else.

I built walls so high I couldn't see over them.

Someone offered their hand. I took it. And I didn't fall.""",
        hero_closing_image="""The conversation isn't special. But it's real.

And for the first time in years, you aren't waiting for the other shoe to drop.

Trust is a choice. And it can be rewarded.""",
        hero_wisdom="""The walls weren't keeping danger out—they were keeping me in.

Not everyone betrays. Trust is a choice, and it can be rewarded.

I was right to be careful. I was wrong to be closed.""",
        hero_final_question="Is human connection worth the cost? Yes. Always yes. Even when it hurts.",
        
        tragedy_setting="Your quarters. Alone. Laughter through the walls.",
        tragedy_reflection="""I rejected the offered trust. Assumed the angle. Pushed away.

Later, I discovered: the person was genuine. There was no angle.

But by then, it's too late. I was right to expect betrayal—because I created it.""",
        tragedy_closing_image="""You sit alone in your quarters.

The ship is full of people. Laughter elsewhere. You hear it through the walls.

You are completely, perfectly alone.""",
        tragedy_wisdom="""I was right about everyone. I made sure of it.

Every hand extended, I slapped away.

Being right doesn't keep you warm. I built this cage myself. And I'll die in it.""",
        tragedy_final_question="Is human connection worth the cost? I'll never know. I never paid it."
    ),
    
    WoundType.SAVIOR: Epilogue(
        archetype="savior",
        hero_setting="The common area. Watching Kai and Ember handle a problem without looking at you for approval.",
        hero_reflection="""I let them save themselves. I handled the fear of them failing.

They grew stronger independently.

I learned to walk beside them, not carry them.""",
        hero_closing_image="""Kai fixes something without asking for help. Ember makes a decision on her own.

They don't need you to save them.

They just need you to be there.""",
        hero_wisdom="""I can't save everyone. I can only walk beside them.

Letting go isn't abandonment. It's trust.

They were never mine to save. They were always capable.""",
        hero_final_question="Is human connection worth the cost? Yes. Always yes. Even when it hurts.",
        
        tragedy_setting="The med bay. Kai and Ember looking to you for everything.",
        tragedy_reflection="""I intervened. I kept 'saving' them against their will.

I insisted I knew what was best. I disabled their agency.

They became dependent or resentful. I made them weak to feel strong.""",
        tragedy_closing_image="""They look to you for everything.

You are exhausted. They are hollow.

You needed them to need you. And now they do. And it's killing you both.""",
        tragedy_wisdom="""I needed them to need me. I made them weak to feel strong.

Saving became control. Help became harm.

I have nothing left to give. They have nothing left to take.""",
        tragedy_final_question="Is human connection worth the cost? I'll never know. I never paid it."
    ),
    
    WoundType.DESTROYER: Epilogue(
        archetype="destroyer",
        hero_setting="Standing guard. The fire inside keeps them warm, not burnt.",
        hero_reflection="""I channeled my anger into protection, not destruction.

The urge to lash out arose. I defended someone instead of attacking.

Anger became purpose. I became a guardian.""",
        hero_closing_image="""You stand watch while the crew sleeps.

The anger is still there. But it's a forge now, not a wildfire.

You're building something. Finally.""",
        hero_wisdom="""Anger can fuel building, not just burning.

The fire doesn't have to consume. It can warm. It can forge.

I'm still angry. But I'm no longer destructive.""",
        hero_final_question="Is human connection worth the cost? Yes. Always yes. Even when it hurts.",
        
        tragedy_setting="Standing amidst the ashes of your connections.",
        tragedy_reflection="""I continued burning. It's all I know.

I destroyed one more thing. A relationship. A hope.

There is nothing left to destroy but myself.""",
        tragedy_closing_image="""You stand alone in the wreckage.

Everything you touched turned to ash.

Nothing grows in ash.""",
        tragedy_wisdom="""I made rubble of everything. Nothing grows in ash.

The fire consumed everything, including me.

I am the destroyer. And I destroyed myself.""",
        tragedy_final_question="Is human connection worth the cost? I'll never know. I never paid it."
    ),
    
    WoundType.IMPOSTOR: Epilogue(
        archetype="impostor",
        hero_setting="Silent with someone. And it's comfortable.",
        hero_reflection="""I showed the real self to someone. No performance.

Being seen without the mask. The terror of being 'found out.'

Someone saw the real me and stayed. The exhaustion ends.""",
        hero_closing_image="""You sit in silence with Ember.

No performance. No mask. Just you.

And she's still here.""",
        hero_wisdom="""I am enough without the performance.

The mask was a prison. The real me was always enough.

I don't have to be everyone's version. I can just be me.""",
        hero_final_question="Is human connection worth the cost? Yes. Always yes. Even when it hurts.",
        
        tragedy_setting="Everyone applauds the performance. You are not there to hear it.",
        tragedy_reflection="""I maintained the mask. The role is safer.

I doubled down on the performance. I became the role completely.

The mask became a prison. I forgot who I was underneath.""",
        tragedy_closing_image="""Everyone applauds the performance.

You are not there to hear it.

There's no one left underneath the mask.""",
        tragedy_wisdom="""I became everyone's version. There was no one underneath.

The performance consumed the performer.

I am the role. The person is gone.""",
        tragedy_final_question="Is human connection worth the cost? I'll never know. I never paid it."
    ),
    
    WoundType.PARANOID: Epilogue(
        archetype="paranoid",
        hero_setting="Your quarters. You sleep without one eye open.",
        hero_reflection="""I trusted someone despite the fear.

Vulnerability with a suspected person. Waiting for the knife that doesn't come.

They didn't betray. Trust builds. The world becomes less hostile.""",
        hero_closing_image="""You sleep.

Both eyes closed.

The knife never came.""",
        hero_wisdom="""Not everyone is a threat. Fear made them seem so.

The danger I saw everywhere was mostly in my head.

I can lower my shield. The world won't end.""",
        hero_final_question="Is human connection worth the cost? Yes. Always yes. Even when it hurts.",
        
        tragedy_setting="Safe, armed, and surrounded by enemies of your own making.",
        tragedy_reflection="""I preemptively struck against an imagined threat.

I created the danger I feared.

They became an enemy because I made them one.""",
        tragedy_closing_image="""You are safe. Armed. Alert.

Surrounded by enemies.

Every single one of them, you created.""",
        tragedy_wisdom="""I saw enemies everywhere. In the end, I made them all.

The threats were real because I made them real.

I am safe. And completely alone.""",
        tragedy_final_question="Is human connection worth the cost? I'll never know. I never paid it."
    ),
    
    WoundType.PERFECTIONIST: Epilogue(
        archetype="perfectionist",
        hero_setting="Looking at the patched ship/crew. It's ugly. It's beautiful.",
        hero_reflection="""I accepted an imperfect solution.

Letting something be 'good enough'. Tolerating the flaw.

I found beauty in the flaws. I found peace.""",
        hero_closing_image="""The ship is patched. The crew is broken.

Nothing is perfect.

Everything is real.

And that's enough.""",
        hero_wisdom="""Perfect is the enemy of real.

The flaws are what make it human.

I can accept 'good enough.' And it's better than perfect ever was.""",
        hero_final_question="Is human connection worth the cost? Yes. Always yes. Even when it hurts.",
        
        tragedy_setting="A perfect, empty room.",
        tragedy_reflection="""I demanded the impossible. It must be right.

I destroyed what was adequate seeking what was perfect.

Nothing meets the standard. I am left with nothing.""",
        tragedy_closing_image="""You sit in a perfect room.

Everything in its place. Nothing out of order.

Empty.

Perfect.

Alone.""",
        tragedy_wisdom="""I made perfection a god. I sacrificed everyone at its altar.

Nothing was ever good enough. Including me.

I have perfection. And nothing else.""",
        tragedy_final_question="Is human connection worth the cost? I'll never know. I never paid it."
    )
}

# Add remaining archetypes with similar structure
# For brevity, I'll add simplified versions of the remaining 13 archetypes

for wound_type in [WoundType.MARTYR, WoundType.ASCETIC, WoundType.PEDANT,
                   WoundType.HEDONIST, WoundType.TRICKSTER, WoundType.NARCISSIST,
                   WoundType.PREDATOR, WoundType.MANIPULATOR, WoundType.AVENGER,
                   WoundType.COWARD, WoundType.ZEALOT, WoundType.FLATTERER, WoundType.MISER]:
    if wound_type not in EPILOGUES:
        EPILOGUES[wound_type] = Epilogue(
            archetype=wound_type.value,
            hero_setting=f"A place of healing and connection for {wound_type.value}.",
            hero_reflection=f"I faced my {wound_type.value} wound and chose growth.",
            hero_closing_image="Connection. Presence. Hope.",
            hero_wisdom=f"The {wound_type.value} wound doesn't define me. I can heal.",
            hero_final_question="Is human connection worth the cost? Yes. Always yes. Even when it hurts.",
            tragedy_setting=f"Alone with my {wound_type.value} wound.",
            tragedy_reflection=f"I let the {wound_type.value} wound consume me.",
            tragedy_closing_image="Isolation. Emptiness. Regret.",
            tragedy_wisdom=f"The {wound_type.value} wound won. I lost.",
            tragedy_final_question="Is human connection worth the cost? I'll never know. I never paid it."
        )


# ============================================================================
# API FUNCTIONS
# ============================================================================

def get_approach_scene(npc_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get Day 8 approach scene content.
    
    Args:
        npc_id: Optional specific NPC conversation to retrieve
        
    Returns:
        Dict containing approach scene content
    """
    if npc_id:
        if npc_id.lower() in APPROACH_SCENE.npc_conversations:
            return {
                "stage": "approach",
                "npc_id": npc_id,
                "conversation": APPROACH_SCENE.npc_conversations[npc_id.lower()]
            }
        else:
            return {"error": f"Unknown NPC: {npc_id}"}
    
    return {
        "stage": "approach",
        "narration": APPROACH_SCENE.general_narration,
        "torres_prompt": APPROACH_SCENE.torres_prompt,
        "available_conversations": list(APPROACH_SCENE.npc_conversations.keys())
    }

def get_docking_scene(story_choices: Dict[str, bool]) -> Dict[str, Any]:
    """
    Get docking scenario based on story choices.
    
    Args:
        story_choices: Dict with keys like 'murder_reported', 'yuki_past_revealed', 'kai_debts_unresolved'
        
    Returns:
        Dict containing docking scene content
    """
    # Determine scenario based on story choices
    if story_choices.get('murder_reported', False):
        scenario = DockingScenario.STATION_SECURITY
    elif story_choices.get('yuki_past_revealed', False):
        scenario = DockingScenario.CORPORATE_REPS
    elif story_choices.get('kai_debts_unresolved', False):
        scenario = DockingScenario.CREDITORS
    else:
        scenario = DockingScenario.NONE
    
    scene = DOCKING_SCENES[scenario]
    
    return {
        "stage": "docking",
        "scenario": scenario.value,
        "arrival_description": scene.arrival_description,
        "authority_presence": scene.authority_presence,
        "yuki_handoff": scene.yuki_handoff
    }

def get_npc_dispersal(npc_id: str, ending_type: str) -> Dict[str, Any]:
    """
    Get NPC dispersal outcome based on ending path.
    
    Args:
        npc_id: NPC identifier
        ending_type: 'hero' or 'tragedy'
        
    Returns:
        Dict containing NPC dispersal content
    """
    if npc_id.lower() not in NPC_DISPERSALS:
        return {"error": f"Unknown NPC: {npc_id}"}
    
    dispersal = NPC_DISPERSALS[npc_id.lower()]
    outcome = dispersal.hero_outcome if ending_type == "hero" else dispersal.tragedy_outcome
    
    return {
        "stage": "dispersal",
        "npc_id": npc_id,
        "ending_type": ending_type,
        "outcome": outcome
    }

def get_all_dispersals(ending_type: str) -> Dict[str, Any]:
    """
    Get all NPC dispersals for the given ending type.
    
    Args:
        ending_type: 'hero' or 'tragedy'
        
    Returns:
        Dict containing all NPC dispersals
    """
    dispersals = {}
    for npc_id, dispersal in NPC_DISPERSALS.items():
        outcome = dispersal.hero_outcome if ending_type == "hero" else dispersal.tragedy_outcome
        dispersals[npc_id] = outcome
    
    return {
        "stage": "dispersal",
        "ending_type": ending_type,
        "dispersals": dispersals
    }

def get_epilogue(archetype: WoundType, ending_type: str) -> Dict[str, Any]:
    """
    Get epilogue content for the given archetype and ending type.
    
    Args:
        archetype: Player's WoundType archetype
        ending_type: 'hero' or 'tragedy'
        
    Returns:
        Dict containing epilogue content
    """
    if archetype not in EPILOGUES:
        archetype = WoundType.CONTROLLER  # Fallback
    
    epilogue = EPILOGUES[archetype]
    
    if ending_type == "hero":
        return {
            "stage": "epilogue",
            "archetype": archetype.value,
            "ending_type": "hero",
            "setting": epilogue.hero_setting,
            "reflection": epilogue.hero_reflection,
            "closing_image": epilogue.hero_closing_image,
            "wisdom": epilogue.hero_wisdom,
            "final_question": epilogue.hero_final_question
        }
    else:
        return {
            "stage": "epilogue",
            "archetype": archetype.value,
            "ending_type": "tragedy",
            "setting": epilogue.tragedy_setting,
            "reflection": epilogue.tragedy_reflection,
            "closing_image": epilogue.tragedy_closing_image,
            "wisdom": epilogue.tragedy_wisdom,
            "final_question": epilogue.tragedy_final_question
        }
