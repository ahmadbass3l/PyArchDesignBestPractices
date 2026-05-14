"""
Filter Registry
===============
IoC-style registry that holds the ordered list of filters
making up a named pipeline.

Usage:
    registry = FilterRegistry()
    registry.register("document", [
        ValidationFilter(),
        SanitizationFilter(),
        EnrichmentFilter(),
        ClassificationFilter(),
    ])
    filters = registry.get("document")
"""

from typing import List, Dict
from pipeline.base import BaseFilter


class FilterRegistry:
    """
    Holds named pipeline definitions.
    A pipeline is an ordered list of BaseFilter instances.
    """

    def __init__(self):
        # pipeline name → ordered list of filters
        self._pipelines: Dict[str, List[BaseFilter]] = {}

    def register(self, name: str, filters: List[BaseFilter]) -> None:
        """
        Register an ordered filter chain under a pipeline name.

        Args:
            name:    Unique pipeline identifier (e.g. 'document')
            filters: Ordered list of BaseFilter instances
        """
        if not filters:
            raise ValueError(f"Pipeline '{name}' must have at least one filter.")
        self._pipelines[name] = filters
        print(f"[Registry] Pipeline '{name}' registered with "
              f"{len(filters)} filter(s): "
              f"{[f.name for f in filters]}")

    def get(self, name: str) -> List[BaseFilter]:
        """
        Retrieve the filter chain for a named pipeline.

        Args:
            name: Pipeline identifier

        Returns:
            Ordered list of filters

        Raises:
            KeyError: If pipeline name is not registered
        """
        if name not in self._pipelines:
            raise KeyError(f"[Registry] Pipeline '{name}' is not registered.")
        return self._pipelines[name]

    @property
    def available(self) -> List[str]:
        """Return all registered pipeline names."""
        return list(self._pipelines.keys())
