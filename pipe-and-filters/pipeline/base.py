"""
Abstract Base Filter
====================
All filters in the pipeline must inherit from BaseFilter.
This enforces a consistent async interface across every node.

DESIGN:
=======
  - Filters are PASSIVE: they receive data pushed by the engine.
  - Each filter transforms its input and returns a new output model.
  - Filters never know about each other — only the engine connects them.
  - CPU-bound filters override `run_in_process=True` to signal the
    engine to execute them in a separate process.

INTERFACE:
==========

  BaseFilter
    └── process(data: InputT) -> OutputT   ← must be implemented
        run_in_process: bool               ← set True for CPU-bound work
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

InputT  = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseFilter(ABC, Generic[InputT, OutputT]):
    """
    Abstract base class for all pipeline filters.

    Subclasses must implement `process()`.
    Set `run_in_process = True` for CPU-bound filters that should
    be offloaded to a separate process via ProcessPoolExecutor.
    """

    # Override to True in CPU-bound filters
    run_in_process: bool = False

    @abstractmethod
    async def process(self, data: InputT) -> OutputT:
        """
        Transform the incoming data and return the enriched result.

        Args:
            data: Typed input model (Pydantic BaseModel)

        Returns:
            Typed output model (Pydantic BaseModel)
        """
        ...

    @property
    def name(self) -> str:
        """Human-readable filter name for logging."""
        return self.__class__.__name__
