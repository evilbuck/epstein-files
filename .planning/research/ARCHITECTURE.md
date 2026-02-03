# Architecture Patterns: Document Cataloging and Intelligence Systems

**Domain:** AI-powered document cataloging and query system  
**Researched:** February 2, 2026  
**Overall Confidence:** MEDIUM-HIGH

## Executive Summary

Document intelligence systems follow a consistent pipeline architecture: **Ingestion → Parsing → Enrichment → Storage → Retrieval → Query**. For the Epstein Files project, this translates to downloading PDFs from justice.gov, extracting text via Python libraries (pdfplumber/pypdf), running entity extraction (spaCy/LLM-based), storing in SQLite with search indexing, and exposing AI-powered querying through a TypeScript web interface.

**Key architectural insight:** Modern document systems separate "batch processing" (ingestion pipeline) from "interactive query" (runtime services). The ingestion pipeline is idempotent and parallelizable, while the query layer is stateless and horizontally scalable.

## Recommended System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INGESTION PIPELINE                         │
│  (Batch processing - can run on-demand or scheduled)                 │
└─────────────────────────────────────────────────────────────────────┘
   │
   │ Downloads
   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Download   │───▶│  PDF Parse   │───▶│  Chunk/Prep  │───▶│   Extract    │
│   Agent      │    │  & OCR       │    │  Pipeline    │    │  Entities    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                  │
                                                                  │ Relationships
                                                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         STORAGE LAYER                                │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │   Documents  │  │  Full-Text   │  │  Entities    │  │  Vector  │ │
│  │   Metadata   │  │  Search Idx  │  │  & Relations │  │  Store   │ │
│  │  (SQLite)    │  │  (FTS5)      │  │  (SQLite)    │  │(SQLite)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Query / Index
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         QUERY LAYER                                  │
│  (Interactive - responds to user requests)                           │
│                                                                      │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│  │  Natural Lang  │  │  Retriever     │  │  Response      │        │
│  │  → Query       │──▶│  (Search/LLM)  │──▶│  Generator     │        │
│  │  Translator    │  │                │  │  (LLM)         │        │
│  └────────────────┘  └────────────────┘  └────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Communicates With | Technology |
|-----------|---------------|-------------------|------------|
| **Download Agent** | Fetch PDFs from justice.gov/epstein | Parsing Service | Python + requests/aiohttp |
| **PDF Parser** | Extract text, tables, layout; OCR if needed | Chunker | pypdf/pdfplumber + OCRmyPDF |
| **Chunker/Preprocessor** | Split documents, clean text, normalize | Extractor | Custom Python |
| **Entity Extractor** | Extract names, dates, locations, events | Relationship Extractor | spaCy + LLM API |
| **Relationship Extractor** | Identify connections (met, communicated) | Storage Layer | LLM API + pattern matching |
| **Document Store** | Raw PDFs + metadata | All components | Filesystem + SQLite |
| **Search Index** | Full-text search capability | Query Layer | SQLite FTS5 |
| **Entity Graph** | Structured entities + relationships | Query Layer | SQLite + optional NetworkX |
| **Query Translator** | Natural language → structured query | Retriever | LLM API (function calling) |
| **Retriever** | Fetch relevant chunks/entities | Generator | SQLite + vector search |
| **Response Generator** | Synthesize answers from retrieved data | Web Interface | LLM API |
| **Web Interface** | Browse docs, run queries, visualize | User | TypeScript + React/FastAPI |

## Data Flow

### Ingestion Flow (One-Way, Batch)

```
Raw PDF (justice.gov)
        │
        ▼
┌───────────────┐
│ Download      │ ── Save to filesystem
│ (idempotent)  │ ── Record metadata in SQLite
└───────────────┘
        │
        ▼
┌───────────────┐
│ PDF Parse     │ ── Extract raw text
│ (pdfplumber)  │ ── Extract tables/structure
└───────────────┘
        │
        ▼
┌───────────────┐
│ Chunk/Prep    │ ── Split into pages/paragraphs
│ (chunking)    │ ── Clean whitespace, normalize dates
└───────────────┘
        │
        ▼
┌───────────────┐
│ Entity Extraction ── NER (names, dates, locations)
│ (spaCy/LLM)   │ ── Store entity spans with provenance
└───────────────┘
        │
        ▼
┌───────────────┐
│ Relationship  │ ── Extract co-occurrence in chunks
│ Extraction    │ ── LLM-based relation classification
└───────────────┘
        │
        ▼
┌───────────────┐
│ Index & Store │ ── Update FTS5 index
│ (SQLite)      │ ── Store entities + relations
│               │ ── Optional: Generate embeddings
└───────────────┘
```

### Query Flow (Interactive, State-Less)

```
User Query (natural language)
        │
        ▼
┌───────────────┐
│ Query         │ ── Parse intent (search, summarize, relationship)
│ Translator    │ ── Extract entities mentioned in query
│ (LLM)         │ ── Route to appropriate retriever
└───────────────┘
        │
        ├─── Entity search ──┐
        │                    ▼
        │           ┌─────────────┐
        │           │ Entity DB   │ ── Return matching entities
        │           │ (SQLite)    │
        │           └─────────────┘
        │
        ├─── Full-text search ──┐
        │                        ▼
        │               ┌─────────────┐
        │               │ FTS5 Index  │ ── Return matching documents
        │               │ (SQLite)    │
        │               └─────────────┘
        │
        ├─── Vector search ──┐ (if embeddings enabled)
        │                    ▼
        │           ┌─────────────┐
        │           │ Vector DB   │ ── Return similar chunks
        │           │ (pgvector)  │
        │           └─────────────┘
        │
        ▼
┌───────────────┐
│ Retriever     │ ── Deduplicate results
│ (Orchestrator)│ ── Rank by relevance
└───────────────┘
        │
        ▼
┌───────────────┐
│ Generator     │ ── Synthesize answer
│ (LLM)         │ ── Cite sources (document IDs, page numbers)
└───────────────┘
        │
        ▼
    Response
```

## Suggested Build Order

Based on architectural dependencies, build in this order:

### Phase 1: Foundation (Weeks 1-2)
1. **Document Store** - SQLite schema for documents, metadata
2. **Download Agent** - Script to fetch from justice.gov
3. **Basic PDF Parser** - pypdf/pdfplumber integration
4. **Simple Web Interface** - Document browser (Next.js or FastAPI)

**Why this order:** Without document storage and basic parsing, nothing else works. Web interface provides immediate feedback loop.

### Phase 2: Search & Query (Weeks 3-4)
1. **Full-Text Index** - SQLite FTS5 implementation
2. **Basic Search API** - Endpoint for document search
3. **Query Translator** - Simple entity extraction from queries
4. **Retrieval Pipeline** - Basic BM25 + keyword search

**Why this order:** Enables basic functionality ("find documents mentioning X"). This is table stakes.

### Phase 3: Intelligence (Weeks 5-6)
1. **Entity Extractor** - spaCy pipeline for NER
2. **Entity Store** - Schema for entities + provenance
3. **Relationship Extraction** - Co-occurrence + LLM patterns
4. **Relationship Store** - Graph structure in SQLite

**Why this order:** Entities build on parsed documents. Relationships depend on entities.

### Phase 4: AI Query (Weeks 7-8)
1. **Advanced Query Translator** - LLM-based query understanding
2. **Hybrid Retriever** - Combine FTS + entity + relationship search
3. **Response Generator** - RAG with citation
4. **Vector Search** (optional) - pgvector for semantic similarity

**Why this order:** AI features require the underlying data structures (entities, relationships) to exist first.

## Architecture Patterns to Follow

### Pattern 1: Separation of Concerns (Ingestion vs Query)

**What:** Keep batch processing (ingestion) completely separate from interactive services (query).

**Why:** Ingestion is I/O and CPU intensive; query needs low latency. Separation allows independent scaling and prevents ingestion from degrading query performance.

**Implementation:**
```python
# Ingestion pipeline (can run offline, scheduled, parallel)
class IngestionPipeline:
    def process_document(self, pdf_path: Path) -> None:
        raw_text = self.parser.extract(pdf_path)
        chunks = self.chunker.split(raw_text)
        entities = self.ner.extract(chunks)
        self.store.save(pdf_path, chunks, entities)

# Query service (fast, stateless)
class QueryService:
    def search(self, query: str) -> List[Result]:
        # Only reads from storage, never modifies
        return self.retriever.retrieve(query)
```

### Pattern 2: Provenance Tracking

**What:** Every extracted entity and relationship must trace back to its source document location.

**Why:** For legal/research use cases, users need to verify claims. Provenance enables "show me where this came from."

**Implementation:**
```python
@dataclass
class Entity:
    text: str
    type: str  # PERSON, DATE, LOCATION, EVENT
    document_id: str
    page_number: int
    paragraph_number: int
    confidence: float
```

### Pattern 3: Idempotent Ingestion

**What:** Re-processing the same document produces the same result without duplications.

**Why:** Allows retries, resumable processing, and incremental updates.

**Implementation:**
```python
def process_document(pdf_url: str) -> None:
    doc_id = hashlib.sha256(pdf_url.encode()).hexdigest()[:16]
    
    if db.document_exists(doc_id):
        logger.info(f"Skipping {pdf_url}, already processed")
        return
    
    # ... processing logic ...
    db.save_document(doc_id, ...)
```

### Pattern 4: Chunking Strategy

**What:** Split documents into overlapping chunks that preserve context.

**Why:** LLMs have token limits; chunking enables processing long documents. Overlap prevents entities/relationships from being split across chunks.

**Implementation:**
```python
def chunk_document(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap  # Overlap for context continuity
    return chunks
```

### Pattern 5: Hybrid Search

**What:** Combine keyword search (BM25/FTS) with semantic search (embeddings).

**Why:** Keyword search is precise for exact matches; semantic search catches related concepts. Hybrid gives best of both.

**Implementation:**
```python
def hybrid_search(query: str, k: int = 10) -> List[Result]:
    # Keyword search
    keyword_results = fts_index.search(query, k=k)
    
    # Semantic search (if embeddings available)
    query_embedding = embedding_model.encode(query)
    semantic_results = vector_db.similarity_search(query_embedding, k=k)
    
    # Reciprocal Rank Fusion for combining
    return reciprocal_rank_fusion(keyword_results, semantic_results)
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Processing on Query Path

**What:** Running PDF parsing or entity extraction during a user query request.

**Why bad:** Makes queries slow and unpredictable. Violates separation of concerns.

**Instead:** All processing happens in ingestion pipeline. Query layer only reads pre-computed data.

### Anti-Pattern 2: Storing Only Embeddings

**What:** Converting documents to embeddings and discarding original text.

**Why bad:** Lose ability to verify, cite sources, or debug. Embeddings are opaque.

**Instead:** Store original text, parsed structure, AND embeddings. Use embeddings for retrieval, original text for generation.

### Anti-Pattern 3: Monolithic Database Schema

**What:** Single table with documents, entities, relationships all mixed.

**Why bad:** Hard to query, inefficient indexes, poor separation of entity types.

**Instead:** Normalized schema:
- `documents` (id, source_url, title, processed_at)
- `chunks` (id, document_id, content, page_number)
- `entities` (id, chunk_id, text, type, start_pos, end_pos)
- `relationships` (id, source_entity_id, target_entity_id, relation_type, evidence)

### Anti-Pattern 4: Synchronous Entity Extraction

**What:** Running spaCy/LLM NER inline during document upload.

**Why bad:** Blocks user; if extraction fails, document appears lost.

**Instead:** Queue documents for background processing. Show "processing" status in UI.

## Database Schema (MVP - SQLite)

```sql
-- Documents table
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    source_url TEXT NOT NULL,
    title TEXT,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    page_count INTEGER,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending' -- pending, processing, completed, failed
);

-- Full-text search virtual table
CREATE VIRTUAL TABLE document_search USING fts5(
    content,
    document_id,
    chunk_index
);

-- Document chunks
CREATE TABLE chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT REFERENCES documents(id),
    chunk_index INTEGER,
    content TEXT NOT NULL,
    page_number INTEGER,
    char_start INTEGER,
    char_end INTEGER
);

-- Extracted entities
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER REFERENCES chunks(id),
    document_id TEXT REFERENCES documents(id),
    text TEXT NOT NULL,
    type TEXT NOT NULL, -- PERSON, ORGANIZATION, DATE, LOCATION, EVENT
    start_pos INTEGER,
    end_pos INTEGER,
    confidence REAL
);

-- Entity indexes for fast lookup
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entities_text ON entities(text);
CREATE INDEX idx_entities_document ON entities(document_id);

-- Relationships between entities
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity_id INTEGER REFERENCES entities(id),
    target_entity_id INTEGER REFERENCES entities(id),
    relation_type TEXT NOT NULL, -- MET_WITH, COMMUNICATED_WITH, ASSOCIATED_WITH
    evidence_chunk_id INTEGER REFERENCES chunks(id),
    confidence REAL,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for relationship queries
CREATE INDEX idx_relations_source ON relationships(source_entity_id);
CREATE INDEX idx_relations_target ON relationships(target_entity_id);
CREATE INDEX idx_relations_type ON relationships(relation_type);

-- Optional: Vector embeddings (requires sqlite-vss or switch to pgvector)
-- For MVP, use pgvector PostgreSQL or store embeddings in separate file
```

## Scalability Considerations

| Concern | At 100 docs | At 1K docs | At 10K+ docs |
|---------|-------------|------------|--------------|
| **Storage** | SQLite fine | SQLite fine | Migrate to PostgreSQL |
| **Search** | FTS5 sufficient | FTS5 + basic indexes | Add pgvector, consider Elasticsearch |
| **Ingestion** | Single process | Parallel workers (4-8) | Queue-based (Celery/RQ) |
| **Entity Extraction** | Local spaCy | Local spaCy + batching | Distributed LLM API calls |
| **Embeddings** | Skip for MVP | Local model | API-based (OpenAI/Anthropic) |
| **Query Latency** | <100ms | <200ms | Cache frequent queries |

## Technology Integration Points

### Python ↔ TypeScript Communication

For the Epstein Files project (Python backend + TypeScript frontend):

**Option 1: REST API (Recommended for MVP)**
```python
# FastAPI backend
from fastapi import FastAPI
app = FastAPI()

@app.get("/api/documents")
def list_documents():
    return db.get_documents()

@app.post("/api/query")
def query_documents(query: QueryRequest):
    return query_service.search(query.text)
```

**Option 2: Direct SQLite Access (Simpler, but coupling)**
- TypeScript/Node reads SQLite directly
- Only works for read-only operations
- Requires shared filesystem

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Component Boundaries | HIGH | Well-established patterns in document AI systems |
| Data Flow | HIGH | Clear separation of ingestion/query is standard |
| Build Order | MEDIUM | Based on dependency logic; may need iteration |
| SQLite Schema | MEDIUM | Verified against similar projects; may need normalization adjustments |
| Python Libraries | HIGH | WebSearch confirmed pdfplumber/pypdf are current (2025) |
| Entity Extraction | MEDIUM | spaCy is solid baseline; LLM-based needs validation |
| RAG Architecture | HIGH | Multiple authoritative sources confirm patterns |

## Research Gaps

1. **Justice.gov structure**: Need to verify exact download mechanism (API vs scraping)
2. **PDF characteristics**: Unknown if files are scanned images or text-based (affects OCR needs)
3. **Entity types**: Should verify which entity types are most useful for legal documents
4. **Query patterns**: Need to understand common user questions to optimize retrieval

## Sources

- [Databricks Document Intelligence](https://www.databricks.com/blog/pdfs-production-announcing-state-art-document-intelligence-databricks) - Nov 2025
- [Docling Architecture DeepWiki](https://deepwiki.com/docling-project/docling/5.1-standard-pdf-pipeline) - Jan 2026
- [PDF Extraction 2025 Comparison](https://onlyoneaman.medium.com/i-tested-7-python-pdf-extractors-so-you-dont-have-to-2025-edition-c88013922257) - Jul 2025
- [pdfplumber Official](https://www.pdfplumber.com/) - Jun 2025
- [RAG Architecture Survey](https://arxiv.org/html/2506.00054v1) - Nov 2025
- [Haystack Pipelines](https://docs.haystack.deepset.ai/docs/pipelines) - Official docs
- [Haystack 2.0 Release](https://haystack.deepset.ai/blog/haystack-2-release) - Mar 2024
- [pgvector PostgreSQL Guide](https://supabase.com/docs/guides/database/extensions/pgvector) - Sep 2025
- [Vector Search Benchmarking](https://www.instaclustr.com/blog/vector-search-benchmarking-setting-up-embeddings-insertion-and-retrieval-with-postgresql/) - Nov 2025
- [Relationship Extraction arXiv](https://arxiv.org/abs/2404.12788) - Apr 2024
- [Knowledge Graph Building Guide](https://medium.com/@brian-curry-research/building-a-knowledge-graph-a-comprehensive-end-to-end-guide-using-modern-tools-e06fe8f3b368) - Jan 2026
