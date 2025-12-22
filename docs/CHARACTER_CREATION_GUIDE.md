# Character Creation Guide

This guide explains the enhanced character creation system for Datasworn, including quick-start characters and narrative templates.

## Quick-Start Characters

Quick-start characters allow players to jump into the game immediately with pre-built, narratively rich character concepts.

### Available Quick-Start Characters

1. **Subject Zero - The Awakened** (Amnesiac Cryosleep Character)
   - **Stats**: Edge 2, Heart 1, Iron 2, Shadow 1, Wits 1
   - **Assets**: Sleuth, Veteran, Vestige
   - **Vow**: Discover the truth of my identity and why I was placed in cryogenic sleep
   - **Special Mechanics**:
     - Amnesia system
     - Memory fragments unlock throughout gameplay
     - Identity crisis psychological tension
     - Links to conspiracy mystery background

2. **Kade Mercer - The Tracker**
   - **Stats**: Edge 2, Heart 1, Iron 3, Shadow 2, Wits 2
   - **Assets**: Bounty Hunter, Gunslinger, Starship
   - **Vow**: Expose the corrupt network that framed my last target and bring them to justice
   - **Special Mechanics**:
     - Feared hunter reputation
     - Guilt tracker for past mistakes

3. **Ambassador Lyssa Venn - The Peacemaker**
   - **Stats**: Edge 1, Heart 3, Iron 1, Shadow 2, Wits 2
   - **Assets**: Diplomat, Empath, Protocol Bot
   - **Vow**: Broker lasting peace between the Syndicate Collective and Free Captains before war erupts
   - **Special Mechanics**:
     - Trusted mediator reputation
     - Peace talks narrative system

4. **Rook Thane - The Salvager**
   - **Stats**: Edge 3, Heart 1, Iron 1, Shadow 2, Wits 2
   - **Assets**: Explorer, Scavenger, Utility Bot
   - **Vow**: Reach the mysterious system marked on the precursor star map and uncover its secrets
   - **Special Mechanics**:
     - Treasure hunter system
     - Precursor system map quest

5. **Dr. Nyx Korren - The Engineer**
   - **Stats**: Edge 1, Heart 2, Iron 1, Shadow 1, Wits 3
   - **Assets**: Gearhead, Tech, Survey Bot
   - **Vow**: Destroy every military application of my stolen technology and create innovations that protect innocent lives
   - **Special Mechanics**:
     - Inventor system
     - Guilt-driven motivation
     - Saboteur narrative hooks

## Narrative Templates

Narrative templates provide context-aware vow suggestions based on selected character assets (Paths). These help players create thematically appropriate character concepts.

### Path Categories

1. **Combat**: Warriors and fighters (Armored, Blademaster, Gunslinger, etc.)
2. **Exploration**: Adventurers and scouts (Explorer, Navigator, Lore Hunter, etc.)
3. **Social**: Negotiators and influencers (Diplomat, Empath, Leader, etc.)
4. **Technical**: Engineers and technicians (Gearhead, Tech, Demolitionist)
5. **Stealth**: Infiltrators and shadows (Infiltrator, Sleuth, Scoundrel, etc.)
6. **Mystical**: Those touched by supernatural forces (Seer, Shade, Voidborn, etc.)
7. **Support**: Specialists who keep others alive (Healer, Mercenary)

### Example Vow Suggestions

**Combat Characters:**
- "Hunt down the warlord who destroyed my home settlement"
- "Protect the Outer Rim colonies from raider attacks"
- "Find redemption for the innocent lives lost under my command"

**Exploration Characters:**
- "Chart the unexplored regions beyond the Void Gate"
- "Discover the lost colony ship that vanished during the Exodus"
- "Find a new habitable world for my dying settlement"

**Social Characters:**
- "Broker peace between two warring factions before all-out war erupts"
- "Unite the scattered settlements under a common cause"
- "Expose the corruption at the heart of the Trade Syndicate"

## Character Creation Flow

### Option 1: Quick-Start Character
1. Select a pre-built character from the list
2. Review character details (stats, assets, background, vow)
3. Begin adventure immediately

### Option 2: Custom Character
1. **Name & Background**: Enter character name and optional background description
2. **Stats**: Allocate 7 points across 5 stats (Edge, Heart, Iron, Shadow, Wits)
3. **Assets**: Choose up to 3 assets that define your character's abilities
4. **Vow**: Write or select a starting vow (context-aware suggestions based on assets)
5. **Review**: Confirm all details before beginning

## API Endpoints

### Quick-Start Characters
- `GET /api/quickstart/characters` - List all available quick-start characters
- Returns character objects with full details

### Narrative Templates
- `GET /api/narrative/templates` - Get all narrative templates by category
- `GET /api/narrative/vows/{path_name}` - Get suggested vows for a specific Path

### Session Start
- `POST /api/session/start` - Create new game session
  - With quick-start: `{"quickstart_id": "cryo_awakened"}`
  - Custom character: `{"character_name": "...", "stats": {...}, "asset_ids": [...], "background": "..."}`

## Design Philosophy

The enhanced character creation system is designed to:

1. **Reduce Friction**: Quick-start characters let players jump in immediately
2. **Provide Guidance**: Narrative templates suggest thematically appropriate vows
3. **Maintain Flexibility**: Custom creation remains fully featured
4. **Tell Better Stories**: Rich backgrounds and special mechanics create narrative hooks
5. **Support Learning**: New players can learn by example before customizing

## Special Character: Subject Zero (The Awakened)

The amnesiac cryosleep character has unique narrative potential:

- **Memory System**: Fragments of the past unlock during gameplay
- **Identity Exploration**: Who were you before? Who are you now?
- **Mystery Hook**: Why were you frozen? What happened to everyone else?
- **Psychological Depth**: Tension between past and present selves
- **Narrative Flexibility**: Player discovers character through play rather than defining upfront

This creates emergent storytelling where the player and AI collaboratively uncover the character's history.

## Implementation Notes

### Backend
- `src/quickstart_characters.py` - Pre-built character definitions
- `src/narrative_templates.py` - Path-based vow and narrative suggestions
- `src/server.py` - API endpoints for character creation

### Frontend
- `frontend/src/components/CharacterCreation.jsx` - Enhanced multi-step wizard
- Step 0: Quick-start selection
- Steps 1-5: Custom creation flow with guided suggestions

### Integration
- Quick-start characters store special mechanics in `narrative.campaign_summary`
- Starting scenes stored in `narrative.session_summary`
- Narrative templates dynamically loaded based on asset selection
