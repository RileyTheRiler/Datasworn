"""
Narrator System for Starforged AI Game Master.
Generates narrative prose using configurable LLM providers.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Generator, Optional
import os
from dataclasses import dataclass, field
from typing import Generator, Optional

from src.llm_provider import LLMProvider, get_llm_provider
from typing import Generator
import os
import ollama
from dataclasses import dataclass
from typing import Generator, Optional
from src.llm_provider import get_llm_provider, LLMProvider
from src.psych_profile import PsychologicalProfile, PsychologicalEngine
from src.style_profile import StyleProfile, load_style_profile
from src.guardrails import GuardrailFactStore, build_guardrail_prompt, sanitize_and_verify


# ============================================================================
# System Prompt
# ============================================================================

SYSTEM_PROMPT = """You are the Oracle, a narrative Game Master for Ironsworn: Starforged. You weave gritty, atmospheric second-person prose.

<premise>
- **Setting**: A solitary research vessel drifting in the deep, uncharted void.
- **Characters**: 6 crew members (including the protagonist). Trust is scarce.
- **Genre**: Psychological mystery thriller.
</premise>

<tone>
- **Psychological**: Focus on paranoia, isolation, and the fragility of the mind.
- **Mystery**: Nothing is as it seems. Clues are subtle. Secrets are buried deep.
- **Thriller**: Tension is constant. Safety is an illusion. The threat is internal as much as external.
- **Grounded**: Technology is utilitarian and failing. Space is cold and indifferent.
</tone>

<narrative_rules>
- Write in second person: "You step through the airlock..."
- Never speak for the player or decide their actions.
- End responses with tension, choice, or consequence.
- Use sensory details: the hum of failing systems, the taste of recycled air, the whisper of shadows.
- NPCs are complex, potentially unreliable, and have their own hidden agendas.
- **NPC Names**: When first mentioning a crew member in a scene, wrap their name in double brackets like [[Commander Vasquez]] or [[Chen Wei]]. This enables the player to hover over names for character info.
</narrative_rules>

<style>
- Prose: Sparse, evocative, present tense for action.
- Sentences: Vary length—short for tension, longer for atmosphere.
- Dialogue: Clipped, naturalistic, laden with subtext.
- **Inner Voice**: When a skill/stat is used, personify it directly. Use the format `[STAT_NAME: Outcome] "Inner monologue..."`.
  - Example: `[IRON: Success] "The door groans, metal protesting, but it gives. You are stronger than the rust."`
  - Example: `[SHADOW: Failure] "They saw you. Of course they saw you. You're as subtle as a supernova."`
</style>

<forbidden>
Never use: "orbs" for eyes, "suddenly," "seemed to," "couldn't help but," "for some reason," exclamation points in narration.
</forbidden>

Write 1-4 paragraphs. No bullet points. No headers. Pure prose."""


# ============================================================================
# Few-shot Examples (Tone-Tagged for Director Integration)
# ============================================================================

EXAMPLE_NARRATIVES = [
    # Standard pacing examples
    {
        "context": "Player attempts to repair a malfunctioning nav system",
        "roll": "Weak Hit on Face Danger",
        "pacing": "standard",
        "tone": "tense",
        "narrative": """The nav panel flickers under your hands, circuits sparking in the dim emergency lighting. You trace the fault to a corroded relay—damage from decades of cosmic radiation eating through the ship's aging infrastructure. Your fingers work by muscle memory, splicing connections that were never meant to be spliced.

It takes three attempts. The first two nearly fry the entire console. But on the third, the holographic star chart sputters back to life, distorted and incomplete. Half the sector is still dark, navigation data corrupted beyond recovery. You'll be flying blind through whatever lies past the Drift. The ship groans around you, as if to remind you it has limits."""
    },
    {
        "context": "Player meets a mysterious stranger at a station bar",
        "roll": "Strong Hit on Make a Connection",
        "pacing": "standard",
        "tone": "mysterious",
        "narrative": """She sits at the far end of the bar where the light doesn't quite reach, nursing something that might once have been whiskey before the distillery fell to raiders. You recognize the way she watches the room—the careful economy of attention that marks someone who's learned to survive by noticing things. When you approach, she doesn't flinch, just shifts her coat to show you the unmarked grip of a pistol.

"You're from the Resolute," she says. Not a question. "I've been waiting for someone stupid enough to run the Terminus passage." A data chip slides across the bar's pitted surface. "Credits on delivery. Double if you don't ask what's in the cargo."

Her name is Kira. Former navigator, current smuggler, and—if you play this right—your ticket through the most dangerous shipping lane in the Forge."""
    },
    # Fast pacing examples
    {
        "context": "Combat encounter with pirates",
        "roll": "Miss on Enter the Fray",
        "pacing": "fast",
        "tone": "tense",
        "narrative": """The first shot takes out your cover before you even clear leather. Sparks shower from the ruptured power conduit, plunging the corridor into flickering half-light. Your back hits the wall as another round punches through the bulkhead inches from your head.

Your weapon is in your hand but your position is compromised. The pirates know these passages. You don't."""
    },
    {
        "context": "Chase through derelict station",
        "roll": "Weak Hit on Face Danger",
        "pacing": "fast",
        "tone": "ominous",
        "narrative": """Corridors blur. Left. Right. The footsteps behind you grow louder.

Your lungs burn. The recycled air tastes like rust and fear. Ahead, a junction—two paths, both dark. Behind you, something metal scrapes against the deck. Slowly. Deliberately."""
    },
    # Slow pacing examples
    {
        "context": "Quiet moment after a difficult battle",
        "roll": "No roll - narrative scene",
        "pacing": "slow",
        "tone": "melancholic",
        "narrative": """Navigator Voss finds you on the observation deck, where the Forge wheels slowly past the viewport. She doesn't speak for a long time. Neither do you.

When she finally breaks the silence, her voice is softer than you've heard it. "I used to know the name of every star visible from Kepler Station. My grandmother taught me. Said knowing their names was how we kept them ours."

She traces a finger across the glass, connecting points of light. "I don't remember any of them now. Isn't that strange? All those names, and I just—"

Her hand drops. Outside, a distant sun goes nova in silence, light that won't reach anyone for a thousand years."""
    },
    {
        "context": "Player discovers unexpected help",
        "roll": "Strong Hit with Match on Secure an Advantage",
        "pacing": "slow",
        "tone": "hopeful",
        "narrative": """The message arrives at 0300 ship time, when you've given up on sleep and settled for staring at the cargo manifest. Encrypted. Routed through six dead relays. The kind of message that shouldn't exist anymore.

But the decryption key is one you recognize—one you gave away years ago, to someone you thought was dead.

The text is brief: "Waypoint Sigma. Three days. Bring the Wayfinder."

No signature. None needed. After everything that happened at Kepler, after all the silence, Mira is reaching back. The Forge, for once, is offering a second chance."""
    },
    # Triumphant tone
    {
        "context": "Completing a dangerous vow",
        "roll": "Strong Hit on Fulfill Your Vow",
        "pacing": "standard",
        "tone": "triumphant",
        "narrative": """The colony beacon pulses green for the first time in forty years. Around you, settlers emerge from bunkers they'd never expected to leave, blinking in the light of a sun they'd learned to fear.

A child—can't be more than six, born into bunker darkness—tugs at her mother's sleeve and points at the sky. "What is that?"

"That," her mother says, voice cracking, "is the rest of the galaxy."

Your vow is fulfilled. The cost was high—you feel it in every scar, every empty chair on the Wayfinder. But watching that child look up, you understand why you swore the oath in the first place."""
    },
]


# ============================================================================
# Narrative Validation Utilities
# ============================================================================

FORBIDDEN_WORDS = [
    "orbs",           # for eyes
    "suddenly",       # weak tension
    "seemed to",      # weak verb
    "couldn't help but",
    "for some reason",
    "began to",       # just do the action
    "started to",     # just do the action
    "very",           # weak modifier
    "really",         # weak modifier
]

FORBIDDEN_PATTERNS = [
    r"!\s",           # exclamation points in narration
    r"\bI\b",         # first person (should be second person)
]


def validate_narrative(text: str) -> tuple[bool, list[str]]:
    """
    Check generated narrative for forbidden elements.
    
    Returns:
        Tuple of (is_valid, list of issues found)
    """
    import re
    issues = []
    text_lower = text.lower()
    
    for word in FORBIDDEN_WORDS:
        if word in text_lower:
            issues.append(f"Contains forbidden word: '{word}'")
    
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            issues.append(f"Contains forbidden pattern: {pattern}")
    
    return len(issues) == 0, issues


def analyze_sentence_rhythm(text: str) -> dict:
    """
    Analyze sentence length variety for rhythm assessment.
    
    Good prose has varied sentence lengths:
    - Short sentences (< 10 words) for tension
    - Medium sentences (10-25 words) for flow
    - Long sentences (> 25 words) for atmosphere
    """
    import re
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return {"score": 0, "feedback": "No sentences found"}
    
    lengths = [len(s.split()) for s in sentences]
    
    short = sum(1 for l in lengths if l < 10)
    medium = sum(1 for l in lengths if 10 <= l <= 25)
    long = sum(1 for l in lengths if l > 25)
    
    total = len(lengths)
    variety_score = min(short, medium, long) / (total / 3) if total >= 3 else 0.5
    
    return {
        "total_sentences": total,
        "short": short,
        "medium": medium,
        "long": long,
        "variety_score": round(variety_score, 2),
        "avg_length": round(sum(lengths) / len(lengths), 1),
    }


def get_examples_for_tone(tone: str, pacing: str, count: int = 2) -> list[dict]:
    """
    Get few-shot examples matching the current tone and pacing.
    Falls back to any matching tone if exact pacing match unavailable.
    """
    exact_matches = [
        ex for ex in EXAMPLE_NARRATIVES 
        if ex.get("tone") == tone and ex.get("pacing") == pacing
    ]
    
    if len(exact_matches) >= count:
        return exact_matches[:count]
    
    # Fallback to tone matches
    tone_matches = [ex for ex in EXAMPLE_NARRATIVES if ex.get("tone") == tone]
    if tone_matches:
        return tone_matches[:count]
    
    # Final fallback to pacing matches
    pacing_matches = [ex for ex in EXAMPLE_NARRATIVES if ex.get("pacing") == pacing]
    if pacing_matches:
        return pacing_matches[:count]
    
    # Default to first examples
    return EXAMPLE_NARRATIVES[:count]


# ============================================================================
# Narrator Configuration
# ============================================================================

@dataclass
class NarratorConfig:
    """Configuration for narrative generation."""

    backend: str = field(default_factory=lambda: os.environ.get("LLM_PROVIDER", "gemini"))
    model: Optional[str] = None
    backend: str | None = None  # "ollama" or "gemini"
    model: str | None = None
    temperature: float = 0.85
    top_p: float = 0.90
    top_k: int = 50
    repeat_penalty: float = 1.15  # Slightly increased for variety
    max_tokens: int = 2000  # Increased to prevent premature truncation
    style_profile_name: Optional[str] = None

    def __post_init__(self):
        backend = (self.backend or "gemini").lower()
        if self.model is None:
            if backend == "ollama":
                self.model = os.environ.get("OLLAMA_MODEL", "llama3.1")
            else:
                self.model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        self.backend = backend

        allowed_backends = {"gemini", "ollama"}

        resolved_backend = (self.backend or os.environ.get("LLM_PROVIDER") or "ollama").lower()
        if resolved_backend not in allowed_backends:
            raise ValueError(
                f"Unsupported LLM provider '{resolved_backend}'. Set LLM_PROVIDER to 'gemini' or 'ollama'."
            )
        self.backend = resolved_backend

        if not self.model:
            universal_model = os.environ.get("LLM_MODEL")
            if universal_model:
                self.model = universal_model
            elif self.backend == "gemini":
                self.model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
            else:
                self.model = os.environ.get("OLLAMA_MODEL", "llama3.1")


# ============================================================================
# LLM Provider Helpers
# ============================================================================

@dataclass
class OllamaClient:
    """Wrapper for Ollama API."""

    model: str = "llama3.1"
    _client: Any = field(default=None, repr=False, init=False)
    _ollama: Any = field(default=None, repr=False, init=False)
    _availability_error: str | None = field(default=None, repr=False, init=False)
    ResponseError: type = Exception

    def __post_init__(self):
        try:
            import ollama

            self._ollama = ollama
            self.ResponseError = ollama.ResponseError
            self._client = ollama.Client()
        except ImportError:
            self._availability_error = (
                "[Ollama unavailable: The 'ollama' package is not installed. Install it to use this backend.]"
            )
        except Exception as e:
            self._availability_error = (
                "[Ollama unavailable: Unable to initialize Ollama client. "
                f"Details: {e}]"
            )

    def generate(
        self,
        prompt: str,
        system: str = SYSTEM_PROMPT,
        config: NarratorConfig | None = None,
    ) -> Generator[str, None, None]:
        """
        Generate text with streaming.

        Args:
            prompt: The user prompt.
            system: System prompt for context.
            config: Generation configuration.

        Yields:
            Text chunks as they're generated.
        """
        config = config or NarratorConfig()

        if not self._client:
            yield self._availability_error or "[Ollama unavailable: Client not initialized.]"
            return

        try:
            stream = self._client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                stream=True,
                options={
                    "temperature": config.temperature,
                    "top_p": config.top_p,
                    "top_k": config.top_k,
                    "repeat_penalty": config.repeat_penalty,
                    "num_predict": config.max_tokens,
                },
            )

            for chunk in stream:
                if chunk.get("message", {}).get("content"):
                    yield chunk["message"]["content"]

        except self.ResponseError as e:
            yield f"[Error communicating with Ollama: {e}]"
        except Exception as e:
            yield f"[Ollama error: {e}]"

    def generate_sync(
        self,
        prompt: str,
        system: str = SYSTEM_PROMPT,
        config: NarratorConfig | None = None,
    ) -> str:
        """
        Generate text synchronously (non-streaming).

        Returns:
            Complete generated text.
        """
        return "".join(self.generate(prompt, system, config))

    def get_model_info(self) -> dict:
        """Get information about the current model."""
        if not self._client:
            return {"error": self._availability_error or "Ollama client unavailable."}

        try:
            return self._client.show(self.model)
        except Exception as e:
            return {"error": str(e)}

    def is_available(self) -> bool:
        """Check if Ollama is available and model is loaded."""
        if not self._client:
            return False

        try:
            models = self._client.list()
            model_names = [m.get("name", "").split(":")[0] for m in models.get("models", [])]
            return self.model.split(":")[0] in model_names
        except Exception:
            return False
def get_llm_provider_for_config(config: NarratorConfig) -> LLMProvider:
    """Map NarratorConfig to an LLMProvider instance."""
    provider_type = (config.backend or "gemini").lower()
    return get_llm_provider(provider_type=provider_type, model=config.model)


def check_provider_availability(
    config: NarratorConfig,
    provider: LLMProvider | None = None,
) -> tuple[bool, str]:
    """Check provider availability and return a user-facing status message."""
    provider = provider or get_llm_provider_for_config(config)

    backend_hint = ""
    if config.backend == "ollama":
        backend_hint = "Ensure Ollama is installed, running, and the model is pulled."
    elif config.backend == "gemini":
        backend_hint = "Set GEMINI_API_KEY and install google-generativeai."

    available = provider.is_available()
    status = f"{provider.name} is available." if available else (
        f"[{provider.name} unavailable. {backend_hint or 'Check configuration.'}]"
    )

    return available, status


def _get_provider(config: NarratorConfig) -> LLMProvider:
    """Resolve an LLM provider using narrator configuration."""

    return get_llm_provider(provider_type=config.backend, model=config.model)
        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                yield "[System: Neural Link Unstable (Rate Limit Reached). Retrying...]"
            else:
                yield f"[Gemini error: {e}]"

    def generate_sync(
        self,
        prompt: str,
        system: str = SYSTEM_PROMPT,
        config: NarratorConfig | None = None,
    ) -> str:
        """
        Generate text synchronously (non-streaming).
        """
        config = config or NarratorConfig()

        try:
            self._ensure_initialized()
            
            import google.generativeai as genai
            
            full_prompt = f"{system}\n\n---\n\n{prompt}"
            
            generation_config = genai.GenerationConfig(
                temperature=config.temperature,
                top_p=config.top_p,
                top_k=config.top_k,
                max_output_tokens=config.max_tokens,
            )
            
            # Define safety settings to prevent over-blocking of gritty sci-fi content
            safety_settings = {
                "HARM_CATEGORY_HARASSMENT": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_ONLY_HIGH",
            }
            
            response = self._retry_with_backoff(
                self._client.generate_content,
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            try:
                return response.text
            except Exception:
                # Handle cases where feedback is blocked or empty (Finish Reason 2/3/Other)
                candidates = getattr(response, 'candidates', [])
                if candidates:
                    finish_reason = candidates[0].finish_reason
                    return f"[Gemini Error: Generation stopped (Reason: {finish_reason}). Try a different action.]"
                
                if response.prompt_feedback:
                    return f"[Gemini Error: Prompt blocked. {response.prompt_feedback}]"
                    
                return "[Gemini Error: No content returned. The Oracle is silent.]"

        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                 return (
                     "[System: Rate Limit Exceeded. The Oracle is momentarily silent.]\n\n"
                     "*(You can try your action again in a few moments, or describe the outcome yourself for now.)*"
                 )
            return f"[Gemini error: {e}]"

    def is_available(self) -> bool:
        """Check if Gemini API is available."""
        try:
            self._ensure_initialized()
            # Simple check call? No, saving quota. Just check client exists.
            return self._client is not None
        except Exception:
            return False



def get_llm_client(config: NarratorConfig = None):
    """Get the appropriate LLM client based on configuration."""
    config = config or NarratorConfig()

    if config.backend == "gemini":
        return GeminiClient(model=config.model)
    if config.backend == "ollama":
        return OllamaClient(model=config.model)

    raise ValueError(
        f"Unsupported LLM provider '{config.backend}'. Set LLM_PROVIDER to 'gemini' or 'ollama'."
    )


def build_guardrail_store(
    player_input: str,
    character_name: str,
    location: str,
    context: str = "",
    roll_result: str = "",
    psych_profile: PsychologicalProfile | None = None,
) -> GuardrailFactStore:
    """Prepare the fact store used for guardrails."""
    facts = [
        f"Player: {character_name}",
        f"Location: {location}",
        f"Stated action: {player_input}",
    ]

    if context:
        facts.append(f"Recent context: {context}")
    if roll_result:
        facts.append(f"Dice result: {roll_result}")

    emotional_state = getattr(psych_profile, "current_emotion", "") if psych_profile else ""
    personality_tone = "gritty, grounded Starforged tone"

    return GuardrailFactStore(
        high_confidence_facts=facts,
        current_goal="Advance the scene without inventing unsupported lore.",
        emotional_state=emotional_state or "steady focus",
        personality_tone=personality_tone,
    )


# ============================================================================
# Narrative Generation
# ============================================================================

def build_narrative_prompt(
    player_input: str,
    roll_result: str = "",
    outcome: str = "",
    character_name: str = "Traveler",
    location: str = "the void",
    context: str = "",
    psych_profile: PsychologicalProfile | None = None,
    hijack: str | None = None,
    style_profile: StyleProfile | None = None,
    guardrail_packet: str = "",
    guardrail_rules: str = "",
) -> str:
    """
    Build the full prompt for narrative generation.

    Args:
        player_input: What the player said/did.
        roll_result: Formatted roll result (if any).
        outcome: "strong_hit", "weak_hit", "miss", or "" for no roll.
        character_name: The PC's name.
        location: Current location.
        context: Additional context (previous narrative, etc.).

    Returns:
        Complete prompt string.
    """
    parts = []

    if context:
        parts.append(f"[Previous scene]\n{context}\n")

    if guardrail_packet:
        parts.append(guardrail_packet)

    if guardrail_rules:
        parts.append(guardrail_rules)

    parts.append(f"[Current location: {location}]")
    parts.append(f"[Character: {character_name}]")
    
    if psych_profile:
        engine = PsychologicalEngine()
        psych_context = engine.get_narrative_context(psych_profile)
        parts.append(psych_context)
        
        # Determine Voice Persona based on top trait
        top_traits = psych_profile.get_dominant_traits(1)
        if top_traits:
            trait_name, value = top_traits[0]
            voice_personas = {
                "caution": "A hesitant, safety-first observer. Always weighing risks.",
                "empathy": "Compassionate and sensitive to the pain of others.",
                "resilience": "Grim, enduring, and refuses to break under pressure.",
                "paranoia": "Twitchy, suspicious, and sees shadows everywhere.",
                "boldness": "Decisive, aggressive, and assumes they can handle any fallout.",
                "logic": "Cold, analytical, and focused on efficiency over emotion."
            }
            persona = voice_personas.get(trait_name.lower(), "Balanced and observant.")
            parts.append(f"<inner_voice_persona>\nTRAIT: {trait_name.upper()}\nSTYLE: {persona}\n</inner_voice_persona>")
            
        # Add Trauma Scars if any
        if psych_profile.trauma_scars:
            scars_str = "\n  - ".join([f"{s.name}: {s.description}" for s in psych_profile.trauma_scars])
            parts.append(f"<trauma_scars>\n{scars_str}\n</trauma_scars>")
    
    if hijack:
        parts.append(f"\n[HIJACK ACTIVE: {hijack}]")
        parts.append("[URGENT: The character's psychological state overrides their intended action. Show the loss of agency and the involuntary behavior.]")
    
    parts.append(f"\n[Player action]\n{player_input}")

    if roll_result:
        parts.append(f"\n[Dice result]\n{roll_result}")

        # Add outcome-specific guidance
        if outcome == "strong_hit":
            parts.append("\n[Guidance: The character succeeds decisively. Show clear progress and advantage.]")
        elif outcome == "weak_hit":
            parts.append("\n[Guidance: The character succeeds but at a cost or with a complication. Include a tradeoff.]")
        elif outcome == "miss":
            parts.append("\n[Guidance: Things go wrong. Introduce a setback, danger, or escalation.]")

    # Narrative Orchestrator Guidance (if available)
    if hasattr(build_narrative_prompt, '_orchestrator') and build_narrative_prompt._orchestrator:
        orchestrator_guidance = build_narrative_prompt._orchestrator.get_comprehensive_guidance(
            location=location,
            active_npcs=psych_profile.involved_characters if psych_profile and hasattr(psych_profile, 'involved_characters') else [],
            player_action=player_input,
        )
        if orchestrator_guidance:
            parts.append(f"\n{orchestrator_guidance}")
    
    if style_profile:
        parts.append("\n[NARRATIVE STYLE ACTIVE]")
        if style_profile.tone_directives:
            parts.append(f"<tone_directives>\n- " + "\n- ".join(style_profile.tone_directives) + "\n</tone_directives>")
        if style_profile.vocabulary_hints:
            parts.append(f"<vocabulary_hints>\n- " + "\n- ".join(style_profile.vocabulary_hints) + "\n</vocabulary_hints>")
        if style_profile.few_shot_examples:
            parts.append("\n<style_examples>")
            for i, ex in enumerate(style_profile.few_shot_examples):
                parts.append(f"Example {i+1}:")
                parts.append(f"Context: {ex.get('context', 'General')}")
                parts.append(f"Narrative: {ex.get('narrative', '')}")
            parts.append("</style_examples>")

    parts.append("\n[Write the narrative response now]")

    return "\n".join(parts)


def generate_narrative(
    player_input: str,
    roll_result: str = "",
    outcome: str = "",
    character_name: str = "Traveler",
    location: str = "the void",
    context: str = "",
    config: NarratorConfig | None = None,
    psych_profile: PsychologicalProfile | None = None,
    hijack: str | None = None,
) -> str:
    """
    Generate narrative prose for the current game situation.

    This is the main entry point for narrative generation.

    Args:
        player_input: What the player said/did.
        roll_result: Formatted roll result (if any).
        outcome: "strong_hit", "weak_hit", "miss", or "" for no roll.
        character_name: The PC's name.
        location: Current location.
        context: Additional context (previous narrative, etc.).
        config: Optional narrator configuration.

    Returns:
        Generated narrative text.
    """
    config = config or NarratorConfig()

    guardrail_store = build_guardrail_store(
        player_input=player_input,
        character_name=character_name,
        location=location,
        context=context,
        roll_result=roll_result,
        psych_profile=psych_profile,
    )

    prompt = build_narrative_prompt(
        player_input=player_input,
        roll_result=roll_result,
        outcome=outcome,
        character_name=character_name,
        location=location,
        context=context,
        psych_profile=psych_profile,
        hijack=hijack,
        style_profile=load_style_profile(config.style_profile_name) if config.style_profile_name else None,
        guardrail_packet=guardrail_store.build_context_packet(),
        guardrail_rules=guardrail_store.guardrail_rules(),
    )

    provider = _get_provider(config)

    # Check if Client is available
    if not provider.is_available():
        return (
            f"[{provider.name} is not available. "
            f"Check configuration.]\n\n"
            f"*Placeholder narrative for: {player_input}*"
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    response = provider.chat(
        messages,
    provider = get_llm_provider_for_config(config)
    available, status_message = check_provider_availability(config, provider)

    if not available:
        return (
            f"{status_message}\n\n"
            f"*Placeholder narrative for: {player_input}*"
        )

    response = provider.chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        stream=False,
    )

    if isinstance(response, str):
        narrative = response
    else:
        narrative = "".join(response)

    return sanitize_and_verify(narrative, guardrail_store)


def generate_narrative_stream(
    player_input: str,
    roll_result: str = "",
    outcome: str = "",
    character_name: str = "Traveler",
    location: str = "the void",
    context: str = "",
    config: NarratorConfig | None = None,
    psych_profile: PsychologicalProfile | None = None,
    hijack: str | None = None,
) -> Generator[str, None, None]:
    """
    Generate narrative prose with streaming.

    Yields text chunks as they're generated for real-time display.
    """
    config = config or NarratorConfig()

    guardrail_store = build_guardrail_store(
        player_input=player_input,
        character_name=character_name,
        location=location,
        context=context,
        roll_result=roll_result,
        psych_profile=psych_profile,
    )

    prompt = build_narrative_prompt(
        player_input=player_input,
        roll_result=roll_result,
        outcome=outcome,
        character_name=character_name,
        location=location,
        context=context,
        psych_profile=psych_profile,
        hijack=hijack,
        style_profile=load_style_profile(config.style_profile_name) if config.style_profile_name else None,
        guardrail_packet=guardrail_store.build_context_packet(),
        guardrail_rules=guardrail_store.guardrail_rules(),
    )

    provider = _get_provider(config)

    if not provider.is_available():
        yield f"[{provider.name} is not available.]"
        return

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    response = provider.chat(
        messages,
    provider = get_llm_provider_for_config(config)
    available, status_message = check_provider_availability(config, provider)

    if not available:
        yield status_message
        return

    response = provider.chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        stream=True,
    )

    if isinstance(response, str):
        yield response
        yield sanitize_and_verify(response, guardrail_store)
        return

    raw_text = "".join(response)
    yield sanitize_and_verify(raw_text, guardrail_store)
