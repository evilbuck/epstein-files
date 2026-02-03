# Technology Stack

**Project:** Epstein Files Document Cataloging System  
**Researched:** 2026-02-02  
**Domain:** AI-powered document cataloging, NLP entity extraction, RAG-based querying

## Executive Summary

For an AI-powered document cataloging system in 2025, the optimal stack combines Python for data processing (PDF parsing, NLP, embeddings) with TypeScript/Next.js for the web interface. Key decisions: **PyMuPDF** for PDF extraction (superior to pypdf/pdfplumber for complex documents), **OpenAI text-embedding-3-small** for cost-effective embeddings (1536 dimensions), **ChromaDB** for local vector storage (zero-config, seamless Python integration), and **FastAPI** for the backend API (async support, automatic documentation, Pydantic validation).

## Recommended Stack

### Core Data Processing (Python)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **PyMuPDF** (fitz) | ^1.25.0 | PDF text/image extraction | Best-in-class for complex PDFs; 10x faster than PyPDF2; handles scanned docs, tables, layout preservation; pure Python bindings to MuPDF engine [Confidence: HIGH] |
| **pypdf** | ^5.1.0 | Fallback/simple PDF operations | Pure Python, no deps; good for metadata extraction, page manipulation; use when PyMuPDF unavailable [Confidence: HIGH] |
| **pdfplumber** | ^0.11.0 | Table extraction | Superior for structured data extraction from PDF tables; built on pdfminer.six [Confidence: HIGH] |
| **langchain-text-splitters** | ^0.3.0 | Document chunking | Industry standard for RAG text splitting; RecursiveCharacterTextSplitter with semantic boundaries [Confidence: HIGH] |
| **openai** | ^1.59.0 | LLM API client | Official SDK; supports GPT-4o, GPT-4o-mini, embedding models; streaming, function calling [Confidence: HIGH] |
| **anthropic** | ^0.42.0 | Alternative LLM client | Claude 3.5 Sonnet for high-quality entity extraction and reasoning; excellent for legal/investigation documents [Confidence: HIGH] |

### NLP & Entity Extraction

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **spaCy** | ^3.8.0 | Named Entity Recognition (NER) | Production-grade NER; en_core_web_trf for high accuracy; custom entity training; 18+ entity types (PERSON, ORG, GPE, DATE, etc.) [Confidence: HIGH] |
| **transformers** (Hugging Face) | ^4.48.0 | Advanced NER / embedding | For domain-specific fine-tuned models; BERT-based NER models; optional for specialized entity types [Confidence: MEDIUM] |
| **GLiNER** | ^0.2.0 | Zero-shot NER | Extract arbitrary entity types without training; "extract all dates mentioned in meetings" [Confidence: MEDIUM] |

### Vector Storage & Search

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **ChromaDB** | ^0.6.0 | Vector database (MVP) | Zero-setup, embedded mode; DuckDB backend; OpenAI-compatible; scales to millions of docs locally [Confidence: HIGH] |
| **sentence-transformers** | ^3.3.0 | Local embeddings (optional) | Run embeddings locally without API; all-MiniLM-L6-v2 for 384-dim vectors; privacy-preserving [Confidence: MEDIUM] |

**Rationale for ChromaDB over alternatives:**
- **vs FAISS**: Chroma offers persistence, metadata filtering, and simpler API; FAISS is lower-level
- **vs Pinecone**: Chroma has no cloud dependency, zero cost, local-first; Pinecone better for production multi-tenant
- **vs Weaviate**: Chroma simpler for single-node Python projects; Weaviate adds unnecessary complexity for MVP

### Backend API

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **FastAPI** | ^0.115.0 | Web framework | Async by default (Starlette); automatic OpenAPI docs; Pydantic validation; 15,000-20,000 req/sec; native WebSocket support [Confidence: HIGH] |
| **Pydantic** | ^2.10.0 | Data validation | V2 is 5-50x faster than V1; type-safe request/response models; JSON Schema generation [Confidence: HIGH] |
| **uvicorn** | ^0.34.0 | ASGI server | Production-grade; Gunicorn integration; HTTP/2 support [Confidence: HIGH] |
| **SQLAlchemy** | ^2.0.36 | Database ORM | Modern 2.0 API; async support; type hints; SQLite/PostgreSQL compatibility [Confidence: HIGH] |
| **alembic** | ^1.14.0 | Database migrations | SQLAlchemy companion; version control for schema changes [Confidence: HIGH] |
| **python-multipart** | ^0.0.20 | File upload handling | For PDF upload endpoints; FastAPI integration [Confidence: HIGH] |

**Why FastAPI over Flask:**
- Async support crucial for I/O-bound operations (PDF processing, LLM API calls)
- 5-10x better performance under concurrent load
- Automatic API documentation (Swagger UI, ReDoc) out of the box
- Pydantic integration eliminates manual validation code
- Modern Python typing support

### Database

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **SQLite** | 3.40+ | Document metadata storage | Zero-config, file-based; perfect for MVP; JSON1 extension for metadata; FTS5 for full-text search [Confidence: HIGH] |
| **sqlite-vec** (optional) | ^0.1.0 | Vector search in SQLite | If Chroma too heavy; native SQLite extension for vector similarity search [Confidence: MEDIUM] |

**SQLite Schema Recommendation:**
```sql
-- Documents table
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    source_url TEXT,
    file_size INTEGER,
    page_count INTEGER,
    extracted_text TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON  -- SQLite JSON1 extension
);

-- Entities table (extracted by spaCy/LLM)
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER REFERENCES documents(id),
    entity_text TEXT NOT NULL,
    entity_type TEXT NOT NULL,  -- PERSON, ORG, DATE, etc.
    start_pos INTEGER,
    end_pos INTEGER,
    confidence REAL
);

-- Full-text search index
CREATE VIRTUAL TABLE document_fts USING fts5(
    content='documents',
    content_rowid='id',
    extracted_text
);
```

### Frontend (TypeScript)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Next.js** | ^15.1.0 | React framework | App Router (server components); API routes; static generation; image optimization; Vercel integration [Confidence: HIGH] |
| **TypeScript** | ^5.7.0 | Type safety | Strict mode; path mapping; enhanced IDE support; reduces runtime errors [Confidence: HIGH] |
| **Tailwind CSS** | ^4.0.0 | Styling | Utility-first; design system consistency; smaller bundle than component libraries; dark mode support [Confidence: HIGH] |
| **shadcn/ui** | latest | UI components | Copy-paste components (not dependency); Radix UI primitives; Tailwind styling; accessible [Confidence: HIGH] |
| **TanStack Query** (React Query) | ^5.64.0 | Data fetching | Caching, background updates, optimistic updates; perfect for document list/entity queries [Confidence: HIGH] |
| **zustand** | ^5.0.0 | State management | Minimal boilerplate; TypeScript-friendly; handles search filters, UI state [Confidence: MEDIUM] |

### AI/LLM Configuration

#### Recommended Model Tiers

| Use Case | Recommended Model | Why |
|----------|-------------------|-----|
| **Entity Extraction** | GPT-4o-mini or Claude 3.5 Haiku | Fast, cost-effective; excellent for structured data extraction |
| **Complex Reasoning** | GPT-4o or Claude 3.5 Sonnet | Higher accuracy for relationship mapping, event extraction |
| **Embeddings** | text-embedding-3-small | 1536 dims, 62% cost reduction vs ada-002, better MTEB scores |
| **Local/Self-hosted** | Ollama + Llama 3.1 8B | Privacy, no API costs; good for development/testing |

#### Embedding Model Selection

| Model | Dimensions | Cost/1M tokens | Best For |
|-------|------------|----------------|----------|
| **text-embedding-3-small** (default) | 1536 | $0.020 | Balance of cost and quality; 99% of use cases [Confidence: HIGH] |
| text-embedding-3-large | 3072 | $0.130 | Maximum retrieval accuracy; larger context windows [Confidence: HIGH] |
| all-MiniLM-L6-v2 (local) | 384 | $0 | Privacy-critical; offline operation; lower quality [Confidence: MEDIUM] |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **tqdm** | ^4.67.0 | Progress bars | Batch PDF processing UX |
| **python-dotenv** | ^1.0.0 | Environment config | API keys, database paths |
| **loguru** | ^0.7.0 | Logging | Structured logging for processing pipeline |
| **typer** | ^0.15.0 | CLI interface | Document processing CLI tools |
| **httpx** | ^0.28.0 | Async HTTP client | Faster than requests for concurrent API calls |
| **aiofiles** | ^24.1.0 | Async file I/O | Non-blocking PDF file operations |
| **tenacity** | ^9.0.0 | Retry logic | Resilient API calls with exponential backoff |

## Installation Commands

### Python Backend

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Core PDF processing
pip install pymupdf pypdf pdfplumber

# NLP & AI
pip install spacy openai anthropic
python -m spacy download en_core_web_sm  # Small model (~12MB)
# python -m spacy download en_core_web_md  # Medium (~40MB)
# python -m spacy download en_core_web_trf  # Transformer (~400MB, most accurate)

# Vector storage & chunking
pip install chromadb langchain-text-splitters

# Web framework
pip install fastapi uvicorn[standard] pydantic sqlalchemy alembic

# Utilities
pip install python-dotenv loguru typer httpx aiofiles tenacity tqdm

# Dev dependencies
pip install pytest pytest-asyncio ruff mypy
```

### TypeScript Frontend

```bash
# Initialize Next.js with shadcn
npx shadcn@latest init --yes --template next --base-color slate

# Install shadcn components
npx shadcn add button input card table badge dialog
npx shadcn add data-table  # For document/entity lists

# Data fetching & state
npm install @tanstack/react-query zustand

# HTTP client
npm install axios

# Date formatting
npm install date-fns

# Class name utilities
npm install clsx tailwind-merge
```

## Architecture Decisions

### Why This Stack?

**1. PyMuPDF over PyPDF2/pdfminer**
- Handles complex layouts that break other parsers
- Built-in OCR support for scanned documents
- Extracts images, tables, and text in single pass
- 10-20x faster performance benchmarks

**2. ChromaDB over Pinecone/Weaviate (for MVP)**
- Zero infrastructure: pip install and go
- Embeddable: no separate server process
- Migration path: Chroma Cloud or export to other vector DBs later
- Native Python integration

**3. FastAPI over Flask/Django**
- Async endpoints for concurrent PDF processing
- Automatic OpenAPI docs reduce API documentation burden
- Pydantic models ensure type safety across Python/TypeScript boundary
- Better performance for I/O-heavy workloads (LLM calls, file processing)

**4. text-embedding-3-small over ada-002**
- 62% cost reduction
- Better MTEB benchmark scores
- 1536 dimensions is sweet spot for Chroma/FAISS
- Shortening parameter allows quality/speed tradeoff

**5. spaCy + LLM hybrid approach**
- spaCy for fast, deterministic entity extraction (names, dates, orgs)
- LLM for relationship extraction and complex event understanding
- Reduces API costs by preprocessing with spaCy

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| **PDF Parsing** | PyMuPDF | Unstructured.io | Unstructured powerful but heavy (600MB+ deps), slower startup |
| **PDF Parsing** | PyMuPDF | AWS Textract | Cloud-only, per-page cost, network dependency |
| **Vector DB** | ChromaDB | Pinecone | Pinecone excellent but requires cloud account, network latency |
| **Vector DB** | ChromaDB | pgvector | Requires PostgreSQL setup; more complex for MVP |
| **Backend** | FastAPI | Django | Django overkill for API-only; FastAPI purpose-built for async APIs |
| **Backend** | FastAPI | Flask | Flask requires async extensions (Flask-Async, etc.); FastAPI async-native |
| **LLM** | OpenAI/Anthropic | Ollama (local) | Local models require GPU, slower; use Ollama for dev/fallback |
| **Embeddings** | OpenAI API | SentenceTransformers | Local embeddings add 400MB+ model download, slower CPU inference |

## What NOT to Use (Anti-Patterns)

### ❌ PyPDF2 as primary parser
**Why avoid:** Struggles with complex layouts, tables, multi-column documents. Use only for simple metadata extraction.

### ❌ Raw numpy for vector storage
**Why avoid:** No persistence, no metadata filtering, manual similarity computation. Chroma/FAISS provide this for free.

### ❌ spaCy `en_core_web_sm` for production NER
**Why avoid:** 91% accuracy vs 95%+ for `en_core_web_trf`. Small model misses complex entities in legal documents. Upgrade to transformer model after MVP.

### ❌ Flask with sync endpoints for PDF processing
**Why avoid:** Blocks on I/O; poor concurrency for batch processing. Use FastAPI async or at minimum Flask with Celery.

### ❌ MongoDB for document storage
**Why avoid:** Overkill for MVP; SQLite with JSON1 handles metadata; Chroma handles vectors. Add Mongo only if complex document relationships emerge.

## Confidence Assessment

| Component | Confidence | Notes |
|-----------|------------|-------|
| **PDF Parsing (PyMuPDF)** | HIGH | Multiple benchmarks confirm superiority; personal testing validated |
| **Embeddings (OpenAI)** | HIGH | Official docs, community consensus, cost benchmarks |
| **Vector DB (ChromaDB)** | HIGH | Documentation, growing ecosystem, proven in production |
| **Backend (FastAPI)** | HIGH | Personal experience, TechEmpower benchmarks, community adoption |
| **NLP (spaCy)** | HIGH | Industry standard, extensive docs, legal NLP use cases proven |
| **Frontend (Next.js)** | HIGH | Vercel standard, React Server Components proven pattern |
| **Local LLM (Ollama)** | MEDIUM | Rapidly evolving space; fallback option rather than primary |

## Migration Path to Production

When scaling beyond MVP:

1. **Database**: SQLite → PostgreSQL + pgvector (for vector search)
2. **Vector DB**: Chroma → Pinecone/Weaviate (for multi-tenant, cloud-native)
3. **Embeddings**: text-embedding-3-small → text-embedding-3-large (if accuracy needs increase)
4. **Processing**: Local → Celery + Redis (for distributed PDF processing)
5. **Storage**: Local filesystem → S3/R2 (for document storage)
6. **LLM**: API-only → API + Ollama cluster (for cost reduction at scale)

## Sources

- **PyMuPDF Documentation**: https://pymupdf.readthedocs.io/ (Official)
- **FastAPI Documentation**: https://fastapi.tiangolo.com/ (Official)
- **ChromaDB Documentation**: https://docs.trychroma.com/ (Official)
- **spaCy Documentation**: https://spacy.io/usage (Official)
- **OpenAI Embedding Models**: https://openai.com/blog/new-embedding-models-and-api-updates (Jan 2024)
- **FastAPI vs Flask 2025**: https://strapi.io/blog/fastapi-vs-flask-python-framework-comparison
- **PDF Library Benchmarks**: https://github.com/py-pdf/benchmarks
- **Vector DB Comparison 2025**: https://medium.com/@priyaskulkarni/vector-databases-for-rag-faiss-vs-chroma-vs-pinecone-6797bd98277d
- **Chunking Strategies**: https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025
- **Embedding Models RAG 2025**: https://www.zenml.io/blog/best-embedding-models-for-rag

## Version Pinning Strategy

For reproducible builds, use exact versions in production:

```toml
# pyproject.toml [project.dependencies] section
# Use ^ for minor version flexibility during development
# Pin exact versions in production requirements.txt

dependencies = [
    "pymupdf>=1.25.0,<2.0.0",
    "fastapi>=0.115.0,<0.116.0",
    "chromadb>=0.6.0,<0.7.0",
    "openai>=1.59.0,<2.0.0",
    # ... etc
]
```

**Last Updated:** 2026-02-02  
**Next Review:** When major versions released (FastAPI 1.0, Chroma 1.0, etc.)
