"""
Story Templates System

Defines different starting scenarios and settings for players to choose from.
Each template provides a unique environmental context, initial situation, and
narrative hooks that shape the beginning of the adventure.
"""

from typing import Dict, List, Any


class StoryTemplate:
    """A pre-defined story setting and starting scenario."""

    def __init__(
        self,
        id: str,
        name: str,
        tagline: str,
        description: str,
        setting_type: str,
        starting_location: str,
        initial_scenario: str,
        opening_scene: str,
        environmental_conditions: Dict[str, str],
        suggested_themes: List[str],
        npc_archetypes: List[str],
        initial_threats: List[str],
        tone: str,
        difficulty: str = "moderate"
    ):
        self.id = id
        self.name = name
        self.tagline = tagline
        self.description = description
        self.setting_type = setting_type
        self.starting_location = starting_location
        self.initial_scenario = initial_scenario
        self.opening_scene = opening_scene
        self.environmental_conditions = environmental_conditions
        self.suggested_themes = suggested_themes
        self.npc_archetypes = npc_archetypes
        self.initial_threats = initial_threats
        self.tone = tone
        self.difficulty = difficulty

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "tagline": self.tagline,
            "description": self.description,
            "setting_type": self.setting_type,
            "starting_location": self.starting_location,
            "initial_scenario": self.initial_scenario,
            "opening_scene": self.opening_scene,
            "environmental_conditions": self.environmental_conditions,
            "suggested_themes": self.suggested_themes,
            "npc_archetypes": self.npc_archetypes,
            "initial_threats": self.initial_threats,
            "tone": self.tone,
            "difficulty": self.difficulty,
        }


# ============================================================================
# Story Template Presets
# ============================================================================

STORY_TEMPLATES = [
    StoryTemplate(
        id="research_vessel_deep_space",
        name="The Chronos Research Vessel",
        tagline="Isolated horror in the depths of space",
        description=(
            "You're aboard the Chronos, a deep-space research vessel on the edge of the Forge. "
            "The crew was studying anomalous readings from an uncharted nebula when communications "
            "went dark. Now, something has changed. The ship feels... wrong. Corridors that should "
            "be familiar seem alien. Crew members are acting strangely. And there's something in "
            "the cargo bay that wasn't there before."
        ),
        setting_type="space_vessel",
        starting_location="Chronos Research Vessel - Section 7, Medical Bay",
        initial_scenario=(
            "You wake in the medical bay with fragmented memories of the past 48 hours. "
            "The station's AI reports 'minor system anomalies,' but the empty corridors and "
            "flickering lights tell a different story. Your last clear memory: the science team "
            "bringing something aboard from the nebula. A sample. An artifact. Something alive."
        ),
        opening_scene=(
            "Harsh white lights flicker overhead as your eyes adjust. The medical bay is empty—no "
            "staff, no patients. A datapad on the counter displays a terse message: 'Quarantine Protocol "
            "Omega Initiated. All personnel report to designated safe zones.' You don't remember any "
            "drills for Protocol Omega. Through the viewport, the nebula churns with colors that shouldn't "
            "exist. And somewhere deeper in the ship, you hear the low hum of machinery... and something else. "
            "Something breathing."
        ),
        environmental_conditions={
            "lighting": "Harsh fluorescent, flickering intermittently",
            "atmosphere": "Recycled air with a metallic tang",
            "temperature": "Uncomfortably cold (life support degraded)",
            "gravity": "Standard artificial gravity with occasional fluctuations",
            "sound": "Distant mechanical hums, ventilation echoes, unexplained sounds"
        },
        suggested_themes=[
            "Isolation and paranoia",
            "Scientific hubris and consequences",
            "Body horror and transformation",
            "Trust and betrayal among survivors",
            "Humanity vs. the unknown"
        ],
        npc_archetypes=[
            "Paranoid chief scientist who knows more than they're saying",
            "Security officer trying to maintain order",
            "Engineer who might be infected/compromised",
            "AI companion with corrupted directives",
            "Sole survivor from another section"
        ],
        initial_threats=[
            "Whatever was brought aboard from the nebula",
            "Infected or transformed crew members",
            "Failing life support systems",
            "Quarantine lockdowns trapping you in dangerous areas",
            "The nebula itself, which seems aware"
        ],
        tone="horror/mystery",
        difficulty="dangerous"
    ),

    StoryTemplate(
        id="dinosaur_planet",
        name="Isla Genesis - Primordial World",
        tagline="Survival on a world ruled by prehistoric titans",
        description=(
            "Welcome to Isla Genesis, a planet untouched by human civilization—until now. Your "
            "expedition was sent to survey this lush world for colonization potential. What you "
            "found defies explanation: massive reptilian creatures resembling Earth's prehistoric "
            "dinosaurs, despite being thousands of light-years from humanity's birthworld. "
            "When your landing craft crashed during a territorial dispute between two titans, "
            "survival became your only mission."
        ),
        setting_type="wilderness_planet",
        starting_location="Isla Genesis - Crash Site in the Verdant Expanse",
        initial_scenario=(
            "Your team is scattered across the jungle. The landing craft is a smoking ruin. "
            "Your equipment is damaged. And the sounds of massive predators echo through the trees. "
            "You have limited supplies, no communication with the orbiting ship, and rescue won't "
            "come for weeks. The jungle is beautiful, deadly, and full of mysteries that shouldn't exist."
        ),
        opening_scene=(
            "You drag yourself from the wreckage, lungs burning with thick, humid air. The jungle "
            "canopy towers overhead—trees unlike anything in Forge databases, their trunks wider than "
            "your crashed ship. Somewhere in the distance, a roar shakes the ground. Not metaphorically. "
            "The earth literally trembles. Through gaps in the foliage, you glimpse it: a creature "
            "twenty meters tall, covered in scales that shimmer green and gold. It turns its massive "
            "head toward your crash site, nostrils flaring. Then it bellows—a sound that speaks of "
            "rage, territory, and ancient hunger."
        ),
        environmental_conditions={
            "lighting": "Dappled sunlight filtering through dense canopy",
            "atmosphere": "Thick, humid, oxygen-rich (slightly intoxicating)",
            "temperature": "Hot and humid, tropical climate",
            "terrain": "Dense jungle, rivers, cliffs, volcanic regions",
            "sound": "Constant wildlife calls, rustling foliage, distant roars"
        },
        suggested_themes=[
            "Humanity's place in nature",
            "Survival vs. scientific discovery",
            "Ancient mysteries and evolutionary anomalies",
            "Working together vs. self-preservation",
            "Respect for powerful, primal forces"
        ],
        npc_archetypes=[
            "Injured scientist obsessed with studying the creatures",
            "Pragmatic survivalist who wants to signal for rescue immediately",
            "Pilot who blames themselves for the crash",
            "Xenobiologist who recognizes something impossible about the planet",
            "Corporate rep with ulterior motives"
        ],
        initial_threats=[
            "Massive predatory dinosaur-like creatures",
            "Territorial herbivores protecting nesting grounds",
            "Hostile native wildlife (raptors, flying reptiles, venomous species)",
            "Environmental hazards (volcanic activity, flash floods, poisonous plants)",
            "Diminishing supplies and internal team conflicts"
        ],
        tone="adventure/survival",
        difficulty="formidable"
    ),

    StoryTemplate(
        id="siege_station",
        name="Bastion Station Under Siege",
        tagline="Defend the last stronghold against overwhelming forces",
        description=(
            "Bastion Station guards the Outer Rim territories from pirate incursions and worse. "
            "For thirty years, it has stood as an unbreakable fortress. Until today. A massive "
            "coalition fleet—pirates, mercenaries, and rogue military forces—has surrounded the "
            "station. They demand the station's surrender and the handover of a political refugee "
            "hiding within. The commander has refused. Now, it's siege warfare in the void, and "
            "you're trapped inside."
        ),
        setting_type="space_station",
        starting_location="Bastion Station - Security Hub Alpha",
        initial_scenario=(
            "Alarms blare throughout the station. Enemy ships fill the viewports. The civilian "
            "sectors are being evacuated to the core, but there's not enough space for everyone. "
            "The station commander has called for volunteers—anyone who can fight, repair systems, "
            "or keep people calm during the siege. You've answered the call. The question is: will "
            "Bastion hold, or will it fall like so many before it?"
        ),
        opening_scene=(
            "Red emergency lights bathe Security Hub Alpha in crimson. Soldiers rush past, checking "
            "weapons and armor. Through the reinforced viewport, you see them: dozens of warships, "
            "their gun ports glowing like predator eyes. The station commander's voice crackles over "
            "the intercom: 'This is Commander Vex. All hands, battle stations. They've given us one "
            "hour to surrender. We're not going to.' A tech beside you mutters, 'They have us "
            "outnumbered five to one.' Someone else replies, 'Then it's a fair fight.'"
        ),
        environmental_conditions={
            "lighting": "Emergency red lights in critical areas, normal elsewhere",
            "atmosphere": "Tense, pressurized (both literally and emotionally)",
            "temperature": "Controlled, but heat builds during extended combat",
            "terrain": "Metal corridors, defense emplacements, civilian shelters",
            "sound": "Alarms, footsteps, distant weapons fire, hull stress"
        },
        suggested_themes=[
            "Sacrifice for the greater good",
            "Unity in the face of overwhelming odds",
            "Moral choices during wartime",
            "Leadership and responsibility",
            "Hope vs. despair"
        ],
        npc_archetypes=[
            "Veteran commander who won't abandon their post",
            "Civilian leader advocating surrender to save lives",
            "The refugee everyone is fighting over (with secrets)",
            "Young soldier facing combat for the first time",
            "Saboteur working for the enemy"
        ],
        initial_threats=[
            "Enemy boarding parties breaching the hull",
            "Orbital bombardment damaging critical systems",
            "Sabotage from within",
            "Diminishing resources (ammunition, medical supplies, power)",
            "Civilian panic and potential riots"
        ],
        tone="military/action",
        difficulty="extreme"
    ),

    StoryTemplate(
        id="derelict_colony",
        name="New Providence - The Silent Colony",
        tagline="Investigate the mystery of a colony where everyone vanished",
        description=(
            "New Providence was a success story: a thriving colony of 8,000 souls on a temperate "
            "world. Regular supply ships visited quarterly. Then, six months ago, they stopped "
            "responding to hails. Your investigation team has been sent to discover what happened. "
            "The orbital scans are confusing—life signs are present, but no movement. Structures "
            "intact, but power fluctuating. When you land, you find a ghost town frozen in time."
        ),
        setting_type="colony_world",
        starting_location="New Providence - Central Plaza",
        initial_scenario=(
            "The colony is eerily preserved. Meals half-eaten on tables. Vehicles abandoned mid-route. "
            "Personal effects scattered as if people simply... stopped. No bodies. No signs of struggle. "
            "Just absence. Your team's mission: determine what happened, locate survivors if any exist, "
            "and assess whether the colony can be salvaged. But the deeper you investigate, the more "
            "you realize some mysteries are better left buried."
        ),
        opening_scene=(
            "Your boots echo across the empty plaza. Flowerbeds bloom with neglected wildness. "
            "A child's toy lies on the ground—a small starship, wings broken. The colony's central "
            "fountain still runs, water burbling cheerfully despite the abandonment. Your team "
            "leader activates their scanner: 'I'm picking up biosigns. Humanoid. Multiple contacts.' "
            "You turn toward the residential district. 'Where?' She points at the administrative "
            "building, voice tight. 'Everywhere. They're all in there. Hundreds of them. And they're "
            "not moving.'"
        ),
        environmental_conditions={
            "lighting": "Natural daylight, some buildings have emergency power",
            "atmosphere": "Earth-normal, pleasant (disturbingly peaceful)",
            "temperature": "Comfortable, temperate climate",
            "terrain": "Colonial architecture, parks, farmland, underground facilities",
            "sound": "Wind, wildlife, automated systems, unsettling silence from buildings"
        },
        suggested_themes=[
            "The unknown and unknowable",
            "Small-town secrets writ large",
            "Technology's unintended consequences",
            "What defines humanity",
            "The cost of progress"
        ],
        npc_archetypes=[
            "Investigation lead determined to find answers",
            "Scientist who recognizes forbidden technology",
            "Sole survivor (if any) who may be unreliable",
            "Corporate rep more interested in salvage than truth",
            "AI that knows more than it should"
        ],
        initial_threats=[
            "The unknown force that caused the disappearance",
            "Whatever the colonists became/transformed into",
            "Automated defense systems protecting something",
            "Psychological horror of the abandoned colony",
            "Time pressure before higher authorities cover it up"
        ],
        tone="mystery/horror",
        difficulty="formidable"
    ),

    StoryTemplate(
        id="frontier_war",
        name="The Meridian Frontier",
        tagline="Navigate political intrigue in a war-torn border region",
        description=(
            "The Meridian Frontier: a contested border region where three factions clash for control. "
            "The Hegemony brings order through authoritarian rule. The Free Traders demand autonomy "
            "and profit. The Indigenous Coalition fights to reclaim ancestral territories. You've "
            "arrived at Crossroads Station, a neutral ground where all three factions maintain an "
            "uneasy presence. But neutrality is fragile, and you've been pulled into a conflict that "
            "will reshape the Forge."
        ),
        setting_type="frontier_station",
        starting_location="Crossroads Station - The Neutral Zone",
        initial_scenario=(
            "You came to Crossroads Station looking for work, refuge, or opportunity. What you found "
            "is a powder keg ready to explode. A Hegemony warship sits in orbit. Free Trader smugglers "
            "operate in the shadows. Indigenous Coalition delegates negotiate in good faith while their "
            "warriors sharpen blades. Everyone wants something from you, and every choice you make will "
            "have consequences far beyond this station."
        ),
        opening_scene=(
            "The Neutral Zone bar is crowded tonight. Three distinct groups occupy three distinct "
            "corners: Hegemony officers in crisp uniforms nursing expensive whiskey, Free Trader captains "
            "arguing loudly over cards, Indigenous Coalition elders speaking in quiet tones. You sit at "
            "the bar between all of them—neutral ground. The bartender slides you a drink. 'First one's "
            "free. After that, you pay in information, same as everyone else.' On the viewscreen overhead, "
            "news crawls past: 'Meridian Talks Stall Again. Experts Predict Armed Conflict Within Weeks.' "
            "A Hegemony officer catches your eye. A Trader captain waves you over. A Coalition elder "
            "nods in acknowledgment. Choose wisely."
        ),
        environmental_conditions={
            "lighting": "Varied by district (military bright, trader dim, coalition natural)",
            "atmosphere": "Tense, multicultural, politically charged",
            "temperature": "Controlled, but tempers run hot",
            "terrain": "Space station with distinct factional territories",
            "sound": "Multiple languages, arguments, music from different cultures"
        },
        suggested_themes=[
            "War and its cost",
            "Cultural conflict and understanding",
            "Political manipulation and truth",
            "Loyalty vs. self-interest",
            "Can peace exist, or only temporary ceasefires?"
        ],
        npc_archetypes=[
            "Hegemony diplomat with hidden orders",
            "Free Trader smuggler with valuable information",
            "Indigenous Coalition warrior seeking justice",
            "Station administrator trying to maintain peace",
            "Journalist documenting the brewing conflict",
            "Spy from an unknown fourth faction"
        ],
        initial_threats=[
            "False flag operations designed to trigger war",
            "Assassinations of key peacemakers",
            "Blockades and resource shortages",
            "Factional extremists on all sides",
            "The revelation that someone wants this war to happen"
        ],
        tone="political/intrigue",
        difficulty="formidable"
    ),

    StoryTemplate(
        id="prison_ship",
        name="The Infernus - Maximum Security Prison Ship",
        tagline="Survive a prison break aboard a ship full of the galaxy's worst",
        description=(
            "The Infernus houses the Forge's most dangerous criminals: war criminals, serial killers, "
            "rogue AIs, and worse. You're aboard either as a prisoner, guard, or specialist. It doesn't "
            "matter which because the ship's AI has just malfunctioned. Cell doors are opening. "
            "Containment fields are failing. And the worst monsters in human space are now free—along "
            "with you. Survival means navigating a ship where every corridor could hide a nightmare."
        ),
        setting_type="prison_vessel",
        starting_location="The Infernus - Cell Block Zeta",
        initial_scenario=(
            "Alarms scream through the ship. Red lights bathe the corridors. The AI's voice, usually "
            "calm and authoritative, stutters: 'Sys-tem failure. All per-sonnel evacuate. Repeat: all—' "
            "Then silence. The cell doors unlock with a hiss. Laughter echoes from nearby cells—the kind "
            "of laughter that makes your skin crawl. You have minutes to arm yourself before the "
            "really dangerous inmates reach your block."
        ),
        opening_scene=(
            "Your cell door slides open. You step into the corridor cautiously, expecting guards, "
            "protocol, answers. Instead: chaos. A guard's body lies motionless, stripped of weapons. "
            "Emergency pods launch from the ship—the crew is abandoning you. Through the viewport, "
            "you watch escape pods fleeing like fireflies. Someone behind you chuckles. 'Well, well. "
            "Fresh meat.' You turn. A massive figure steps from the shadows, tattoos covering scarred "
            "flesh. 'Here's how this works: you help me reach the bridge, or I paint these walls with "
            "you. Choose quick.'"
        ),
        environmental_conditions={
            "lighting": "Emergency red lights, some sections completely dark",
            "atmosphere": "Recycled air with smoke from fires, oppressive",
            "temperature": "Uncomfortably warm, life support degraded",
            "terrain": "Metal corridors, cell blocks, industrial areas, bridge",
            "sound": "Screams, violence, alarms, hull breaches hissing"
        },
        suggested_themes=[
            "Morality in desperate circumstances",
            "Can the worst people be redeemed?",
            "Temporary alliances with enemies",
            "Justice vs. vengeance",
            "What would you do to survive?"
        ],
        npc_archetypes=[
            "The charismatic psychopath who wants followers",
            "Former military prisoner with combat skills",
            "Wrongly convicted innocent trying to prove it",
            "Vengeful inmate hunting a specific target",
            "Prison doctor/psychologist trapped with patients",
            "AI fragment that may or may not be trustworthy"
        ],
        initial_threats=[
            "Violent inmates hunting prey",
            "Malfunctioning ship systems (life support, gravity, airlocks)",
            "Containment breaches releasing hazardous materials or creatures",
            "Factional prisoner gangs fighting for control",
            "The AI itself, whose malfunction may not be accidental"
        ],
        tone="thriller/action",
        difficulty="extreme"
    ),

    StoryTemplate(
        id="expedition_ruins",
        name="Precursor Ruins of Khyber-9",
        tagline="Uncover ancient secrets in alien ruins",
        description=(
            "Khyber-9: an airless moon riddled with vast underground structures predating human "
            "civilization by millennia. These Precursor ruins have yielded technology that revolutionized "
            "the Forge—and secrets that drove researchers mad. Your archaeological expedition has "
            "discovered a new chamber, sealed for thousands of years. Whatever lies inside could change "
            "humanity's understanding of the universe... or doom everyone who sees it."
        ),
        setting_type="archaeological_site",
        starting_location="Khyber-9 - Research Camp Alpha",
        initial_scenario=(
            "The excavation is nearly complete. Tomorrow, you breach the sealed chamber. Tonight, "
            "the team celebrates in the pressurized habitat. But something feels wrong. The ruins' "
            "energy readings have spiked. Team members report strange dreams. And one of the senior "
            "archaeologists is missing. The ruins are waking up, and humanity may not be ready for "
            "what they have to say."
        ),
        opening_scene=(
            "The habitat's lights flicker as another power surge rolls through from the ruins. "
            "Dr. Chen stands at the viewport, staring at the excavation site. 'We shouldn't open it,' "
            "she whispers. 'The warning glyphs... we translated them wrong. It's not \"knowledge waits "
            "within.\" It's \"knowledge must wait. Do not wake what sleeps.\"' The expedition leader "
            "dismisses her concerns: 'Cold feet, Doctor? We're making history.' But you've seen the "
            "translated warnings too. And deep below, something ancient is stirring."
        ),
        environmental_conditions={
            "lighting": "Artificial lights in habitat, bioluminescent in ruins",
            "atmosphere": "Airless moon surface, pressurized habitat and suits",
            "temperature": "Extreme cold outside, controlled inside",
            "terrain": "Rocky moon surface, vast underground structures, alien architecture",
            "sound": "Silence outside, pressurized hum inside, strange resonances from ruins"
        },
        suggested_themes=[
            "The price of knowledge",
            "Hubris and consequences",
            "Ancient mysteries and cosmic horror",
            "Science vs. superstition",
            "Some doors should stay closed"
        ],
        npc_archetypes=[
            "Obsessed expedition leader ignoring warnings",
            "Cautious archaeologist who senses danger",
            "Corporate sponsor demanding results",
            "Xenolinguist who can communicate with whatever awakens",
            "Security specialist who's seen ruins like this before",
            "AI assistant analyzing Precursor technology"
        ],
        initial_threats=[
            "Precursor defense systems activating",
            "Psychological effects from alien technology",
            "Awakening of dormant Precursor AI or entities",
            "Environmental hazards (airless surface, unstable structures)",
            "Competing factions trying to steal discoveries",
            "The knowledge itself, which may be dangerous to comprehend"
        ],
        tone="mystery/cosmic horror",
        difficulty="formidable"
    )
]


def get_story_templates() -> List[Dict[str, Any]]:
    """Return all story templates as dictionaries."""
    return [template.to_dict() for template in STORY_TEMPLATES]


def get_story_template_by_id(template_id: str) -> StoryTemplate | None:
    """Get a specific story template by ID."""
    for template in STORY_TEMPLATES:
        if template.id == template_id:
            return template
    return None
