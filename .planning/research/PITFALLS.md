# Domain Pitfalls: Document Processing & AI Analysis

**Domain:** AI-powered document cataloging for government/legal documents
**Researched:** February 2, 2026
**Project Context:** DOJ Epstein file releases - PDF processing, entity extraction, AI Q&A with citations

---

## Critical Pitfalls

Mistakes that cause rewrites, major data integrity issues, or complete loss of user trust.

### Pitfall 1: Treating All PDFs the Same

**What goes wrong:** Using a single parsing approach for all PDFs fails because government document releases contain a mix of:
- Native/digital PDFs with selectable text
- Scanned PDFs requiring OCR
- PDFs with both native and scanned pages
- Documents with complex layouts (tables, forms, multi-column)
- Files with poor scan quality or skewed pages

**Why it happens:** Teams assume PDF = text document. They don't detect document type upfront and route to appropriate processing pipeline.

**Consequences:** 
- Silent data loss (empty or garbled text extraction)
- "Missing" documents in search (they exist but have no extractable text)
- Tables extracted as unstructured text, losing relationships
- OCR errors propagate into entity extraction, creating false entities

**Prevention:**
1. **Classify documents before parsing:** Detect if PDF contains embedded text layers or is image-only
2. **Multi-strategy pipeline:**
   - Native PDFs → Direct text extraction (pypdf, pdfplumber)
   - Scanned PDFs → OCR (Tesseract, marker, or vision-language models)
   - Mixed PDFs → Page-by-page detection and routing
3. **Quality gates:** Check extraction completeness; flag documents with <50% expected content density
4. **Preserve structure:** Use tools that maintain table/section boundaries (marker, nougat, or specialized layout parsers)

**Detection (warning signs):**
- Search returns no results for documents that should contain keywords
- Average extracted text length is unexpectedly low
- Entity extraction confidence scores are abnormally low on certain document batches

**Phase to address:** Document Ingestion (Phase 1)

---

### Pitfall 2: Entity Extraction Without Disambiguation

**What goes wrong:** The system extracts "John Smith" as a person entity but cannot distinguish between:
- John Smith the attorney
- John Smith the witness  
- John Smith mentioned in passing as a reference

This leads to conflated entity profiles and incorrect relationship mapping.

**Why it happens:** 
- Standard NER libraries extract entities but don't resolve coreference or disambiguate
- Teams focus on extraction accuracy (F1 scores) without evaluating entity resolution quality
- Context is lost when documents are processed in isolation

**Consequences:**
- User searches for "John Smith" get results about 5 different people
- Relationship graphs show false connections (e.g., "John Smith was at Epstein's island" when it was a different John Smith)
- Investigative conclusions are factually wrong, destroying credibility

**Prevention:**
1. **Contextual entity extraction:** Include surrounding text (±2 sentences) in entity records
2. **Entity resolution pipeline:** Use contextual clues (co-occurring entities, document metadata, dates) to cluster mentions
3. **Manual review workflow:** Flag ambiguous entities for human verification before publishing
4. **Confidence thresholds:** Don't auto-link entities below 0.85 confidence; require confirmation
5. **Canonicalization:** Create entity profiles with unique IDs; link mentions to profiles, not raw names

**Detection (warning signs):**
- Entity "John Smith" appears in 200+ documents spanning unrelated events/time periods
- Relationship queries return nonsensical results (same person in multiple locations simultaneously)
- User complaints about "wrong person" in search results

**Phase to address:** Entity Processing (Phase 2-3)

---

### Pitfall 3: AI Answers Without Verifiable Citations

**What goes wrong:** The RAG system generates answers like "According to the flight logs, John Smith visited the island 5 times" but:
- Cannot point to specific source documents
- Cites documents that don't actually support the claim
- Mixes information from multiple documents incorrectly

**Why it happens:**
- Teams prioritize answer fluency over accuracy
- RAG retrieves chunks but doesn't enforce citation verification
- LLMs hallucinate citations or "round up" from partial evidence

**Consequences:**
- **Catastrophic for journalism/legal research:** Wrong citations destroy credibility and may have legal implications
- Users cannot verify claims, making the tool useless for serious research
- Misinformation spreads if AI answers are quoted without verification

**Prevention:**
1. **Mandatory citation grounding:** Every factual claim must map to a specific document location (page, paragraph, line)
2. **Citation verification layer:** Post-process LLM output to verify each citation exists and actually supports the claim
3. **Chunk metadata preservation:** Store document ID, page number, and exact text in vector DB alongside embeddings
4. **Source-first answers:** Structure prompts to require citations before synthesis: "First, list relevant quotes. Then, synthesize answer."
5. **Confidence scoring:** Flag answers with low citation coverage or conflicting sources

**Detection (warning signs):**
- Citation links return 404 or point to wrong documents
- Users report "I can't find that in the source document"
- Answers sound plausible but contain fabricated details

**Phase to address:** AI Q&A (Phase 4-5)

---

### Pitfall 4: Ignoring Redaction Patterns

**What goes wrong:** The system treats redacted black boxes as "no content" or tries to OCR through them, leading to:
- False positive entities from redaction artifacts
- Missing context where redactions break sentence continuity
- Security issues if redaction layers are improperly removed

**Why it happens:**
- Standard OCR/text extraction doesn't distinguish redacted regions
- PDF redaction is often done incorrectly (black boxes over text rather than text removal)
- Teams don't analyze document structure to detect redaction patterns

**Consequences:**
- Extracted text includes "■ ■ ■" or black box artifacts as words
- Missing critical context: "[REDACTED] was present at the meeting" loses who was present
- Accidental exposure of redacted content if PDF structure is misread

**Prevention:**
1. **Redaction detection:** Use visual analysis (CV) or PDF structure parsing to identify redacted regions
2. **Redaction metadata:** Store redaction locations and types in database alongside extracted text
3. **Text gap handling:** Mark redactions explicitly in extracted text (e.g., `[REDACTED: 3 words]`) rather than removing
4. **Context preservation:** Maintain sentence fragments on either side of redactions for NLP processing
5. **Security audit:** Verify extraction process doesn't accidentally expose redacted text layers

**Detection (warning signs):**
- Entities extracted like "███████" (literal box characters)
- Sentences that don't make sense due to missing redacted content
- Redacted content appearing in search results (security breach)

**Phase to address:** Document Ingestion (Phase 1)

---

### Pitfall 5: Poor Text Chunking Breaking Context

**What goes wrong:** Documents are split into chunks arbitrarily (e.g., every 500 tokens), causing:
- Key context lost at chunk boundaries (entity definitions split across chunks)
- Retrieval misses relevant information because it's in adjacent chunks
- LLM answers lack full context from split paragraphs

**Why it happens:**
- Teams use naive chunking (fixed size) without considering document structure
- No overlap between chunks to preserve boundary context
- Semantic breaks (paragraphs, sections) ignored in favor of token counts

**Consequences:**
- RAG retrieves chunks that lack defining context (e.g., "He said..." without identifying who "he" is)
- Important details missed because they're in "context" not retrieved
- Answer quality degrades significantly on documents with complex narratives

**Prevention:**
1. **Semantic chunking:** Split at natural boundaries (paragraphs, sections) rather than fixed token counts
2. **Hierarchical chunking:** Maintain parent-child relationships (document → section → paragraph → sentence)
3. **Contextual chunking:** Include document metadata and surrounding context in each chunk's metadata
4. **Smart overlap:** Use 10-20% overlap between chunks to preserve boundary context
5. **Late chunking:** Use long-context embedding models (128k+ tokens) to embed full context then extract relevant chunks

**Detection (warning signs):**
- Chunks starting with pronouns ("He", "It", "This") without antecedents
- Retrieved chunks lack entity definitions found in adjacent text
- User queries requiring cross-boundary context fail

**Phase to address:** Document Processing (Phase 2)

---

## Moderate Pitfalls

Mistakes that cause delays, technical debt, or require rework but don't destroy the project.

### Pitfall 6: Not Handling Handwritten Notes

**What goes wrong:** Government documents often contain handwritten marginalia, stamps, and signatures that automated systems miss or misread.

**Prevention:**
1. **Handwriting detection:** Use layout analysis to identify handwritten regions
2. **Specialized OCR:** Apply handwriting recognition models (e.g., TrOCR) to handwritten sections
3. **Metadata tagging:** Mark handwritten content separately from typed text
4. **Confidence scoring:** Flag handwritten text for manual review if OCR confidence is low

**Phase to address:** Document Ingestion (Phase 1)

---

### Pitfall 7: Database Schema Not Designed for Document Relationships

**What goes wrong:** Flat document storage (one row per document) without:
- Relationships between documents (references, attachments, duplicates)
- Versioning (document updates/replacements)
- Document sets (batch releases, case files)

**Prevention:**
1. **Graph-relational schema:** Use tables for documents, entities, and relationships
2. **Document relationships:** Track references, duplicates, and logical groupings
3. **Provenance tracking:** Store source URL, download date, and processing pipeline version
4. **Extensible metadata:** JSONB or similar for document-specific attributes

**Phase to address:** Database Design (Phase 1-2)

---

### Pitfall 8: No Pipeline Observability

**What goes wrong:** Document processing runs as black box; when errors occur, no visibility into:
- Which documents failed and why
- Processing stage bottlenecks
- Data quality metrics over time

**Prevention:**
1. **Stage tracking:** Log every document's progress through pipeline stages
2. **Error classification:** Categorize failures (OCR fail, parse error, timeout, etc.)
3. **Metrics dashboard:** Track documents processed, success rates, error trends
4. **Retry logic:** Automatic retry with backoff for transient failures

**Phase to address:** Infrastructure (Phase 1)

---

### Pitfall 9: Inadequate Testing on Document Diversity

**What goes wrong:** Testing on clean, well-formatted samples; production encounters:
- Poor quality scans
- Mixed orientations
- Corrupted or partial PDFs
- Non-standard character encodings

**Prevention:**
1. **Diverse test set:** Include worst-case documents (poor scans, complex layouts) in test suite
2. **Golden dataset:** Manually verified extractions for regression testing
3. **Cross-validation:** Test NER and extraction on held-out document types
4. **Fuzzing:** Test with intentionally corrupted inputs to verify error handling

**Phase to address:** Testing/QA (All phases)

---

### Pitfall 10: Premature Optimization for Scale

**What goes wrong:** Over-engineering for "millions of documents" when current dataset is hundreds or thousands:
- Complex distributed systems for simple workloads
- Premature use of vector DBs when SQL full-text search would suffice
- Over-complicated ETL pipelines

**Prevention:**
1. **MVP first:** Build for current dataset size (Epstein files are ~10k documents, not millions)
2. **SQLite for MVP:** Use SQLite for first iteration; migrate to PostgreSQL only when needed
3. **Simple vector search:** Start with FAISS or Chroma locally before cloud vector DBs
4. **Measure before optimizing:** Establish actual performance bottlenecks

**Phase to address:** Architecture (Phase 1)

---

## Minor Pitfalls

Mistakes that cause annoyance but are easily fixable.

### Pitfall 11: Not Normalizing Entity Names

Entities extracted as "John Smith", "Smith, John", and "J. Smith" don't match in search.

**Prevention:** Normalize names during extraction (title case, remove extra spaces, expand initials where confident).

**Phase:** Entity Processing (Phase 2)

---

### Pitfall 12: No Full-Text Backup for Vector Search

Relying solely on vector search for document discovery; semantic search misses exact phrase matches.

**Prevention:** Maintain parallel full-text index (SQLite FTS5 or Elasticsearch) for exact/prefix matching.

**Phase:** Search Implementation (Phase 3)

---

### Pitfall 13: Missing Document Metadata

Not preserving document properties like:
- Original filename
- Release batch/date
- Document type (email, transcript, form)
- Page count

**Prevention:** Extract and store all available metadata at ingestion time.

**Phase:** Document Ingestion (Phase 1)

---

## Phase-Specific Warnings

| Phase | Likely Pitfall | Mitigation |
|-------|----------------|------------|
| **Phase 1: Document Download** | Rate limiting, incomplete downloads | Implement resume/retry, verify checksums |
| **Phase 1: PDF Parsing** | Silent OCR failures | Quality gates, manual review sampling |
| **Phase 2: Entity Extraction** | False positives on common names | Confidence thresholds, disambiguation |
| **Phase 2: Database Design** | Schema too rigid for document variety | Use JSONB for flexible metadata |
| **Phase 3: Search** | Poor relevance ranking | Hybrid search (vector + keyword + recency) |
| **Phase 4: AI Q&A** | Hallucinated answers | Mandatory citation verification |
| **Phase 5: UI/UX** | Overwhelming document volume | Faceted search, document sets, bookmarks |
| **All Phases** | No data quality monitoring | Automated quality metrics, alerting |

---

## Domain-Specific Concerns for Epstein Files

### Redaction Heavy
Government releases are heavily redacted. Special attention needed for:
- Detecting redaction boxes vs text
- Preserving sentence context around redactions
- Not attempting to "fill in" redacted content with AI

### Legal Document Structure
Documents include:
- Depositions (Q&A format)
- Flight logs (tabular data)
- Emails (headers + threads)
- Correspondence (formal letters)

Each type needs specialized parsing to preserve structure.

### High Stakes Accuracy
Users are journalists and researchers. A false claim about person X visiting location Y can damage reputations. System must:
- Err on side of uncertainty ("source unclear" > confident wrong answer)
- Provide confidence scores on all AI-generated content
- Enable easy verification of every claim

### Source Authority
Only justice.gov is authoritative. System should:
- Track document provenance rigorously
- Flag if documents came from unofficial sources
- Verify document integrity (checksums, signatures)

---

## Confidence Assessment

| Pitfall Category | Confidence | Reason |
|-----------------|------------|--------|
| PDF Parsing | **HIGH** | Well-documented challenges with OCR and mixed PDFs (Context7: OCRmyPDF docs, multiple research papers) |
| Entity Disambiguation | **HIGH** | Academic research confirms this is an active, unsolved problem (ACL 2024 papers on AmbigDocs, name disambiguation) |
| AI Hallucinations/Citations | **HIGH** | Stanford study on legal RAG hallucinations (May 2024), extensive documented failures |
| Redaction Handling | **MEDIUM** | Known issue but fewer documented solutions; PDF Association paper on Epstein PDFs specifically |
| Chunking Strategies | **HIGH** | Multiple 2024 papers on chunking optimization (Chroma research, late chunking) |
| Handwritten Text | **MEDIUM** | Known challenge, solutions exist but add complexity |

---

## Sources

1. **PDF Parsing & OCR:**
   - OCRmyPDF documentation (https://ocrmypdf.readthedocs.io)
   - "Demystifying PDF Parsing" (AI Exploration Journey, May 2024)
   - "Analysis and Benchmarking of OCR Accuracy" (Docsumo, 2025)
   - "olmOCR: Unlocking Trillions of Tokens in PDFs" (Allen Institute, Feb 2025)

2. **Entity Extraction & Disambiguation:**
   - "The Effects of Data Quality on Named Entity Recognition" (ACL W-NUT 2024)
   - "AmbigDocs: Reasoning across Documents on Different Entities under the Same Name" (arXiv 2024)
   - "NOISEBENCH: Benchmarking the Impact of Real Label Noise on NER" (EMNLP 2024)

3. **AI Hallucinations & Legal RAG:**
   - "Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools" (Stanford, May 2024)
   - "This Reference Does Not Exist: An Exploration of LLM Citation Accuracy" (ACL 2024)
   - "Seven Failure Points When Engineering a Retrieval Augmented Generation System" (arXiv Jan 2024)
   - "How faithful are RAG models? Quantifying the tug-of-war between RAG and LLMs' internal prior" (arXiv 2024)

4. **Redaction:**
   - "Deep Research on PDF Redaction Failures and Security" (Argelius Labs, Oct 2024)
   - "Story Beyond the Eye: Glyph Positions Break PDF Text Redaction" (arXiv 2022)
   - "A case study in PDF forensics: The Epstein PDFs" (PDF Association)
   - "Redacted Documents Are Not as Secure as You Think" (WIRED, Nov 2022)

5. **Chunking & RAG:**
   - "Evaluating Chunking Strategies for Retrieval" (Chroma Research, July 2024)
   - "Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models" (Jina AI, 2024)
   - "Rethinking Chunk Size for Long-Document Retrieval" (Fraunhofer IAIS, 2024)
   - "RAG chunking: Fetch surrounding chunks to refine LLM responses" (Elasticsearch, June 2024)

6. **Scaling & Performance:**
   - "Optimizing ColPali for Retrieval at Scale" (Qdrant, Nov 2024)
   - "DocETL: Agentic Query Rewriting and Evaluation for Complex Document Processing" (arXiv Oct 2024)
   - "Towards Principled, Practical Document Database Design" (VLDB 2025)
