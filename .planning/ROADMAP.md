# Roadmap: Epstein Files Intelligence System

## Overview

This roadmap delivers an AI-powered document cataloging system that enables researchers to ask questions about DOJ Epstein file releases and receive accurate, sourced answers with document and page citations. The journey starts with document ingestion and foundational infrastructure, progresses through search and entity extraction capabilities, builds intelligence through relationships and timelines, adds AI-powered Q&A with mandatory citation verification, and finishes with UI polish and advanced features.

## Phases

- [ ] **Phase 1: Foundation** - Document ingestion, storage, parsing, and basic web UI
- [ ] **Phase 2: Search & Entities** - Full-text search and entity extraction (names, dates, locations, organizations)
- [ ] **Phase 3: Intelligence** - Entity relationships, graph visualization, and timeline
- [ ] **Phase 4: AI Q&A** - Natural language queries with citation verification and hybrid search
- [ ] **Phase 5: Polish** - UI enhancements, document annotations, and advanced features

## Phase Details

### Phase 1: Foundation
**Goal**: Documents are downloaded, parsed, stored with metadata, and accessible via web interface
**Depends on**: Nothing (first phase)
**Requirements**: INGEST-01, INGEST-02, INGEST-03, PARSE-01, PARSE-02, PARSE-03, UI-01, UI-02, AGENT-01
**Success Criteria** (what must be TRUE):
  1. User can view a list of all downloaded Epstein documents with metadata (source URL, release date, document ID)
  2. User can click any document to view/download the original PDF
  3. System extracts and displays searchable text from both native and scanned PDFs
  4. Document processing status is visible (pending/processing/completed/failed)
  5. Agent has access to all processed document data through defined API/schema
**Plans**: TBD

Plans:
- [ ] 01-01: Document download pipeline with retry/resume logic
- [ ] 01-02: SQLite schema and document storage layer
- [ ] 01-03: PDF parsing with OCR detection and text extraction
- [ ] 01-04: Basic Next.js web interface for document browsing
- [ ] 01-05: Quality verification and redaction detection

### Phase 2: Search & Entities
**Goal**: Users can search across all documents and discover extracted entities
**Depends on**: Phase 1
**Requirements**: SEARCH-01, SEARCH-02, SEARCH-03, ENTITY-01, ENTITY-02, ENTITY-03, ENTITY-04, UI-03, AGENT-02
**Success Criteria** (what must be TRUE):
  1. User can perform full-text search and see ranked results with snippets showing context around matches
  2. User can click search results to jump to the relevant document and page
  3. System automatically extracts and displays names, dates, organizations, and locations from documents
  4. User can view all entities mentioned in a specific document
  5. Search supports pagination for queries returning many results
  6. URLs can be shared for specific search queries and documents
  7. Agent can build and use tools from the project codebase
**Plans**: TBD

Plans:
- [ ] 02-01: SQLite FTS5 full-text search implementation
- [ ] 02-02: Search API with BM25 ranking and snippet generation
- [ ] 02-03: spaCy NER pipeline for entity extraction
- [ ] 02-04: Entity storage and API endpoints
- [ ] 02-05: Search UI with filters and pagination

### Phase 3: Intelligence
**Goal**: Users can explore connections between entities and view chronological event timelines
**Depends on**: Phase 2
**Requirements**: GRAPH-01, GRAPH-02, GRAPH-03, TIME-01, TIME-02, TIME-03, AGENT-03
**Success Criteria** (what must be TRUE):
  1. User can view a graph visualization showing relationships between people and organizations
  2. User can click on any entity to see its connections and related documents
  3. System identifies when the same entity appears across different documents
  4. User can view a chronological timeline of events extracted from documents
  5. Timeline can be filtered by entity or event type
  6. Dates are normalized and displayed consistently across all views
  7. Agent can perform analysis and identify interesting data points across documents
**Plans**: TBD

Plans:
- [ ] 03-01: Entity relationship extraction (co-occurrence + LLM classification)
- [ ] 03-02: Graph database structure and API
- [ ] 03-03: Simple network visualization (D3.js/vis.js)
- [ ] 03-04: Date extraction and normalization pipeline
- [ ] 03-05: Timeline component and filtering

### Phase 4: AI Q&A
**Goal**: Users can ask natural language questions and receive cited, verified answers
**Depends on**: Phase 3
**Requirements**: AI-01, AI-02, AI-03, AI-04, UI-04, AGENT-04
**Success Criteria** (what must be TRUE):
  1. User can ask natural language questions and receive AI-generated answers
  2. Every AI answer includes clickable citations to source documents and specific pages
  3. AI can synthesize information across multiple documents to answer complex questions
  4. AI indicates confidence level and expresses uncertainty when sources are unclear or conflicting
  5. Citation links are verified to actually support the claims made in the answer
  6. User can add highlights and notes to documents (annotations)
  7. Agent interactions are logged for transparency
**Plans**: TBD

Plans:
- [ ] 04-01: RAG pipeline with ChromaDB vector storage
- [ ] 04-02: Query translation and intent classification
- [ ] 04-03: Hybrid retriever (FTS + vector + entity search)
- [ ] 04-04: Response generator with mandatory citation verification
- [ ] 04-05: Annotation system for user highlights and notes

### Phase 5: Polish
**Goal**: System is polished with advanced features and complete web interface
**Depends on**: Phase 4
**Requirements**: (All v1 requirements already covered; this is enhancement phase)
**Success Criteria** (what must be TRUE):
  1. Web interface is responsive and works seamlessly across desktop, tablet, and mobile devices
  2. Document clustering groups related documents automatically
  3. Deduplication identifies identical or near-duplicate documents
  4. Advanced filters enable multi-faceted search by entity, date range, and document type
  5. System is performant with acceptable query latency even as dataset grows
**Plans**: TBD

Plans:
- [ ] 05-01: Document clustering and deduplication pipeline
- [ ] 05-02: Advanced faceted search UI
- [ ] 05-03: Performance optimization and caching
- [ ] 05-04: Responsive design polish and accessibility improvements

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/5 | Not started | - |
| 2. Search & Entities | 0/5 | Not started | - |
| 3. Intelligence | 0/5 | Not started | - |
| 4. AI Q&A | 0/5 | Not started | - |
| 5. Polish | 0/4 | Not started | - |
