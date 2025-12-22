import pytest

from src.narrative.npc_skills import NPCSkillSystem


def test_get_skills_initializes_defaults():
    system = NPCSkillSystem()

    skills = system.get_skills("npc-1")

    assert (skills.combat, skills.tech, skills.social, skills.level, skills.xp) == (1, 1, 1, 1, 0)


def test_award_xp_handles_multiple_level_ups(monkeypatch):
    system = NPCSkillSystem()
    rolls = iter([0.1, 0.5])
    monkeypatch.setattr("src.narrative.npc_skills.random.random", lambda: next(rolls))

    leveled = system.award_xp("npc-1", 30)

    skills = system.get_skills("npc-1")
    assert leveled is True
    assert skills.level == 3
    assert skills.xp == 0
    assert skills.combat == 2  # First roll boosts combat
    assert skills.tech == 2    # Second roll boosts tech
    assert skills.social == 1


def test_award_xp_tracks_progress_without_leveling(monkeypatch):
    system = NPCSkillSystem()
    monkeypatch.setattr("src.narrative.npc_skills.random.random", lambda: 0.2)

    leveled = system.award_xp("npc-1", 5)

    skills = system.get_skills("npc-1")
    assert leveled is False
    assert skills.level == 1
    assert skills.xp == 5
    assert skills.combat == 1
    assert skills.tech == 1
    assert skills.social == 1
