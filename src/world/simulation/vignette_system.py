"""
Vignette System - Runtime matching of ambient event templates.
Subscribes to world events and generates contextual narrative encounters.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
import yaml
from pathlib import Path
import random


@dataclass
class VignetteTrigger:
    """Trigger condition for a vignette."""
    event_type: str
    conditions: Dict[str, Any]


@dataclass
class VignetteVariant:
    """Contextual variant of a vignette."""
    condition: str
    description: str
    outcomes: Dict[str, str]


@dataclass
class VignetteTemplate:
    """Template for an ambient vignette."""
    id: str
    name: str
    category: str
    triggers: List[VignetteTrigger]
    requirements: Dict[str, Any]
    description: str
    variants: List[VignetteVariant]
    npc_involvement: Dict[str, Any]


@dataclass
class ActiveVignette:
    """An active vignette instance."""
    vignette_id: str
    template: VignetteTemplate
    variant: Optional[VignetteVariant]
    context: Dict[str, Any]
    timestamp: float


class VignetteSystem:
    """Manages ambient vignette generation and matching."""
    
    def __init__(self, vignette_data_path: str = "data/events/ambient.yaml"):
        self.templates: Dict[str, VignetteTemplate] = {}
        self.active_vignettes: List[ActiveVignette] = []
        self.event_subscriptions: Dict[str, List[str]] = {}  # event_type -> [vignette_ids]
        self._vignette_counter = 0
        
        # Load templates
        self._load_templates(vignette_data_path)
    
    def _load_templates(self, path: str):
        """Load vignette templates from YAML."""
        yaml_path = Path(path)
        if not yaml_path.exists():
            print(f"Warning: Vignette data not found at {path}")
            return
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        for vignette_data in data.get('vignettes', []):
            # Parse triggers
            triggers = []
            for trigger_data in vignette_data.get('triggers', []):
                trigger = VignetteTrigger(
                    event_type=trigger_data.get('event_type', ''),
                    conditions=trigger_data
                )
                triggers.append(trigger)
            
            # Parse variants
            variants = []
            for variant_data in vignette_data.get('variants', []):
                variant = VignetteVariant(
                    condition=variant_data.get('condition', ''),
                    description=variant_data.get('description', ''),
                    outcomes=variant_data.get('outcomes', {})
                )
                variants.append(variant)
            
            # Create template
            template = VignetteTemplate(
                id=vignette_data['id'],
                name=vignette_data['name'],
                category=vignette_data['category'],
                triggers=triggers,
                requirements=vignette_data.get('requirements', {}),
                description=vignette_data['description'],
                variants=variants,
                npc_involvement=vignette_data.get('npc_involvement', {})
            )
            
            self.templates[template.id] = template
            
            # Register event subscriptions
            for trigger in triggers:
                event_type = trigger.event_type
                if event_type not in self.event_subscriptions:
                    self.event_subscriptions[event_type] = []
                self.event_subscriptions[event_type].append(template.id)
    
    def match_vignettes(self, events: List[Dict], game_state: Dict) -> List[ActiveVignette]:
        """
        Match events to vignette templates and generate active vignettes.
        
        Args:
            events: List of world events from simulation tick
            game_state: Current game state for context matching
            
        Returns:
            List of newly activated vignettes
        """
        new_vignettes = []
        
        # Group events by type
        events_by_type = {}
        for event in events:
            event_type = event.get('type')
            if event_type:
                if event_type not in events_by_type:
                    events_by_type[event_type] = []
                events_by_type[event_type].append(event)
        
        # Check each event type
        for event_type, event_list in events_by_type.items():
            # Get subscribed vignettes
            vignette_ids = self.event_subscriptions.get(event_type, [])
            
            for vignette_id in vignette_ids:
                template = self.templates.get(vignette_id)
                if not template:
                    continue
                
                # Check if vignette can trigger
                if self._can_trigger(template, events_by_type, game_state):
                    # Select best variant
                    variant = self._select_variant(template, game_state)
                    
                    # Create active vignette
                    self._vignette_counter += 1
                    vignette = ActiveVignette(
                        vignette_id=f"{vignette_id}_{self._vignette_counter}",
                        template=template,
                        variant=variant,
                        context=self._build_context(template, events_by_type, game_state),
                        timestamp=0.0  # Would use time.time() in production
                    )
                    
                    new_vignettes.append(vignette)
                    self.active_vignettes.append(vignette)
        
        return new_vignettes
    
    def _can_trigger(self, template: VignetteTemplate, events_by_type: Dict, game_state: Dict) -> bool:
        """Check if a vignette can trigger based on requirements."""
        requirements = template.requirements
        
        # Check all trigger conditions are met
        for trigger in template.triggers:
            if trigger.event_type not in events_by_type:
                return False
            
            # Check trigger-specific conditions
            for key, value in trigger.conditions.items():
                if key == 'event_type':
                    continue
                
                # Check if any event matches the condition
                matched = False
                for event in events_by_type[trigger.event_type]:
                    if self._check_condition(key, value, event):
                        matched = True
                        break
                
                if not matched:
                    return False
        
        # Check global requirements
        for req_key, req_value in requirements.items():
            if not self._check_requirement(req_key, req_value, game_state):
                return False
        
        return True
    
    def _check_condition(self, key: str, expected: Any, event: Dict) -> bool:
        """Check if an event matches a condition."""
        actual = event.get(key)
        
        if isinstance(expected, list):
            return actual in expected
        else:
            return actual == expected
    
    def _check_requirement(self, key: str, value: Any, game_state: Dict) -> bool:
        """Check if a requirement is met."""
        # Parse requirement key
        if key == 'min_traffic_density':
            # Would check actual traffic density from game state
            return True
        elif key == 'weather_severity':
            # Would check weather severity
            return True
        elif key == 'player_alone':
            # Would check if player has companions
            return True
        elif key == 'wildlife_density':
            # Would check wildlife density
            return True
        elif key == 'law_presence':
            # Would check law presence level
            return True
        elif key == 'settlement_density':
            # Would check settlement density
            return True
        elif key == 'player_bounty':
            # Would check player bounty amount
            character = game_state.get('character', {})
            # Simplified check
            return True
        elif key == 'player_reputation':
            # Would check player reputation
            return True
        
        return True
    
    def _select_variant(self, template: VignetteTemplate, game_state: Dict) -> Optional[VignetteVariant]:
        """Select the best matching variant for current context."""
        character = game_state.get('character', {})
        
        # Score each variant
        scored_variants = []
        for variant in template.variants:
            score = self._score_variant(variant, character)
            scored_variants.append((score, variant))
        
        # Sort by score (highest first)
        scored_variants.sort(key=lambda x: x[0], reverse=True)
        
        # Return best variant if score > 0, otherwise use base description
        if scored_variants and scored_variants[0][0] > 0:
            return scored_variants[0][1]
        
        return None
    
    def _score_variant(self, variant: VignetteVariant, character: Dict) -> float:
        """Score how well a variant matches the player's state."""
        condition = variant.condition
        score = 0.0
        
        # Check player state conditions
        if 'reputation_positive' in condition:
            # Check if player has positive reputation
            reputation = getattr(character, 'reputation', {}) if hasattr(character, 'reputation') else {}
            if any(rep > 0.3 for rep in reputation.values()):
                score += 1.0
        
        if 'reputation_negative' in condition:
            reputation = getattr(character, 'reputation', {}) if hasattr(character, 'reputation') else {}
            if any(rep < -0.3 for rep in reputation.values()):
                score += 1.0
        
        if 'wanted' in condition:
            crimes = getattr(character, 'crimes_committed', []) if hasattr(character, 'crimes_committed') else []
            if len(crimes) > 0:
                score += 1.0
        
        if 'honor' in condition:
            honor = getattr(character, 'honor', 0.5) if hasattr(character, 'honor') else 0.5
            if 'high' in condition and honor > 0.7:
                score += 1.0
            elif 'low' in condition and honor < 0.3:
                score += 1.0
        
        if 'ship_damaged' in condition:
            # Would check ship integrity
            score += 0.5
        
        if 'has_' in condition:
            # Generic "has X" check
            score += 0.5
        
        if 'charismatic' in condition or 'intimidating' in condition or 'cautious' in condition:
            # Personality-based variants
            score += 0.7
        
        return score
    
    def _build_context(self, template: VignetteTemplate, events_by_type: Dict, game_state: Dict) -> Dict:
        """Build context dictionary for the vignette."""
        context = {
            'template_id': template.id,
            'category': template.category,
            'events': []
        }
        
        # Collect relevant events
        for trigger in template.triggers:
            if trigger.event_type in events_by_type:
                context['events'].extend(events_by_type[trigger.event_type])
        
        # Add player state
        character = game_state.get('character', {})
        context['player'] = {
            'name': getattr(character, 'name', 'Unknown') if hasattr(character, 'name') else 'Unknown',
            'honor': getattr(character, 'honor', 0.5) if hasattr(character, 'honor') else 0.5,
            'crimes': len(getattr(character, 'crimes_committed', []) if hasattr(character, 'crimes_committed') else [])
        }
        
        return context
    
    def get_active_vignettes(self) -> List[ActiveVignette]:
        """Get all currently active vignettes."""
        return self.active_vignettes
    
    def resolve_vignette(self, vignette_id: str, outcome: str):
        """Resolve a vignette with a chosen outcome."""
        # Find and remove vignette
        self.active_vignettes = [v for v in self.active_vignettes if v.vignette_id != vignette_id]
    
    def get_vignette_description(self, vignette: ActiveVignette) -> str:
        """Get the full description for a vignette."""
        if vignette.variant:
            return vignette.variant.description
        return vignette.template.description
    
    def get_vignette_outcomes(self, vignette: ActiveVignette) -> Dict[str, str]:
        """Get available outcomes for a vignette."""
        if vignette.variant:
            return vignette.variant.outcomes
        return {}
    
    def to_dict(self) -> Dict:
        """Serialize state."""
        return {
            'active_vignettes': [
                {
                    'vignette_id': v.vignette_id,
                    'template_id': v.template.id,
                    'variant_condition': v.variant.condition if v.variant else None,
                    'context': v.context,
                    'timestamp': v.timestamp
                }
                for v in self.active_vignettes
            ],
            'vignette_counter': self._vignette_counter
        }
    
    @classmethod
    def from_dict(cls, data: Dict, vignette_data_path: str = "data/events/ambient.yaml") -> VignetteSystem:
        """Deserialize state."""
        system = cls(vignette_data_path)
        system._vignette_counter = data.get('vignette_counter', 0)
        
        # Restore active vignettes
        for v_data in data.get('active_vignettes', []):
            template = system.templates.get(v_data['template_id'])
            if template:
                # Find matching variant
                variant = None
                if v_data.get('variant_condition'):
                    for v in template.variants:
                        if v.condition == v_data['variant_condition']:
                            variant = v
                            break
                
                vignette = ActiveVignette(
                    vignette_id=v_data['vignette_id'],
                    template=template,
                    variant=variant,
                    context=v_data['context'],
                    timestamp=v_data['timestamp']
                )
                system.active_vignettes.append(vignette)
        
        return system
