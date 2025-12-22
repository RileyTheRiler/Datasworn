import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from narrative.endings import EndingOrchestrator, EndingType, EndingStage

def verify_endings():
    orchestrator = EndingOrchestrator()
    
    # Archetypes to test
    archetypes = [
        "Controller", "Judge", "Ghost", "Fugitive", "Cynic",
        "Savior", "Destroyer", "Impostor", "Paranoid", "Perfectionist"
    ]
    
    print("=== STARTING HERO/TRAGEDY FORK VERIFICATION ===\n")
    
    for arch in archetypes:
        print(f"--- Testing Archetype: {arch.upper()} ---")
        
        # 1. Get Decision Prompt
        prompt = orchestrator.get_decision_prompt(arch)
        print(f"Moral Question: {prompt['question']}")
        print(f"Options: {prompt['options']}")
        
        # 2. Test Hero Path
        print(f"\n[HERO PATH]")
        hero_type = orchestrator.process_decision(arch, "accept")
        assert hero_type == EndingType.HERO
        
        decision_text = orchestrator.get_narrative_beat(arch, hero_type, EndingStage.DECISION)
        print(f"Decision: {decision_text[:50]}...")
        
        test_text = orchestrator.get_narrative_beat(arch, hero_type, EndingStage.TEST)
        print(f"Test: {test_text[:50]}...")
        
        res_text = orchestrator.get_narrative_beat(arch, hero_type, EndingStage.RESOLUTION)
        print(f"Resolution: {res_text[:50]}...")
        
        wis_text = orchestrator.get_narrative_beat(arch, hero_type, EndingStage.WISDOM)
        print(f"Wisdom: {wis_text[:50]}...")
        
        final_text = orchestrator.get_narrative_beat(arch, hero_type, EndingStage.FINAL_SCENE)
        print(f"Final Scene: {final_text[:50]}...")
        
        # Check specific keywords for verification
        if arch == "Controller":
            assert "crew decide" in decision_text, "Hero decision text mismatch"
        if arch == "Ghost":
            assert "choose to stay" in decision_text, "Hero decision text mismatch"

        # 3. Test Tragedy Path
        print(f"\n[TRAGEDY PATH]")
        trag_type = orchestrator.process_decision(arch, "reject")
        assert trag_type == EndingType.TRAGEDY
        
        decision_text = orchestrator.get_narrative_beat(arch, trag_type, EndingStage.DECISION)
        print(f"Decision: {decision_text[:50]}...")
        
        test_text = orchestrator.get_narrative_beat(arch, trag_type, EndingStage.TEST)
        print(f"Doubling Down: {test_text[:50]}...")
        
        res_text = orchestrator.get_narrative_beat(arch, trag_type, EndingStage.RESOLUTION)
        print(f"Catastrophe: {res_text[:50]}...")
        
        wis_text = orchestrator.get_narrative_beat(arch, trag_type, EndingStage.WISDOM)
        print(f"Wisdom: {wis_text[:50]}...")
        
        final_text = orchestrator.get_narrative_beat(arch, trag_type, EndingStage.FINAL_SCENE)
        print(f"Final Scene: {final_text[:50]}...")
        
        if arch == "Controller":
            assert "impose your own" in decision_text, "Tragedy decision text mismatch"
        
        print(f"\n{arch} verified successfully.\n")
        
    print("=== ALL ARCHETYPES VERIFIED ===")

if __name__ == "__main__":
    verify_endings()
