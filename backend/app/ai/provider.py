from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AIProvider(ABC):
    """Interface for the hosted LLM used in research flows.

    Phase 1 only defines the interface; concrete implementations and
    integration are added in later phases.
    """

    @abstractmethod
    async def generate_answer(
        self, *,
        question: str,
        context: List[Dict[str, Any]],
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError
