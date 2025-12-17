"""
LLM Provider Abstraction

Provides a unified interface for multiple LLM backends:
- Ollama (local models)
- Google Gemini (API)

Configuration via environment variables:
- LLM_PROVIDER: "ollama" or "gemini" (default: ollama)
- GEMINI_API_KEY: Your Gemini API key
- OLLAMA_MODEL: Model name for Ollama (default: llama3.1)
- GEMINI_MODEL: Model name for Gemini (default: gemini-2.0-flash)
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generator, Optional, Dict, Any, List
import json


# =============================================================================
# ABSTRACT PROVIDER
# =============================================================================

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> str | Generator[str, None, None]:
        """Send a chat completion request."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for display."""
        pass


# =============================================================================
# OLLAMA PROVIDER
# =============================================================================

@dataclass
class OllamaProvider(LLMProvider):
    """Ollama local model provider."""
    
    model: str = "llama3.1"
    _client: Any = field(default=None, repr=False)
    
    def __post_init__(self):
        try:
            import ollama
            self._client = ollama.Client()
        except ImportError:
            self._client = None
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> str | Generator[str, None, None]:
        if not self._client:
            return "[Ollama not installed. Run: pip install ollama]"
        
        try:
            if stream:
                return self._stream_chat(messages, temperature, max_tokens)
            else:
                response = self._client.chat(
                    model=self.model,
                    messages=messages,
                    options={
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                )
                return response.get("message", {}).get("content", "")
        except Exception as e:
            return f"[Ollama error: {e}]"
    
    def _stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Generator[str, None, None]:
        try:
            stream = self._client.chat(
                model=self.model,
                messages=messages,
                stream=True,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            )
            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
        except Exception as e:
            yield f"[Ollama error: {e}]"
    
    def is_available(self) -> bool:
        if not self._client:
            return False
        try:
            models = self._client.list()
            model_names = [m.get("name", "").split(":")[0] for m in models.get("models", [])]
            return self.model.split(":")[0] in model_names
        except Exception:
            return False
    
    @property
    def name(self) -> str:
        return f"Ollama ({self.model})"


# =============================================================================
# GEMINI PROVIDER
# =============================================================================

@dataclass
class GeminiProvider(LLMProvider):
    """Google Gemini API provider."""
    
    model: str = "gemini-2.0-flash"
    api_key: str = ""
    _client: Any = field(default=None, repr=False)
    
    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.environ.get("GEMINI_API_KEY", "")
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                self._client = None
        else:
            self._client = None
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> str | Generator[str, None, None]:
        if not self._client:
            if not self.api_key:
                return "[Gemini API key not set. Set GEMINI_API_KEY environment variable.]"
            return "[google-generativeai not installed. Run: pip install google-generativeai]"
        
        try:
            # Convert messages to Gemini format
            gemini_messages = []
            system_prompt = ""
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    system_prompt = content
                elif role == "user":
                    gemini_messages.append({"role": "user", "parts": [content]})
                elif role == "assistant":
                    gemini_messages.append({"role": "model", "parts": [content]})
            
            # Start chat with history
            chat = self._client.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
            
            # Get the last user message
            last_message = gemini_messages[-1]["parts"][0] if gemini_messages else ""
            
            # Prepend system prompt to first message if present
            if system_prompt and last_message:
                last_message = f"[System: {system_prompt}]\n\n{last_message}"
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            if stream:
                return self._stream_chat(chat, last_message, generation_config)
            else:
                response = chat.send_message(
                    last_message,
                    generation_config=generation_config
                )
                return response.text
                
        except Exception as e:
            return f"[Gemini error: {e}]"
    
    def _stream_chat(
        self,
        chat,
        message: str,
        generation_config: dict
    ) -> Generator[str, None, None]:
        try:
            response = chat.send_message(
                message,
                generation_config=generation_config,
                stream=True
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"[Gemini error: {e}]"
    
    def is_available(self) -> bool:
        if not self._client or not self.api_key:
            return False
        try:
            # Quick test
            response = self._client.generate_content("Say 'ok'", generation_config={"max_output_tokens": 5})
            return bool(response.text)
        except Exception:
            return False
    
    @property
    def name(self) -> str:
        return f"Gemini ({self.model})"


# =============================================================================
# PROVIDER FACTORY
# =============================================================================

def get_llm_provider(
    provider_type: str = None,
    model: str = None,
    api_key: str = None
) -> LLMProvider:
    """
    Get an LLM provider based on configuration.
    
    Args:
        provider_type: "ollama" or "gemini" (default: from LLM_PROVIDER env var or "ollama")
        model: Model name (default: from env var or provider default)
        api_key: API key for Gemini (default: from GEMINI_API_KEY env var)
    
    Returns:
        Configured LLM provider
    """
    if provider_type is None:
        provider_type = os.environ.get("LLM_PROVIDER", "ollama").lower()
    
    if provider_type == "gemini":
        if model is None:
            model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY", "")
        return GeminiProvider(model=model, api_key=api_key)
    
    else:  # Default to ollama
        if model is None:
            model = os.environ.get("OLLAMA_MODEL", "llama3.1")
        return OllamaProvider(model=model)


# =============================================================================
# GLOBAL PROVIDER INSTANCE
# =============================================================================

_global_provider: Optional[LLMProvider] = None


def get_provider() -> LLMProvider:
    """Get the global LLM provider instance."""
    global _global_provider
    if _global_provider is None:
        _global_provider = get_llm_provider()
    return _global_provider


def set_provider(provider: LLMProvider):
    """Set the global LLM provider instance."""
    global _global_provider
    _global_provider = provider


def configure_gemini(api_key: str, model: str = "gemini-2.0-flash"):
    """Convenience function to configure Gemini as the provider."""
    provider = GeminiProvider(model=model, api_key=api_key)
    set_provider(provider)
    return provider


def configure_ollama(model: str = "llama3.1"):
    """Convenience function to configure Ollama as the provider."""
    provider = OllamaProvider(model=model)
    set_provider(provider)
    return provider


# =============================================================================
# HELPER FUNCTIONS (drop-in replacements for ollama.Client calls)
# =============================================================================

def chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 1024,
    stream: bool = False,
    provider: LLMProvider = None
) -> str | Generator[str, None, None]:
    """
    Provider-agnostic chat completion.
    
    This is a drop-in replacement for ollama.Client().chat()
    """
    if provider is None:
        provider = get_provider()
    return provider.chat(messages, temperature, max_tokens, stream)


def generate_narrative(
    prompt: str,
    system: str = "",
    temperature: float = 0.8,
    max_tokens: int = 500,
    stream: bool = True,
    provider: LLMProvider = None
) -> str | Generator[str, None, None]:
    """
    Generate narrative text.
    
    Args:
        prompt: User prompt
        system: System prompt
        temperature: Creativity (0.0-1.0)
        max_tokens: Maximum tokens to generate
        stream: Whether to stream response
        provider: LLM provider (default: global)
    
    Returns:
        Generated text or generator of chunks
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    return chat_completion(messages, temperature, max_tokens, stream, provider)


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LLM PROVIDER TEST")
    print("=" * 60)
    
    # Check environment
    provider_type = os.environ.get("LLM_PROVIDER", "ollama")
    print(f"\nLLM_PROVIDER: {provider_type}")
    print(f"GEMINI_API_KEY: {'set' if os.environ.get('GEMINI_API_KEY') else 'not set'}")
    
    # Get provider
    provider = get_llm_provider()
    print(f"\nUsing provider: {provider.name}")
    print(f"Available: {provider.is_available()}")
    
    if provider.is_available():
        print("\n--- Test Generation ---")
        response = provider.chat(
            messages=[
                {"role": "system", "content": "You are a fantasy narrator."},
                {"role": "user", "content": "Describe a starship in one sentence."}
            ],
            temperature=0.8,
            max_tokens=100
        )
        print(f"Response: {response}")
    else:
        print("\nProvider not available. Check configuration.")
