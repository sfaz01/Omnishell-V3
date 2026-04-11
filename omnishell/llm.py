"""
Multi-LLM support — factory for Groq, Ollama, OpenAI, and Google Gemini.
"""

import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Supported providers
PROVIDERS = ["groq", "ollama", "openai", "gemini"]

# Default models per provider
DEFAULT_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "ollama": "llama3",
    "openai": "gpt-4o-mini",
    "gemini": "gemini-2.0-flash",
}


def get_llm(provider: str = None, model: str = None, temperature: float = 0.1):
    """
    Factory function to create an LLM instance.

    Args:
        provider: One of 'groq', 'ollama', 'openai', 'gemini'. 
                  Defaults to OMNISHELL_PROVIDER env var or 'groq'.
        model: Model name override. Defaults to OMNISHELL_MODEL env var or provider default.
        temperature: LLM temperature. Defaults to 0.1 for precise command generation.

    Returns:
        A LangChain chat model instance.

    Raises:
        ValueError: If the provider is unknown or credentials are missing.
    """
    provider = provider or os.getenv("OMNISHELL_PROVIDER", "groq")
    model = model or os.getenv("OMNISHELL_MODEL", DEFAULT_MODELS.get(provider))
    provider = provider.lower()

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Set it in your .env file or environment.\n"
                "Get a free key at: https://console.groq.com"
            )
        from langchain_groq import ChatGroq
        return ChatGroq(model=model, temperature=temperature, groq_api_key=api_key)

    elif provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ValueError(
                "Ollama support requires: pip install langchain-ollama\n"
                "Also ensure Ollama is running: https://ollama.ai"
            )
        return ChatOllama(model=model, temperature=temperature)

    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found. Set it in your .env file.")
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ValueError("OpenAI support requires: pip install langchain-openai")
        return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)

    elif provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found. Set it in your .env file.\n"
                "Get a key at: https://aistudio.google.com/apikey"
            )
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ValueError("Gemini support requires: pip install langchain-google-genai")
        return ChatGoogleGenerativeAI(model=model, temperature=temperature, google_api_key=api_key)

    else:
        raise ValueError(
            f"Unknown provider: '{provider}'. "
            f"Supported: {', '.join(PROVIDERS)}"
        )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def invoke_llm(llm, messages) -> str:
    """
    Invoke the LLM with retry logic and exponential backoff.
    Handles rate limits and transient API failures.

    Returns:
        The LLM response content as a stripped string.
    """
    try:
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        logger.error(f"LLM invocation failed: {e}")
        raise
