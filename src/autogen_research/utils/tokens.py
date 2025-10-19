"""Token counting and cost estimation utilities."""

from typing import Any

import tiktoken

from .logger import get_logger

logger = get_logger(__name__)


# Model pricing per 1K tokens (input/output) in USD
MODEL_PRICING = {
    # OpenAI pricing (as of 2025)
    "gpt-4": (0.03, 0.06),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-4o": (0.005, 0.015),
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-3.5-turbo": (0.0005, 0.0015),
    # Ollama models are free (local)
    "llama3.2": (0.0, 0.0),
    "llama3.2:1b": (0.0, 0.0),
    "llama3.2:3b": (0.0, 0.0),
    "mistral": (0.0, 0.0),
    "codellama": (0.0, 0.0),
}


class TokenCounter:
    """Utility for counting tokens and estimating costs."""

    def __init__(self, model: str = "gpt-4"):
        """
        Initialize token counter.

        Args:
            model: Model name for encoding selection
        """
        self.model = model
        self._encoding = None

    @property
    def encoding(self):
        """Lazy load encoding."""
        if self._encoding is None:
            try:
                # Try to get model-specific encoding
                self._encoding = tiktoken.encoding_for_model(self.model)
            except KeyError:
                # Fall back to cl100k_base (used by GPT-4, GPT-3.5-turbo)
                logger.warning(f"No encoding found for {self.model}, using cl100k_base")
                self._encoding = tiktoken.get_encoding("cl100k_base")
        return self._encoding

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in a text string.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def count_message_tokens(self, messages: list[dict[str, Any]]) -> int:
        """
        Count tokens in a list of chat messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content'

        Returns:
            Total number of tokens
        """
        total_tokens = 0

        # Add tokens for each message
        for message in messages:
            # Every message follows <|start|>{role/name}\n{content}<|end|>\n
            total_tokens += 4  # Message formatting tokens

            for key, value in message.items():
                if isinstance(value, str):
                    total_tokens += self.count_tokens(value)
                if key == "name":
                    total_tokens += -1  # Role is always required and always 1 token

        total_tokens += 2  # Every reply is primed with <|start|>assistant
        return total_tokens

    def estimate_cost(
        self, input_tokens: int, output_tokens: int, model: str | None = None
    ) -> float:
        """
        Estimate cost for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name (uses self.model if not provided)

        Returns:
            Estimated cost in USD
        """
        model_name = model or self.model

        # Find matching pricing
        pricing = None
        for key, value in MODEL_PRICING.items():
            if key in model_name.lower():
                pricing = value
                break

        if pricing is None:
            logger.warning(f"No pricing found for {model_name}, assuming free")
            return 0.0

        input_price, output_price = pricing

        # Calculate cost (pricing is per 1K tokens)
        input_cost = (input_tokens / 1000) * input_price
        output_cost = (output_tokens / 1000) * output_price

        return round(input_cost + output_cost, 6)

    def truncate_to_token_limit(self, text: str, max_tokens: int, from_end: bool = False) -> str:
        """
        Truncate text to fit within token limit.

        Args:
            text: Text to truncate
            max_tokens: Maximum number of tokens
            from_end: If True, keep end of text; if False, keep beginning

        Returns:
            Truncated text
        """
        tokens = self.encoding.encode(text)

        if len(tokens) <= max_tokens:
            return text

        if from_end:
            # Keep end of text
            truncated_tokens = tokens[-max_tokens:]
        else:
            # Keep beginning of text
            truncated_tokens = tokens[:max_tokens]

        return self.encoding.decode(truncated_tokens)

    def get_token_stats(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Get detailed token statistics for a conversation.

        Args:
            messages: List of messages

        Returns:
            Dictionary with token statistics
        """
        total_tokens = 0
        by_role = {}

        for msg in messages:
            role = msg.get("role", msg.get("source", "unknown"))
            content = msg.get("content", "")
            tokens = self.count_tokens(str(content))

            total_tokens += tokens
            by_role[role] = by_role.get(role, 0) + tokens

        return {
            "total_tokens": total_tokens,
            "by_role": by_role,
            "message_count": len(messages),
            "avg_tokens_per_message": total_tokens / len(messages) if messages else 0,
        }


def truncate_conversation_history(
    messages: list[dict[str, Any]],
    max_tokens: int = 4000,
    model: str = "gpt-4",
    keep_system: bool = True,
) -> list[dict[str, Any]]:
    """
    Truncate conversation history to fit within token limit.

    Keeps most recent messages and optionally preserves system message.

    Args:
        messages: List of messages
        max_tokens: Maximum total tokens
        model: Model name for token counting
        keep_system: Whether to always keep system message

    Returns:
        Truncated list of messages
    """
    counter = TokenCounter(model)

    # Separate system message if present
    system_msg = None
    if keep_system and messages and messages[0].get("role") == "system":
        system_msg = messages[0]
        messages = messages[1:]

    # Start from most recent and work backwards
    truncated = []
    total_tokens = 0

    if system_msg:
        system_tokens = counter.count_tokens(system_msg.get("content", ""))
        total_tokens = system_tokens + 4  # Message formatting

    # Add messages from newest to oldest
    for msg in reversed(messages):
        msg_tokens = counter.count_tokens(str(msg.get("content", ""))) + 4

        if total_tokens + msg_tokens > max_tokens:
            break

        truncated.insert(0, msg)
        total_tokens += msg_tokens

    # Re-add system message at beginning
    if system_msg:
        truncated.insert(0, system_msg)

    logger.info(
        f"Truncated {len(messages)} messages to {len(truncated)} "
        f"({total_tokens}/{max_tokens} tokens)"
    )

    return truncated
