# Research Summary: Epstein Files Document Cataloging System

**Project:** AI-powered document cataloging for DOJ Epstein file releases  
**Synthesized:** 2026-02-02  
**Overall Confidence:** MEDIUM-HIGH

---

## Executive Summary

The Epstein Files project requires building an AI-powered document intelligence platform for government investigation documents. Research indicates the optimal approach combines **Python-based data processing** with a **TypeScript/Next.js web interface**, following a **RAG (Retrieval-Augmented Generation) architecture** with **mandatory source citations**.

The recommended path is a **4-phase build** starting with document ingestion and full-text search (foundational), then adding entity extraction and relationships (intelligence layer), followed by AI-powered Q&A with citations (differentiation), and finally vector search and advanced visualizations (polish). Key risks center on **PDF parsing complexity** (mixed scanned/digital documents), **entity disambiguation** (multiple people with same names), and **AI hallucinations** without verifiable citations — all of which can destroy credibility in a journalism/legal research context.

The technology stack is well-established and confident: PyMuPDF for PDF extraction, FastAPI for the backend API, ChromaDB for local vector storage, spaCy + LLM hybrid for entity extraction, and OpenAI's text-embedding-3-small for cost-effective embeddings. SQLite is recommended for the MVP database with a clear migration path to PostgreSQL + pgvector at scale.

---

## Key Findings

### From STACK.md: Technology Recommendations

| Technology | Purpose | Rationale |
|------------|---------|-----------|
| **PyMuPDF** (fitz) | PDF text/image extraction | Best-in-class for complex PDFs; 10x faster than alternatives; handles scanned docs, tables, layout preservation |
| **FastAPI** | Web framework | Async-native (crucial for I/O-heavy PDF/LLM operations); automatic OpenAPI docs; Pydantic validation; 15-20k req/sec |
| **ChromaDB** | Vector database (MVP) | Zero-setup, embedded mode; seamless Python integration; scales to millions locally |
| **spaCy** (en_core_web_trf) | Named Entity Recognition | Production-grade NER; 95%+ accuracy on legal documents; 18+ entity types |
| **OpenAI text-embedding-3-small** | Embeddings | 1536 dims, 62% cost reduction vs ada-002, better MTEB scores |
| **Next.js 15 + shadcn/ui** | Frontend | App Router, server components, copy-paste accessible UI components |
| **SQLite** | Document metadata (MVP) | Zero-config, file-based, JSON1 extension for metadata, FTS5 for full-text search |

**Key Version Requirements:**
- PyMuPDF ^1.25.0 (recent major improvements)
- FastAPI ^0.115.0 (stable 0.x API)
- ChromaDB ^0.6.0 (before 1.0 breaking changes)
- spaCy ^3.8.0 with en_core_web_trf (transformer model for accuracy)

### From FEATURES.md: Feature Priorities

**Table Stakes (Must-Have for MVP):**
- Full-text search with BM25 ranking and snippets
- PDF text extraction with OCR for scanned documents
- Document listing/browsing with pagination and metadata
- Basic entity extraction (names, dates, organizations)
- Download original documents
- Responsive web interface

**Differentiators (Competitive Advantages):**
- **AI-powered Q&A with source citations** (document + page level) — Tier 1 differentiator
- **Entity relationship mapping** — visualize connections between people/orgs
- **Timeline visualization** — chronological view of events
- **Cross-document entity linking** — "John Smith in Doc A is same as Doc B"
- **Document clustering** — auto-group related documents by similarity
- **Deduplication** — identify identical/near-duplicate documents

**Anti-Features (Explicitly Avoid):**
- Automatic PII redaction (risk of over-redaction; provide detection only)
- Document editing (destroys chain of custody)
- User uploads (legal liability; restrict to official sources)
- Real-time collaborative editing (not needed; adds complexity)
- Multi-tenancy (single shared instance sufficient)
- Access control/permissions (public documents should be fully public)

**Deferred to v2+:**
- Advanced annotations with highlighting
- API access for programmatic queries
- Batch export to Zotero/Mendeley
- Redaction detection as a feature

### From ARCHITECTURE.md: System Design

**Core Architectural Pattern:**
Document intelligence systems follow a consistent pipeline: **Ingestion → Parsing → Enrichment → Storage → Retrieval → Query**

**Separation of Concerns:**
- **Ingestion Pipeline** (batch processing): Idempotent, parallelizable, can run offline/scheduled
- **Query Layer** (interactive): Stateless, horizontally scalable, low-latency reads only

**Major Components & Responsibilities:**
1. **Download Agent** — Fetch PDFs from justice.gov/epstein with resume/retry
2. **PDF Parser** — Extract text, tables, layout; OCR if needed (classify first!)
3. **Chunker/Preprocessor** — Split documents with semantic boundaries and 10-20% overlap
4. **Entity Extractor** — spaCy for fast NER + LLM for complex relationship extraction
5. **Relationship Extractor** — Co-occurrence patterns + LLM-based classification
6. **Storage Layer** — SQLite for metadata/entities/relationships + Chroma for vectors
7. **Query Translator** — Natural language → structured query (LLM function calling)
8. **Retriever** — Hybrid search combining FTS + entity + relationship search
9. **Response Generator** — RAG with mandatory citation verification
10. **Web Interface** — Next.js frontend for browsing, search, Q&A, visualizations

**Key Patterns to Follow:**
- **Provenance Tracking** — Every entity/relationship traces to source document (page, paragraph, line)
- **Idempotent Ingestion** — Re-processing same document produces same result (hash-based IDs)
- **Semantic Chunking** — Split at natural boundaries (paragraphs, sections) with overlap
- **Hybrid Search** — Combine keyword (BM25/FTS) + semantic (embeddings) via Reciprocal Rank Fusion

**Database Schema (MVP - SQLite):**
- `documents` — metadata, source URL, processing status
- `chunks` — document segments with page numbers and positions
- `entities` — extracted entities with type, confidence, provenance
- `relationships` — entity connections with evidence and confidence
- `document_search` — FTS5 virtual table for full-text search

### From PITFALLS.md: Critical Risks

**Top 5 Critical Pitfalls:**

1. **Treating All PDFs the Same** (Phase 1)
   - **Risk:** Silent data loss from mixed native/scanned PDFs, poor OCR, garbled tables
   - **Prevention:** Classify documents first; route to appropriate parser; quality gates for extraction completeness

2. **Entity Extraction Without Disambiguation** (Phase 2-3)
   - **Risk:** Conflating "John Smith" (attorney) with "John Smith" (witness); false relationship mapping
   - **Prevention:** Contextual extraction with surrounding text; entity resolution pipeline; canonical entity profiles; 0.85+ confidence threshold for auto-linking

3. **AI Answers Without Verifiable Citations** (Phase 4)
   - **Risk:** Catastrophic credibility loss; legal implications; misinformation spread
   - **Prevention:** Mandatory citation grounding to document + page; post-process verification; source-first prompts; confidence scoring on answers

4. **Ignoring Redaction Patterns** (Phase 1)
   - **Risk:** False entities from redaction artifacts; missing context; accidental exposure
   - **Prevention:** Redaction detection via visual analysis; store redaction metadata; mark explicitly in extracted text; security audit

5. **Poor Text Chunking Breaking Context** (Phase 2)
   - **Risk:** Lost context at chunk boundaries; retrieval misses; LLM answers lack full context
   - **Prevention:** Semantic chunking at paragraph/section boundaries; hierarchical parent-child relationships; 10-20% overlap; contextual metadata

**Moderate Pitfalls:**
- Not handling handwritten notes (marginalia, signatures)
- Database schema not designed for document relationships
- No pipeline observability (stage tracking, error classification)
- Inadequate testing on document diversity (poor scans, mixed orientations)
- Premature optimization for scale (over-engineering for current dataset size)

**Minor Pitfalls:**
- Not normalizing entity names ("John Smith" vs "Smith, John")
- No full-text backup for vector search
- Missing document metadata (filename, release batch, page count)

---

## Implications for Roadmap

### Suggested Phase Structure

Based on research findings, the optimal build order follows architectural dependencies while addressing highest-risk pitfalls early:

| Phase | Focus | Duration | Key Deliverables |
|-------|-------|----------|------------------|
| **Phase 1** | Foundation | Weeks 1-2 | Document ingestion, storage, basic web UI |
| **Phase 2** | Search & Entities | Weeks 3-4 | Full-text search, basic NER, entity listing |
| **Phase 3** | Intelligence | Weeks 5-6 | Relationship extraction, entity graph, timeline |
| **Phase 4** | AI Q&A | Weeks 7-8 | RAG pipeline, citation verification, hybrid search |
| **Phase 5** | Polish | Week 9+ | Clustering, deduplication, advanced filters, UI polish |

### Phase 1: Foundation (Weeks 1-2)

**Rationale:** Without document storage and parsing, nothing else works. Must address PDF classification and redaction detection immediately (critical pitfalls).

**Features from FEATURES.md:**
- PDF text extraction with OCR detection
- Document listing/browsing with metadata
- Download original documents
- Basic responsive web interface

**Must Avoid Pitfalls:**
- Pitfall 1: Implement PDF classification (native vs scanned) before parsing
- Pitfall 4: Add redaction detection to preserve context
- Pitfall 10: Use SQLite (don't over-engineer for scale)

**Components:**
- Document Store (SQLite schema)
- Download Agent with retry logic
- PDF Parser with classification (native vs scanned)
- Simple Web Interface (Next.js document browser)

**Research Flag:** ⚠️ NEEDS RESEARCH — Justice.gov download mechanism (API vs scraping), actual PDF characteristics (scanned vs text-based)

### Phase 2: Search & Entities (Weeks 3-4)

**Rationale:** Enables core table stakes functionality ("find documents mentioning X"). Establishes foundation for all AI features.

**Features from FEATURES.md:**
- Full-text search with snippets (SQLite FTS5)
- Basic entity extraction (spaCy)
- Simple entity listing per document
- Search result display with context

**Must Avoid Pitfalls:**
- Pitfall 5: Implement semantic chunking with overlap
- Pitfall 11: Normalize entity names during extraction
- Pitfall 13: Preserve all document metadata

**Components:**
- Full-Text Index (FTS5)
- Entity Extractor (spaCy pipeline)
- Chunker with semantic boundaries
- Basic Search API

**Research Flag:** ✅ STANDARD PATTERNS — FTS5 and spaCy are well-documented

### Phase 3: Intelligence (Weeks 5-6)

**Rationale:** Entities build on parsed documents; relationships depend on entities. Adds differentiation layer (entity graph, timeline).

**Features from FEATURES.md:**
- Entity relationship graph (simple visualization)
- Timeline view (date extraction + display)
- Cross-document entity linking (basic disambiguation)
- Advanced filters (by entity type, date range)

**Must Avoid Pitfalls:**
- Pitfall 2: Add contextual entity extraction; start entity resolution pipeline
- Pitfall 7: Ensure schema supports relationships
- Pitfall 9: Test on diverse document types

**Components:**
- Relationship Extractor (co-occurrence + LLM)
- Entity Store with provenance
- Simple Graph Visualization (D3.js or vis.js)
- Timeline Component

**Research Flag:** ⚠️ NEEDS RESEARCH — Optimal entity resolution approach for legal documents

### Phase 4: AI Q&A (Weeks 7-8)

**Rationale:** AI features require underlying data structures (entities, relationships, chunks) to exist first. Highest risk phase (citations, hallucinations).

**Features from FEATURES.md:**
- RAG-based Q&A with document citations
- Hybrid search (FTS + vector)
- Citation verification layer

**Must Avoid Pitfalls:**
- Pitfall 3: Mandatory citation grounding and verification
- Pitfall 12: Maintain parallel full-text index for exact matching
- Pitfall 6: Consider handwritten note handling if needed

**Components:**
- Advanced Query Translator (LLM function calling)
- Hybrid Retriever (FTS + entity + relationship)
- Response Generator with citation verification
- Vector Store integration (ChromaDB)

**Research Flag:** ⚠️ NEEDS RESEARCH — Citation verification implementation, optimal hybrid search weights

### Phase 5: Polish (Week 9+)

**Rationale:** Nice-to-have differentiators that improve UX but aren't core to functionality.

**Features from FEATURES.md:**
- Document clustering (similarity grouping)
- Deduplication (MinHash/LSH)
- Document annotations (highlights, notes)
- API access for programmatic queries
- Redaction detection as feature

**Components:**
- Clustering pipeline
- Deduplication engine
- Annotation system
- REST API with rate limiting

**Research Flag:** ✅ STANDARD PATTERNS — Well-documented algorithms

### Research Flags Summary

| Phase | Research Needed | Standard Patterns |
|-------|-----------------|-------------------|
| Phase 1 | Justice.gov scraping, PDF characteristics | SQLite, FastAPI basics |
| Phase 2 | — | FTS5, spaCy NER |
| Phase 3 | Entity resolution for legal docs | Graph visualization basics |
| Phase 4 | Citation verification, hybrid search tuning | RAG patterns |
| Phase 5 | — | Clustering algorithms |

---

## Confidence Assessment

| Area | Confidence | Basis |
|------|------------|-------|
| **Stack** | **HIGH** | Multiple authoritative sources (official docs, benchmarks, 2024-2025 comparisons); personal experience with FastAPI/spaCy; clear migration path documented |
| **Features** | **HIGH** | Analysis of existing platforms (DocumentCloud, FOIA.gov, Azure/Google Document AI); government document analysis patterns well-established; anti-features validated by NIST guidelines |
| **Architecture** | **MEDIUM-HIGH** | Well-established patterns in document AI systems; separation of ingestion/query is standard; SQLite schema may need normalization adjustments during implementation |
| **Pitfalls** | **HIGH** | Academic research (ACL 2024, Stanford legal RAG study, PDF Association Epstein case study); documented failures in production systems; domain-specific risks identified |

### Overall Confidence: MEDIUM-HIGH

**Why not HIGH overall:**
1. **Entity resolution** approaches for legal documents need validation
2. **Citation verification** implementation details require deeper research
3. **Actual PDF characteristics** from justice.gov are unknown (scanned vs text ratio, redaction patterns)

---

## Gaps to Address

### During Planning Phase

1. **Justice.gov Structure** — Need to verify exact download mechanism (API vs scraping) and document organization
2. **PDF Characteristics** — Unknown if Epstein files are primarily scanned images or text-based (affects OCR strategy)
3. **Entity Types Priority** — Should verify which entity types are most useful for legal/investigation documents (people, orgs, dates, locations, events)
4. **Query Patterns** — Need to understand common user questions to optimize retrieval (entity-centric vs event-centric vs relationship-centric)

### During Implementation

1. **Entity Disambiguation Thresholds** — Need to validate 0.85 confidence threshold through testing on actual document set
2. **Chunk Size Optimization** — Optimal chunk size/overlap for legal documents needs experimentation
3. **Citation Verification Rules** — Specific rules for what constitutes a valid citation in this domain

### Known Unknowns

- Actual volume of Epstein file releases (estimates vary from hundreds to tens of thousands)
- Presence of handwritten notes/marginalia in documents (affects OCR strategy)
- Redaction density and patterns (heavily redacted vs mostly complete)
- User technical sophistication (affects UI complexity decisions)

---

## Aggregated Sources

### Stack Sources
- PyMuPDF Documentation (https://pymupdf.readthedocs.io/)
- FastAPI Documentation (https://fastapi.tiangolo.com/)
- ChromaDB Documentation (https://docs.trychroma.com/)
- spaCy Documentation (https://spacy.io/usage)
- OpenAI Embedding Models (Jan 2024)
- PDF Library Benchmarks (https://github.com/py-pdf/benchmarks)
- Vector DB Comparison 2025
- Chunking Strategies for RAG (Firecrawl, 2025)

### Feature Sources
- DocumentCloud platform analysis
- Azure AI Document Intelligence (Microsoft, 2024)
- Google Cloud Document AI overview (2025)
- FOIA.gov search tool upgrades (DOJ OIP, 2024-2025)
- paper-qa RAG implementation (Future-House)
- Sema4.ai Document Intelligence analysis
- GovScape: A Public Multimodal Search System (arXiv 2025)
- NIST SP 800-188 De-Identifying Government Datasets (2023)

### Architecture Sources
- Databricks Document Intelligence (Nov 2025)
- Docling Architecture DeepWiki (Jan 2026)
- PDF Extraction 2025 Comparison
- RAG Architecture Survey (arXiv, Nov 2025)
- Haystack Pipelines (Official docs)
- pgvector PostgreSQL Guide (Supabase, Sep 2025)
- Relationship Extraction (arXiv, Apr 2024)
- Knowledge Graph Building Guide (Jan 2026)

### Pitfalls Sources
- OCRmyPDF Documentation
- "Demystifying PDF Parsing" (May 2024)
- "olmOCR: Unlocking Trillions of Tokens" (Allen Institute, Feb 2025)
- ACL W-NUT 2024 papers on NER data quality
- "AmbigDocs: Reasoning across Documents" (arXiv 2024)
- Stanford study on Legal RAG Hallucinations (May 2024)
- "Seven Failure Points When Engineering RAG" (arXiv Jan 2024)
- PDF Association case study on Epstein PDFs
- Chroma Research on Chunking Strategies (July 2024)
- "Late Chunking" (Jina AI, 2024)

---

## Next Steps

1. **Proceed to Requirements** — Research complete, ready for detailed requirements definition
2. **Address Research Flags** — Run `/gsd-research-phase` for Phase 1 (download mechanism) and Phase 4 (citation verification) during planning
3. **Validate Assumptions** — Sample actual Epstein PDFs early to validate PDF characteristics and redaction patterns
4. **Start with SQLite MVP** — Don't over-engineer; migrate to PostgreSQL only when actual scaling needs emerge

---

*This summary synthesizes findings from STACK.md, FEATURES.md, ARCHITECTURE.md, and PITFALLS.md to inform roadmap creation.*
