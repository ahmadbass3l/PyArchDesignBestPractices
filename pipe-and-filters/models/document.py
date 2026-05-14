"""
Pydantic Models — Pipeline Contracts
=====================================
Every filter in the pipeline has a strictly typed input and output.
Pydantic v2 enforces these contracts at runtime.

DATA FLOW:
==========

  RawDocument
      │
      ▼
  ValidatedDocument
      │
      ▼
  SanitizedDocument
      │
      ▼
  EnrichedDocument
      │
      ▼
  ClassifiedDocument  ← final pipeline output
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Category(str, Enum):
    TECHNICAL  = "technical"
    LEGAL      = "legal"
    FINANCIAL  = "financial"
    GENERAL    = "general"
    UNKNOWN    = "unknown"


# ── Input: what the API receives ──────────────────────────────────────────────
class RawDocument(BaseModel):
    """Raw payload received from the API caller."""
    id:      str         = Field(..., description="Unique document identifier")
    title:   str         = Field(..., min_length=1, max_length=200)
    content: str         = Field(..., min_length=1)
    author:  Optional[str] = None


# ── Intermediate: produced by each filter ─────────────────────────────────────
class ValidatedDocument(BaseModel):
    """Produced by ValidationFilter — content confirmed non-empty and safe."""
    id:      str
    title:   str
    content: str
    author:  Optional[str] = None
    word_count: int


class SanitizedDocument(BaseModel):
    """Produced by SanitizationFilter — HTML stripped, whitespace normalised."""
    id:      str
    title:   str
    content: str          # cleaned
    author:  Optional[str] = None
    word_count: int


class EnrichedDocument(BaseModel):
    """Produced by EnrichmentFilter — CPU-bound NLP scores attached."""
    id:         str
    title:      str
    content:    str
    author:     Optional[str] = None
    word_count: int
    sentiment_score:  float   = Field(..., ge=-1.0, le=1.0)
    complexity_score: float   = Field(..., ge=0.0,  le=1.0)


class ClassifiedDocument(BaseModel):
    """Produced by ClassificationFilter — final pipeline output."""
    id:               str
    title:            str
    content:          str
    author:           Optional[str] = None
    word_count:       int
    sentiment_score:  float
    complexity_score: float
    category:         Category
    confidence:       float = Field(..., ge=0.0, le=1.0)
