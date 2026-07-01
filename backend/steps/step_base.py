import logging
from abc import ABC, abstractmethod
from typing import Callable, Any

class BaseStep(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, context: dict, log_fn: Callable[[str], None]) -> Any:
        """
        Executes the step logic.
        context: shared dictionary for passing data between steps
        log_fn: callback to stream logs to the client
        """
        pass
