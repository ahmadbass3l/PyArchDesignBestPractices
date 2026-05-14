"""
Pipeline Engine
===============
The async orchestrator that pushes data through the filter chain.

ARCHITECTURE:
=============

  FastAPI endpoint
      │
      ▼
  PipelineEngine.run(pipeline_name, raw_input)
      │
      ├──▶ Filter 1 (async)            await filter.process(data)
      │         │
      │         ▼  output becomes next input
      ├──▶ Filter 2 (async)            await filter.process(data)
      │         │
      │         ▼
      ├──▶ Filter 3 (CPU-bound)        loop.run_in_executor(
      │         │                          ProcessPoolExecutor, ...)
      │         ▼
      └──▶ Filter 4 (async)            await filter.process(data)
                │
                ▼
           Final typed result

KEY BEHAVIOURS:
===============
  - Filters marked run_in_process=True are offloaded to a
    ProcessPoolExecutor so they don't block the event loop.
  - All other filters run as standard coroutines (await).
  - Each filter's output is passed as the next filter's input.
  - Exceptions bubble up with the failing filter name attached.
"""

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Any

from pipeline.registry import FilterRegistry


# Module-level executor — created once, shared across requests
# max_workers controls how many parallel processes can run
_process_pool = ProcessPoolExecutor(max_workers=4)


class PipelineEngine:
    """
    Async pipeline orchestrator.

    Iterates the registered filter chain and passes data through
    each filter sequentially. CPU-bound filters are automatically
    offloaded to a separate OS process via ProcessPoolExecutor.
    """

    def __init__(self, registry: FilterRegistry):
        self._registry = registry

    async def run(self, pipeline_name: str, data: Any) -> Any:
        """
        Execute the named pipeline on the given data.

        Args:
            pipeline_name: Registered pipeline identifier
            data:          Initial Pydantic input model

        Returns:
            Final transformed Pydantic model after all filters
        """
        filters = self._registry.get(pipeline_name)
        print(f"\n[Engine] Starting pipeline '{pipeline_name}' "
              f"with {len(filters)} filter(s)")

        for filt in filters:
            start = time.perf_counter()

            if filt.run_in_process:
                # ── CPU-bound: run in a separate OS process ──────────────
                # We can't send a coroutine to another process, so the
                # filter's `process` method must be a regular (sync)
                # function internally — the engine wraps the call.
                print(f"[Engine] → {filt.name} (multiprocessing)")
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(
                    _process_pool,
                    filt.process_sync,   # sync version called in subprocess
                    data
                )
            else:
                # ── I/O-bound: run as a standard coroutine ───────────────
                print(f"[Engine] → {filt.name} (async)")
                data = await filt.process(data)

            elapsed = (time.perf_counter() - start) * 1000
            print(f"[Engine]   ✓ {filt.name} completed in {elapsed:.1f}ms")

        print(f"[Engine] Pipeline '{pipeline_name}' finished.\n")
        return data
