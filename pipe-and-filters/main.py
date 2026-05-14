"""
FastAPI Entry Point
===================
Exposes the document processing pipeline as an HTTP API.

ENDPOINTS:
==========
  POST /pipeline/document   → run the full filter chain
  GET  /pipeline/available  → list registered pipelines
  GET  /health              → liveness check

STARTUP:
========
  On app startup, all filters are instantiated and registered
  with the FilterRegistry. This is the COMPOSITION ROOT —
  the only place where concrete filter classes are referenced.

RUN:
====
  uvicorn main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from models.document import RawDocument, ClassifiedDocument
from pipeline.registry import FilterRegistry
from pipeline.engine import PipelineEngine
from filters.validation import ValidationFilter
from filters.sanitization import SanitizationFilter
from filters.enrichment import EnrichmentFilter
from filters.classification import ClassificationFilter


# ── Globals (initialised at startup) ─────────────────────────────────────────
registry: FilterRegistry | None = None
engine:   PipelineEngine  | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan handler.
    Runs setup before the app starts serving requests.
    This is the COMPOSITION ROOT — wire filters here.
    """
    global registry, engine

    # ── Register the document processing pipeline ─────────────────────────
    # Order matters: each filter's output is the next filter's input.
    registry = FilterRegistry()
    registry.register("document", [
        ValidationFilter(),      # 1. gate — validate & count words
        SanitizationFilter(),    # 2. clean — strip HTML, normalise
        EnrichmentFilter(),      # 3. enrich — NLP scores (multiprocessing)
        ClassificationFilter(),  # 4. classify — assign category
    ])

    engine = PipelineEngine(registry)
    print("[App] Pipeline engine ready.")

    yield  # app is running

    print("[App] Shutting down.")


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Pipe & Filter — Document Processing Pipeline",
    description=(
        "Demonstrates the Pipe & Filter architectural pattern using "
        "FastAPI, Pydantic v2, asyncio, and multiprocessing."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Liveness check."""
    return {"status": "ok"}


@app.get("/pipeline/available")
async def available_pipelines():
    """List all registered pipeline names."""
    return {"pipelines": registry.available}


@app.post("/pipeline/document", response_model=ClassifiedDocument)
async def process_document(raw: RawDocument):
    """
    Push a raw document through the full processing pipeline.

    The pipeline runs filters in order:
      1. ValidationFilter    (async)
      2. SanitizationFilter  (async)
      3. EnrichmentFilter    (multiprocessing)
      4. ClassificationFilter(async)

    Returns the fully enriched and classified document.
    """
    try:
        result: ClassifiedDocument = await engine.run("document", raw)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}")
