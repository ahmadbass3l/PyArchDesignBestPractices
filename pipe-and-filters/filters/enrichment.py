"""
Filter 3 — EnrichmentFilter  (CPU-BOUND)
=========================================
Scope  : MULTIPROCESSING via ProcessPoolExecutor
Input  : SanitizedDocument
Output : EnrichedDocument

Responsibilities:
  - Compute a sentiment score  (-1.0 negative → +1.0 positive)
  - Compute a complexity score ( 0.0 simple   →  1.0 complex)

Why multiprocessing?
  NLP scoring is CPU-intensive. Running it in the asyncio event
  loop would block all other requests. Offloading to a separate
  OS process (via ProcessPoolExecutor) keeps the API responsive.

IMPORTANT — process_sync vs process:
  Objects sent to another process must be PICKLABLE.
  Coroutines are NOT picklable, so CPU-bound filters expose:
    - process_sync(data) → called by the engine in the subprocess
    - process(data)      → async wrapper (not used for CPU filters,
                           but required by the ABC contract)
"""

import asyncio
from pipeline.base import BaseFilter
from models.document import SanitizedDocument, EnrichedDocument


# ── Standalone functions (must be module-level to be picklable) ───────────────

def _compute_sentiment(text: str) -> float:
    """
    Naïve sentiment: ratio of positive vs negative keyword hits.
    Replace with a real model (VADER, HuggingFace) in production.
    """
    positive = {"good", "great", "excellent", "happy", "positive",
                "love", "wonderful", "amazing", "best", "fantastic"}
    negative = {"bad",  "terrible", "awful",   "sad",  "negative",
                "hate", "horrible", "worst",   "poor", "dreadful"}

    words  = text.lower().split()
    pos    = sum(1 for w in words if w in positive)
    neg    = sum(1 for w in words if w in negative)
    total  = pos + neg

    if total == 0:
        return 0.0
    return round((pos - neg) / total, 4)


def _compute_complexity(text: str) -> float:
    """
    Naïve complexity: average word length normalised to [0, 1].
    Replace with Flesch-Kincaid or similar in production.
    """
    words = text.split()
    if not words:
        return 0.0
    avg_len = sum(len(w) for w in words) / len(words)
    # Cap at 12 chars average → score of 1.0
    return round(min(avg_len / 12.0, 1.0), 4)


# ── Filter class ──────────────────────────────────────────────────────────────

class EnrichmentFilter(BaseFilter[SanitizedDocument, EnrichedDocument]):

    # Signal to the engine: run me in a separate OS process
    run_in_process = True

    def process_sync(self, data: SanitizedDocument) -> EnrichedDocument:
        """
        Synchronous entry point called by ProcessPoolExecutor.
        This runs in a SEPARATE PROCESS — no event loop here.
        """
        sentiment  = _compute_sentiment(data.content)
        complexity = _compute_complexity(data.content)

        return EnrichedDocument(
            id=data.id,
            title=data.title,
            content=data.content,
            author=data.author,
            word_count=data.word_count,
            sentiment_score=sentiment,
            complexity_score=complexity,
        )

    async def process(self, data: SanitizedDocument) -> EnrichedDocument:
        """
        Async wrapper — the engine calls process_sync() directly
        for CPU-bound filters, but this satisfies the ABC contract.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process_sync, data)
