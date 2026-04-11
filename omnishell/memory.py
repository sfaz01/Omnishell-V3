"""
Conversational memory — maintains context across multiple requests in a session.
"""

from langchain_core.messages import HumanMessage, AIMessage

# Maximum number of message pairs to keep in memory to avoid token overflow
MAX_MEMORY_PAIRS = 10


class ConversationMemory:
    """
    Manages conversation history for contextual multi-turn interactions.
    
    Example:
        USER > install nginx
        AI   > sudo pacman -S nginx
        USER > now enable and start it
        AI   > sudo systemctl enable --now nginx  (knows "it" = nginx)
    """

    def __init__(self, max_pairs: int = MAX_MEMORY_PAIRS):
        self._history: list = []
        self._max_pairs = max_pairs

    def add_user_message(self, content: str) -> None:
        """Record a user query."""
        self._history.append(HumanMessage(content=content))
        self._trim()

    def add_ai_message(self, content: str) -> None:
        """Record an AI response."""
        self._history.append(AIMessage(content=content))
        self._trim()

    def get_messages(self) -> list:
        """Return the conversation history as LangChain message objects."""
        return list(self._history)

    def get_context_summary(self) -> str:
        """
        Return a text summary of recent conversation for injection into prompts.
        Useful when you want context without passing full message objects.
        """
        if not self._history:
            return ""
        
        lines = []
        for msg in self._history[-6:]:  # Last 3 exchanges
            role = "User" if isinstance(msg, HumanMessage) else "AI"
            lines.append(f"{role}: {msg.content}")
        
        return "RECENT CONVERSATION:\n" + "\n".join(lines)

    def clear(self) -> None:
        """Reset conversation memory."""
        self._history.clear()

    def _trim(self) -> None:
        """Keep only the last N message pairs to prevent token overflow."""
        max_messages = self._max_pairs * 2
        if len(self._history) > max_messages:
            self._history = self._history[-max_messages:]

    def __len__(self) -> int:
        return len(self._history)

    def __bool__(self) -> bool:
        return len(self._history) > 0
