"""Direct test of NPC archetype response logic."""
from src.relationship_system import RelationshipWeb
from src.character_identity import WoundType

# Initialize RelationshipWeb
web = RelationshipWeb()

# Test the get_npc_archetype_response method
print("Testing NPC Archetype Response...")
print(f"Crew members: {list(web.crew.keys())}")

# Test with 'security' (Yuki)
npc_id = "security"
player_wound = WoundType.CONTROLLER.value

print(f"\nTesting {npc_id} with player wound: {player_wound}")

if npc_id in web.crew:
    npc = web.crew[npc_id]
    print(f"NPC found: {npc.name}")
    print(f"Has psyche: {npc.psyche is not None}")
    if npc.psyche:
        print(f"Has moral_profile: {npc.psyche.moral_profile is not None}")
        if npc.psyche.moral_profile:
            print(f"Archetype interactions: {npc.psyche.moral_profile.archetype_interactions}")
    
    response = web.get_npc_archetype_response(npc_id, player_wound)
    print(f"\nResponse: {response}")
else:
    print(f"NPC {npc_id} not found in crew")
