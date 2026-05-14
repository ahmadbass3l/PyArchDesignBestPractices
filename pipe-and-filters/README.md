# 📦 Pipe & Filter — Document Processing Pipeline

## What is the Pipe & Filter Pattern?

**Pipe & Filter** is an architectural pattern where data flows through a sequence of
independent processing steps (**filters**), connected by **pipes** (the data passed between them).

Each filter:
- Receives data from the previous step
- Transforms it
- Passes the result to the next step
- Has **no knowledge** of any other filter

---

## Architecture Diagram

```
  HTTP Request (RawDocument)
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                      FastAPI Endpoint                           │
  │              POST /pipeline/document                            │
  └────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                     PipelineEngine                              │
  │           async orchestrator — pushes data through filters      │
  └──┬──────────────────────────────────────────────────────────────┘
     │
     ├──▶ ┌─────────────────────┐
     │    │  ValidationFilter   │  async   RawDocument → ValidatedDocument
     │    └─────────────────────┘
     │
     ├──▶ ┌─────────────────────┐
     │    │ SanitizationFilter  │  async   ValidatedDocument → SanitizedDocument
     │    └─────────────────────┘
     │
     ├──▶ ┌─────────────────────┐
     │    │  EnrichmentFilter   │  ★ multiprocessing (CPU-bound NLP)
     │    │                     │    SanitizedDocument → EnrichedDocument
     │    └─────────────────────┘
     │
     └──▶ ┌─────────────────────┐
          │ClassificationFilter │  async   EnrichedDocument → ClassifiedDocument
          └─────────────────────┘
                    │
                    ▼
         HTTP Response (ClassifiedDocument)
```

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| API | **FastAPI** | Expose pipeline as HTTP endpoint |
| Contracts | **Pydantic v2** | Typed input/output per filter |
| Async orchestration | **asyncio** | Non-blocking filter chaining |
| CPU-bound parallelism | **ProcessPoolExecutor** | Multiprocessing for EnrichmentFilter |
| Abstractions | **ABC** | Enforced filter interface |

---

## Project Structure

```
pipe-and-filters/
│
├── main.py                  ← FastAPI app + composition root
│
├── pipeline/
│   ├── base.py              ← Abstract BaseFilter (ABC)
│   ├── registry.py          ← Filter registration (IoC-style)
│   └── engine.py            ← Async pipeline orchestrator
│
├── filters/
│   ├── validation.py        ← Filter 1: validate & count words
│   ├── sanitization.py      ← Filter 2: strip HTML, normalise
│   ├── enrichment.py        ← Filter 3: NLP scores (multiprocessing)
│   └── classification.py   ← Filter 4: categorise document
│
├── models/
│   └── document.py          ← Pydantic models (pipeline contracts)
│
└── README.md
```

---

## Key Design Decisions

### 1. Passive Filters
Filters never pull data — they receive it pushed by the engine.
This keeps filters completely decoupled from each other.

### 2. Typed Contracts via Pydantic
Every filter has a strictly typed input and output model.
If a filter returns the wrong shape, Pydantic raises immediately.

### 3. Async + Multiprocessing
```
I/O-bound filters  →  await filter.process(data)          (event loop)
CPU-bound filters  →  loop.run_in_executor(ProcessPool)   (separate process)
```
The engine decides which path to take based on `filter.run_in_process`.

### 4. IoC-style Registry
Filters are registered by name at startup (composition root in `main.py`).
The engine never references concrete filter classes — only the registry.

---

## How to Run

```bash
cd pipe-and-filters

# Install dependencies
pip install fastapi uvicorn pydantic

# Start the API
uvicorn main:app --reload
```

### Example Request

```bash
curl -X POST http://localhost:8000/pipeline/document \
  -H "Content-Type: application/json" \
  -d '{
    "id": "doc-001",
    "title": "Python Software Architecture",
    "content": "Python is a great language for building software systems and APIs.",
    "author": "Ahmad"
  }'
```

### Example Response

```json
{
  "id": "doc-001",
  "title": "Python Software Architecture",
  "content": "Python is a great language for building software systems and APIs.",
  "author": "Ahmad",
  "word_count": 12,
  "sentiment_score": 1.0,
  "complexity_score": 0.39,
  "category": "technical",
  "confidence": 0.6667
}
```

---

## Key Takeaway

> Each filter is a **black box** — it knows nothing about its neighbours.
> The engine is the **only** component that knows the order.
> Swap, reorder, or add filters in **one place** (the registry in `main.py`).
