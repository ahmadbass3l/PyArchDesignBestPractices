"""
Filter 4 — ClassificationFilter
================================
Scope  : async (I/O-bound style)
Input  : EnrichedDocument
Output : ClassifiedDocument

Responsibilities:
  - Classify the document into a Category enum value
  - Assign a confidence score based on keyword density

The classification logic is intentionally simple (keyword matching)
so the sub-project runs without any ML dependencies.
Swap it for a transformer model in production.
"""

from pipeline.base import BaseFilter
from models.document import EnrichedDocument, ClassifiedDocument, Category


# Keyword sets per category
_KEYWORDS: dict[Category, set[str]] = {
    Category.TECHNICAL:  {"api", "code", "software", "system", "algorithm",
                          "database", "server", "network", "python", "data"},
    Category.LEGAL:      {"contract", "law", "legal", "court", "agreement",
                          "liability", "clause", "regulation", "compliance"},
    Category.FINANCIAL:  {"revenue", "profit", "loss", "investment", "budget",
                          "financial", "market", "stock", "capital", "tax"},
    Category.GENERAL:    set(),   # fallback
}


class ClassificationFilter(BaseFilter[EnrichedDocument, ClassifiedDocument]):

    run_in_process = False

    async def process(self, data: EnrichedDocument) -> ClassifiedDocument:
        words = set(data.content.lower().split())
        scores: dict[Category, int] = {}

        for category, keywords in _KEYWORDS.items():
            if not keywords:
                continue
            scores[category] = len(words & keywords)

        best_category  = max(scores, key=lambda c: scores[c], default=Category.UNKNOWN)
        best_score     = scores.get(best_category, 0)
        total_keywords = sum(scores.values())

        # Confidence = ratio of matching keywords for the winning category
        confidence = round(best_score / total_keywords, 4) if total_keywords > 0 else 0.0

        # Fall back to GENERAL if no keywords matched at all
        if best_score == 0:
            best_category = Category.GENERAL
            confidence    = 0.5   # neutral confidence for fallback

        return ClassifiedDocument(
            id=data.id,
            title=data.title,
            content=data.content,
            author=data.author,
            word_count=data.word_count,
            sentiment_score=data.sentiment_score,
            complexity_score=data.complexity_score,
            category=best_category,
            confidence=confidence,
        )
