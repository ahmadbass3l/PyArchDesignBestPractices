"""
Filter 2 — SanitizationFilter
==============================
Scope  : async (I/O-bound style)
Input  : ValidatedDocument
Output : SanitizedDocument

Responsibilities:
  - Strip HTML tags from content
  - Collapse multiple whitespace/newlines into single spaces
  - Normalise title casing

Kept dependency-free (no BeautifulSoup) so the sub-project
runs out of the box. In production, swap the regex for a
properly library (e.g. bleach, html-sanitizer).
"""

import re
from pipeline.base import BaseFilter
from models.document import ValidatedDocument, SanitizedDocument


# Simple HTML tag pattern — good enough for demonstration purposes
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


class SanitizationFilter(BaseFilter[ValidatedDocument, SanitizedDocument]):

    run_in_process = False

    async def process(self, data: ValidatedDocument) -> SanitizedDocument:
        # Remove HTML tags
        clean = _HTML_TAG_RE.sub(" ", data.content)
        # Collapse whitespace
        clean = _WHITESPACE_RE.sub(" ", clean).strip()
        # Recount words after sanitisation
        word_count = len(clean.split())

        return SanitizedDocument(
            id=data.id,
            title=data.title.title(),   # normalise title casing
            content=clean,
            author=data.author,
            word_count=word_count,
        )
