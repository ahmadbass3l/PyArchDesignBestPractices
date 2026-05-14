"""
Filter 1 — ValidationFilter
============================
Scope  : async (I/O-bound style, fast)
Input  : RawDocument
Output : ValidatedDocument

Responsibilities:
  - Confirm content is not empty or whitespace-only
  - Count words
  - Pass through a typed, validated model

This filter acts as the pipeline's GATEKEEPER.
If validation fails, an exception is raised and the
pipeline stops — no further filters are executed.
"""

from pipeline.base import BaseFilter
from models.document import RawDocument, ValidatedDocument


class ValidationFilter(BaseFilter[RawDocument, ValidatedDocument]):

    run_in_process = False  # fast, no need for a separate process

    async def process(self, data: RawDocument) -> ValidatedDocument:
        # Strip and check content is meaningful
        content = data.content.strip()
        if not content:
            raise ValueError(f"[ValidationFilter] Document '{data.id}' has empty content.")

        word_count = len(content.split())
        if word_count < 3:
            raise ValueError(
                f"[ValidationFilter] Document '{data.id}' is too short ({word_count} words)."
            )

        return ValidatedDocument(
            id=data.id,
            title=data.title.strip(),
            content=content,
            author=data.author,
            word_count=word_count,
        )
