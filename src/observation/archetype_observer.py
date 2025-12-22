"""
Archetype Observer - Watches player behavior and extracts archetype signals.

This module analyzes player actions, dialogue choices, and crisis responses
to identify which archetypes the player is exhibiting.
"""

from datetime import datetime
from typing import List, Dict, Optional
from src.narrative.archetype_types import BehaviorInstance
from src.config.archetype_config_loader import get_config_loader


class ArchetypeObserver:
    """
    Observes player behavior and extracts archetype signals.
    
    The observer doesn't make judgments about which archetype the player IS,
    it just records signals that suggest various archetypes. The inference
    engine will integrate these signals over time.
    """
    
    def __init__(self):
        self.config = get_config_loader()
        self.all_archetypes = self.config.get_archetype_names()
    
    def observe_dialogue(
        self,
        player_choice: str,
        context: str,
        scene_id: str,
        npc_involved: Optional[str] = None,
    ) -> BehaviorInstance:
        """
        Analyzes a dialogue choice for archetype signals.
        
        Args:
            player_choice: The dialogue option the player selected
            context: The situation/conversation context
            scene_id: ID of the current scene
            npc_involved: Name of NPC being talked to
            
        Returns:
            BehaviorInstance with archetype signals
        """
        signals = {}
        
        # Analyze the dialogue for each archetype's signals
        for archetype in self.all_archetypes:
            archetype_def = self.config.get_archetype(archetype)
            dialogue_signals = archetype_def.signals.get('dialogue', {})
            
            archetype_score = 0.0
            
            # Check each signal pattern
            for signal_name, weight in dialogue_signals.items():
                if self._matches_dialogue_signal(player_choice, signal_name):
                    archetype_score += weight
            
            if archetype_score > 0:
                signals[archetype] = archetype_score
        
        return BehaviorInstance(
            scene_id=scene_id,
            timestamp=datetime.now(),
            behavior_type="dialogue",
            behavior_description=player_choice,
            archetype_signals=signals,
            context=context,
            npc_involved=npc_involved,
        )
    
    def observe_action(
        self,
        action_description: str,
        context: str,
        scene_id: str,
        target: Optional[str] = None,
    ) -> BehaviorInstance:
        """
        Analyzes a physical action for archetype signals.
        
        Args:
            action_description: What the player did
            context: The situation context
            scene_id: ID of the current scene
            target: Who/what was affected
            
        Returns:
            BehaviorInstance with archetype signals
        """
        signals = {}
        
        for archetype in self.all_archetypes:
            archetype_def = self.config.get_archetype(archetype)
            action_signals = archetype_def.signals.get('action', {})
            
            archetype_score = 0.0
            
            for signal_name, weight in action_signals.items():
                if self._matches_action_signal(action_description, signal_name):
                    archetype_score += weight
            
            if archetype_score > 0:
                signals[archetype] = archetype_score
        
        return BehaviorInstance(
            scene_id=scene_id,
            timestamp=datetime.now(),
            behavior_type="action",
            behavior_description=action_description,
            archetype_signals=signals,
            context=context,
            npc_involved=target,
        )
    
    def observe_interrogation(
        self,
        approach: str,
        npc: str,
        context: str,
        scene_id: str,
        outcome: Optional[str] = None,
    ) -> BehaviorInstance:
        """
        Analyzes interrogation style.
        
        This is the crucible - primary source of archetype signals.
        
        Args:
            approach: How the player approached the interrogation
            npc: Who they're interrogating
            context: The situation
            scene_id: ID of the current scene
            outcome: What happened as a result
            
        Returns:
            BehaviorInstance with archetype signals
        """
        signals = {}
        
        for archetype in self.all_archetypes:
            archetype_def = self.config.get_archetype(archetype)
            interrogation_signals = archetype_def.signals.get('interrogation', {})
            
            archetype_score = 0.0
            
            for signal_name, weight in interrogation_signals.items():
                if self._matches_interrogation_signal(approach, signal_name):
                    archetype_score += weight
            
            if archetype_score > 0:
                signals[archetype] = archetype_score
        
        return BehaviorInstance(
            scene_id=scene_id,
            timestamp=datetime.now(),
            behavior_type="interrogation",
            behavior_description=approach,
            archetype_signals=signals,
            context=context,
            npc_involved=npc,
        )
    
    def observe_crisis_response(
        self,
        crisis_description: str,
        response: str,
        context: str,
        scene_id: str,
    ) -> BehaviorInstance:
        """
        How they respond under pressure reveals deep patterns.
        
        Args:
            crisis_description: What the crisis was
            response: How the player responded
            context: Additional context
            scene_id: ID of the current scene
            
        Returns:
            BehaviorInstance with archetype signals
        """
        signals = {}
        
        for archetype in self.all_archetypes:
            archetype_def = self.config.get_archetype(archetype)
            crisis_signals = archetype_def.signals.get('crisis', {})
            
            archetype_score = 0.0
            
            for signal_name, weight in crisis_signals.items():
                if self._matches_crisis_signal(response, signal_name):
                    archetype_score += weight
            
            if archetype_score > 0:
                signals[archetype] = archetype_score
        
        return BehaviorInstance(
            scene_id=scene_id,
            timestamp=datetime.now(),
            behavior_type="crisis",
            behavior_description=f"Crisis: {crisis_description} | Response: {response}",
            archetype_signals=signals,
            context=context,
        )
    
    # ========================================================================
    # Signal Matching Helpers
    # ========================================================================
    
    def _matches_dialogue_signal(self, dialogue: str, signal_name: str) -> bool:
        """Check if dialogue matches a signal pattern."""
        dialogue_lower = dialogue.lower()
        
        # Map signal names to detection patterns
        patterns = {
            "demanding_tone": ["demand", "tell me", "you will", "must", "need to know"],
            "impatient_interruption": ["enough", "get to the point", "hurry", "quickly"],
            "requires_explanation": ["explain", "why", "how", "justify"],
            "dismisses_feelings": ["don't care how you feel", "feelings don't matter", "irrelevant"],
            "moralistic_language": ["right", "wrong", "should", "shouldn't", "moral", "immoral"],
            "condemns_others": ["disgust", "pathetic", "weak", "failure", "shame"],
            "expresses_disgust": ["disgusting", "revolting", "sick", "vile"],
            "binary_thinking": ["always", "never", "either", "or", "black and white"],
            "deflects_personal_questions": ["not important", "doesn't matter", "let's talk about"],
            "changes_subject_when_emotional": ["anyway", "moving on", "what about"],
            "speaks_in_abstractions": ["in general", "theoretically", "abstractly"],
            "self_critical_language": ["not good enough", "failed", "mistake", "should have"],
            "points_out_flaws": ["but", "however", "actually", "wrong"],
            "never_satisfied": ["could be better", "not quite", "almost"],
            "emphasizes_own_suffering": ["i suffered", "i sacrificed", "i gave up"],
            "guilt_trips_others": ["after all i've done", "ungrateful", "owe me"],
            "refuses_help_dramatically": ["i'll do it myself", "don't need anyone"],
            "denounces_pleasure": ["indulgent", "wasteful", "excessive"],
            "praises_deprivation": ["discipline", "restraint", "sacrifice"],
            "suspicious_of_comfort": ["too easy", "suspicious", "trap"],
            "questions_motives": ["why really", "what do you want", "what's your angle"],
            "sees_conspiracies": ["they're all", "working together", "planned"],
            "refuses_to_share_information": ["need to know basis", "classified", "secret"],
            "corrects_others_constantly": ["actually", "technically", "to be precise"],
            "cites_sources_excessively": ["according to", "studies show", "research indicates"],
            "dismisses_intuition": ["no evidence", "unscientific", "illogical"],
            "mocks_idealism": ["naive", "unrealistic", "fairy tale"],
            "expects_worst": ["will fail", "won't work", "doomed"],
            "dismisses_positive_outcomes": ["luck", "fluke", "won't last"],
            "talks_about_leaving": ["get out", "leave", "escape", "move on"],
            "avoids_promises": ["maybe", "we'll see", "no promises"],
            "romanticizes_freedom": ["free", "unbound", "no ties"],
            "seeks_pleasure_constantly": ["fun", "enjoy", "pleasure", "feel good"],
            "avoids_discomfort": ["uncomfortable", "unpleasant", "rather not"],
            "dismisses_consequences": ["worry later", "deal with it then", "who cares"],
            "threatens_violence": ["hurt", "kill", "destroy", "break"],
            "glorifies_destruction": ["burn it", "tear it down", "smash"],
            "dismisses_creation": ["waste of time", "pointless", "futile"],
            "lies_casually": ["trust me", "would i lie", "honestly"],
            "makes_jokes_of_serious_things": ["haha", "funny", "joke"],
            "wears_masks": ["pretend", "act", "play the part"],
            "talks_about_self_constantly": ["i", "me", "my", "mine"],
            "dismisses_others_experiences": ["not as bad as", "you think that's"],
            "seeks_admiration": ["impressive", "amazing", "look at me"],
            "talks_about_dominance": ["weak", "strong", "power", "control"],
            "identifies_weakness": ["vulnerable", "soft spot", "weakness"],
            "threatens_subtly": ["would be a shame", "unfortunate", "careful"],
            "uses_guilt": ["disappoint", "let down", "after everything"],
            "gaslights": ["didn't happen", "imagining", "crazy"],
            "plays_victim": ["poor me", "always happens to me", "unfair"],
            "downplays_achievements": ["luck", "anyone could", "not that hard"],
            "fears_being_found_out": ["what if they know", "discover", "exposed"],
            "attributes_success_to_luck": ["got lucky", "right place", "timing"],
            "offers_help_constantly": ["let me help", "i can fix", "i'll take care"],
            "dismisses_own_needs": ["i'm fine", "don't worry about me", "not important"],
            "sees_others_as_projects": ["fix", "save", "rescue"],
            "talks_about_revenge": ["pay back", "get even", "make them suffer"],
            "holds_grudges": ["remember when", "never forget", "haven't forgiven"],
            "justifies_excessive_punishment": ["deserve", "had it coming", "justice"],
            "expresses_fear_constantly": ["scared", "afraid", "terrified", "dangerous"],
            "suggests_retreat": ["run", "hide", "get away", "too risky"],
            "rationalizes_cowardice": ["smart", "tactical", "live to fight"],
            "talks_about_the_cause": ["for the cause", "greater good", "mission"],
            "dismisses_individual_concerns": ["sacrifice", "necessary", "for the many"],
            "justifies_harm_for_greater_good": ["ends justify", "necessary evil"],
            "agrees_with_everyone": ["you're right", "i agree", "absolutely"],
            "gives_false_praise": ["amazing", "perfect", "brilliant"],
            "avoids_disagreement": ["sure", "whatever you say", "if you think so"],
        }
        
        signal_patterns = patterns.get(signal_name, [])
        return any(pattern in dialogue_lower for pattern in signal_patterns)
    
    def _matches_action_signal(self, action: str, signal_name: str) -> bool:
        """Check if action matches a signal pattern."""
        action_lower = action.lower()
        
        patterns = {
            "searches_without_permission": ["search", "look through", "rummage", "without asking"],
            "manipulates_for_information": ["trick", "deceive", "manipulate", "lie to get"],
            "creates_detailed_logs": ["log", "record", "document", "note"],
            "overrides_others_decisions": ["override", "ignore", "disregard", "my way"],
            "refuses_to_help_flawed_people": ["refuse", "won't help", "not worth"],
            "punishes_perceived_wrongdoing": ["punish", "penalize", "make pay"],
            "avoids_morally_gray_situations": ["avoid", "stay away", "not my problem"],
            "leaves_conversations_early": ["leave", "walk away", "exit"],
            "avoids_social_gatherings": ["skip", "avoid", "stay away"],
            "disappears_when_needed": ["disappear", "vanish", "gone"],
            "redoes_work_repeatedly": ["redo", "start over", "not good enough"],
            "criticizes_others_work": ["criticize", "point out flaws", "wrong"],
            "avoids_tasks_they_might_fail": ["avoid", "too risky", "might fail"],
            "takes_on_unnecessary_burdens": ["take on", "burden", "my responsibility"],
            "makes_sacrifices_publicly": ["sacrifice", "give up", "for you"],
            "keeps_score_of_favors": ["remember", "owe", "did for you"],
            "refuses_comfort_items": ["refuse", "don't need", "too much"],
            "lives_spartanly": ["minimal", "bare", "simple"],
            "judges_others_indulgence": ["wasteful", "excessive", "indulgent"],
            "checks_for_surveillance": ["check", "look for cameras", "sweep"],
            "tests_others_loyalty": ["test", "see if", "prove"],
            "keeps_secrets_unnecessarily": ["secret", "can't tell", "classified"],
            "insists_on_proper_procedure": ["procedure", "protocol", "by the book"],
            "refuses_shortcuts": ["no shortcuts", "proper way", "follow rules"],
            "lectures_instead_of_helping": ["lecture", "explain", "teach"],
            "sabotages_hopeful_plans": ["sabotage", "won't work", "ruin"],
            "refuses_to_try": ["won't try", "pointless", "waste of time"],
            "spreads_negativity": ["negative", "pessimistic", "doom"],
            "keeps_escape_routes": ["escape route", "exit", "way out"],
            "avoids_long_term_plans": ["avoid commitment", "short term", "temporary"],
            "leaves_when_things_get_hard": ["leave", "quit", "abandon"],
            "indulges_excessively": ["indulge", "excess", "overdo"],
            "avoids_hard_work": ["avoid work", "easy way", "shortcut"],
            "uses_others_for_gratification": ["use", "take advantage", "for pleasure"],
            "breaks_things": ["break", "smash", "destroy"],
            "escalates_to_violence": ["attack", "fight", "violence"],
            "sabotages_others_work": ["sabotage", "ruin", "destroy"],
            "deceives_unnecessarily": ["lie", "deceive", "trick"],
            "plays_pranks_that_hurt": ["prank", "joke", "trick"],
            "manipulates_for_fun": ["manipulate", "mess with", "play"],
            "makes_everything_about_themselves": ["about me", "my story", "i"],
            "uses_others_for_validation": ["validate", "praise", "admire"],
            "ignores_others_needs": ["ignore", "don't care", "not important"],
            "targets_vulnerable": ["target", "prey on", "exploit weak"],
            "exploits_others": ["exploit", "use", "take advantage"],
            "intimidates": ["intimidate", "threaten", "scare"],
            "manipulates_situations": ["manipulate", "control", "orchestrate"],
            "controls_through_deception": ["deceive", "lie", "trick"],
            "creates_dependencies": ["depend", "need me", "rely on"],
            "takes_credit_for_others_work": ["take credit", "my idea", "i did"],
            "avoids_challenges": ["avoid", "too hard", "can't"],
            "overcompensates": ["overcompensate", "prove", "show"],
            "rescues_unnecessarily": ["rescue", "save", "help"],
            "creates_dependency": ["make dependent", "need me", "rely"],
            "refuses_help": ["refuse help", "alone", "myself"],
            "seeks_revenge": ["revenge", "payback", "get even"],
            "punishes_excessively": ["punish", "hurt", "make suffer"],
            "can't_let_go": ["hold on", "remember", "never forget"],
            "avoids_danger": ["avoid", "stay safe", "too dangerous"],
            "uses_others_as_shields": ["use as shield", "hide behind", "protect me"],
            "abandons_others": ["abandon", "leave behind", "save myself"],
            "sacrifices_others_for_cause": ["sacrifice", "for the cause", "necessary"],
            "refuses_compromise": ["no compromise", "all or nothing", "my way"],
            "forces_beliefs_on_others": ["force", "must believe", "convert"],
            "enables_bad_behavior": ["enable", "allow", "permit"],
            "refuses_to_confront": ["avoid confrontation", "let it go", "ignore"],
            "seeks_approval_constantly": ["approve", "like me", "accept"],
        }
        
        signal_patterns = patterns.get(signal_name, [])
        return any(pattern in action_lower for pattern in signal_patterns)
    
    def _matches_interrogation_signal(self, approach: str, signal_name: str) -> bool:
        """Check if interrogation approach matches a signal pattern."""
        approach_lower = approach.lower()
        
        patterns = {
            "threatening_approach": ["threaten", "intimidate", "force"],
            "refuses_ambiguity": ["need certainty", "clear answer", "yes or no"],
            "demands_certainty": ["must know", "tell me exactly", "precise"],
            "judgmental_tone": ["judge", "condemn", "disgust"],
            "focuses_on_moral_failings": ["wrong", "immoral", "sin"],
            "emotionally_distant": ["facts only", "emotions aside", "objective"],
            "focuses_on_facts_not_feelings": ["facts", "evidence", "proof"],
            "assumes_deception": ["lying", "deceiving", "hiding"],
            "sets_traps": ["trap", "catch", "trick"],
            "focuses_on_technicalities": ["technically", "precisely", "exactly"],
            "demands_precise_language": ["precise", "exact", "specific"],
            "assumes_guilt": ["guilty", "did it", "know you"],
            "focuses_on_failures": ["failed", "mistake", "wrong"],
            "evasive": ["evade", "dodge", "avoid"],
            "keeps_options_open": ["maybe", "possibly", "we'll see"],
            "distracted_by_comfort": ["comfortable", "relax", "easy"],
            "avoids_difficult_topics": ["avoid", "change subject", "not that"],
            "intimidates": ["intimidate", "scare", "threaten"],
            "threatens": ["threaten", "or else", "consequences"],
            "misdirects": ["misdirect", "distract", "confuse"],
            "tells_half_truths": ["half truth", "partial", "some"],
            "redirects_to_self": ["about me", "my experience", "i"],
            "seeks_praise": ["good job", "well done", "impressive"],
            "hunts_for_weakness": ["weakness", "vulnerable", "soft spot"],
            "exploits_fear": ["afraid", "scared", "fear"],
            "twists_words": ["twist", "manipulate", "reframe"],
            "uses_emotional_manipulation": ["guilt", "pity", "sympathy"],
            "deflects_praise": ["not me", "luck", "anyone"],
            "fears_scrutiny": ["don't look", "private", "personal"],
            "focuses_on_helping": ["help", "fix", "solve"],
            "avoids_own_issues": ["not about me", "focus on you"],
            "focuses_on_past_wrongs": ["remember", "did to me", "wronged"],
            "demands_retribution": ["pay", "justice", "punishment"],
            "fearful": ["scared", "afraid", "dangerous"],
            "seeks_safety": ["safe", "secure", "protected"],
            "focuses_on_ideology": ["cause", "belief", "principle"],
            "dismisses_nuance": ["simple", "clear", "black and white"],
            "tells_people_what_they_want_to_hear": ["agree", "right", "exactly"],
            "avoids_hard_truths": ["avoid", "not ready", "later"],
        }
        
        signal_patterns = patterns.get(signal_name, [])
        return any(pattern in approach_lower for pattern in signal_patterns)
    
    def _matches_crisis_signal(self, response: str, signal_name: str) -> bool:
        """Check if crisis response matches a signal pattern."""
        response_lower = response.lower()
        
        patterns = {
            "takes_charge_immediately": ["take charge", "i'll handle", "follow me"],
            "ignores_others_input": ["ignore", "my way", "don't care"],
            "condemns_before_understanding": ["condemn", "wrong", "guilty"],
            "refuses_to_compromise": ["no compromise", "my way", "all or nothing"],
            "withdraws_instead_of_engaging": ["withdraw", "retreat", "hide"],
            "goes_silent": ["silent", "quiet", "nothing"],
            "freezes_from_fear_of_failure": ["freeze", "can't", "too scared"],
            "becomes_hypercritical": ["criticize", "wrong", "mistake"],
            "volunteers_to_suffer": ["i'll do it", "sacrifice", "take the pain"],
            "makes_it_about_themselves": ["about me", "my pain", "i suffer"],
            "refuses_necessary_comforts": ["refuse", "don't need", "suffer"],
            "becomes_more_austere": ["stricter", "harsher", "more discipline"],
            "suspects_everyone": ["suspect", "trust no one", "all guilty"],
            "acts_preemptively": ["strike first", "before they", "preemptive"],
            "freezes_without_data": ["need data", "no information", "can't decide"],
            "becomes_more_rigid": ["rules", "procedure", "by the book"],
            "gives_up_immediately": ["give up", "pointless", "why try"],
            "mocks_those_who_try": ["mock", "foolish", "waste"],
            "runs_away": ["run", "flee", "escape"],
            "abandons_others": ["abandon", "leave", "save myself"],
            "seeks_escape_through_pleasure": ["drink", "drugs", "pleasure"],
            "ignores_problem": ["ignore", "not my problem", "avoid"],
            "resorts_to_violence": ["attack", "fight", "violence"],
            "destroys_to_solve": ["destroy", "break", "smash"],
            "lies_to_escape": ["lie", "deceive", "trick"],
            "uses_deception": ["deceive", "manipulate", "misdirect"],
            "concerned_with_image": ["how do i look", "reputation", "image"],
            "uses_crisis_for_attention": ["look at me", "poor me", "attention"],
            "attacks_the_weak": ["attack weak", "easy target", "vulnerable"],
            "takes_advantage": ["advantage", "exploit", "use"],
            "manipulates_to_escape": ["manipulate", "trick", "deceive"],
            "uses_others_as_shields": ["shield", "hide behind", "protect me"],
            "fears_exposure": ["exposed", "found out", "discovered"],
            "becomes_defensive": ["defensive", "not my fault", "blame"],
            "must_be_the_hero": ["i'll save", "hero", "rescue"],
            "can't_accept_help": ["refuse help", "alone", "myself"],
            "seeks_vengeance": ["revenge", "payback", "vengeance"],
            "escalates_punishment": ["punish", "hurt", "make pay"],
            "sacrifices_others": ["sacrifice them", "for the cause", "necessary"],
            "agrees_to_avoid_conflict": ["agree", "whatever", "fine"],
            "enables_harm": ["allow", "let it happen", "enable"],
        }
        
        signal_patterns = patterns.get(signal_name, [])
        return any(pattern in response_lower for pattern in signal_patterns)
