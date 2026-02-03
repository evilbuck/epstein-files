# Epstein Files Intelligence System

## What This Is

An AI-powered document cataloging system that downloads, organizes, and extracts meaning from the DOJ Epstein file releases. It enables researchers to ask questions about the documents and receive accurate, sourced answers by combining document scraping, entity extraction, and natural language querying.

## Core Value

**Researchers can ask questions about the Epstein documents and get accurate, sourced answers with citations to specific files and pages.**

Everything else can fail; this capability cannot. The system must deliver trustworthy answers backed by source material.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Download all released Epstein files from justice.gov/epstein
- [ ] Parse PDFs and extract clean, searchable text
- [ ] Store documents with metadata (source URL, release date, document ID)
- [ ] Extract entities (names, dates, locations, organizations, events)
- [ ] Build relationships between entities (who met whom, when, where)
- [ ] Enable full-text search across all documents
- [ ] Allow natural language queries with AI-generated answers
- [ ] Cite sources — every answer must reference specific documents and pages
- [ ] Provide web interface for browsing and querying
- [ ] Include reusable scripts for scraping similar document releases

### Out of Scope

- **Real-time document updates** — Manual re-runs of download scripts are acceptable for v1
- **Document comparison/diff** — Comparing different versions of same document is deferred
- **Audio/video processing** — Focus on text/PDF documents only for v1
- **Collaborative features** — No user accounts, annotations, or sharing in v1
- **Mobile app** — Web-first, mobile interface later if needed

## Context

**Target dataset:** DOJ Epstein file releases (https://www.justice.gov/epstein)

**Data characteristics:**
- Released in multiple "data sets" (1-11+ as of early 2025)
- Mix of PDFs, images, and text files
- Some datasets are bulk downloads, others require browser scraping
- Documents range from court filings to flight logs to correspondence

**Technical approach:**
- Python excels at document parsing (PDF extraction, NLP)
- SQLite sufficient for initial dataset size
- TypeScript/React suitable for query interface
- Mixed stack leverages best tool for each job

**Civic transparency motivation:** Government releases bulk documents without structure. This system transforms raw data into accessible intelligence.

## Constraints

- **Tech Stack**: Python (data processing), TypeScript (web interface), SQLite (database)
- **Data Source**: justice.gov/epstein only — don't scrape unrelated government sites
- **Citation Required**: Every AI answer must include document/page citations
- **Local-first**: System should run locally without cloud dependencies for researchers who need it
- **MVP Bias**: Prefer working pipelines over perfect extraction. Iterate on entity recognition.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Mixed stack (Python + TypeScript) | Python for NLP/document parsing, TS for web UI — best tool for each job | — Pending |
| SQLite for v1 | Sufficient for Epstein dataset, zero config, portable | — Pending |
| Entity extraction + relationship mapping | Essential for answering "who met whom when" questions | — Pending |
| Source citation mandatory | Trust requires verifiability; answers without sources are useless | — Pending |
| Reusable scraping framework | Other investigations (JFK, etc.) will have similar needs | — Pending |

---
*Last updated: 2025-02-02 after initialization*
