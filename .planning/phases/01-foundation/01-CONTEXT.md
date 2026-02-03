# Phase 1: Foundation - Context

**Gathered:** 2025-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Document ingestion infrastructure with download pipeline, storage schema, PDF parsing, and basic web interface. Users can view downloaded Epstein documents with metadata, download original PDFs, and see text extraction results. Scope includes document processing status visibility but excludes search, entity extraction, and AI features (later phases).

</domain>

<decisions>
## Implementation Decisions

### Download Pipeline Behavior
- **Manual-triggered downloads**: Downloads initiated locally, not automated streaming from justice.gov
- **Batch download queue**: Queue all documents for sequential download with resume capability
- **Sequential processing**: One download at a time to be respectful to source server
- **Resume partial downloads**: Use HTTP range requests to continue interrupted downloads
- **Auto-retry with backoff**: Retry 3 times with exponential backoff, then mark as failed
- **Duplicate protection**: Prevent downloading same document twice unless force-override flag used

### Processing Status Visibility
- **Detailed pipeline states**: Show granular steps - downloaded / parsing / extracting text / ocr / indexed / completed / failed
- **Step-based progress**: Display current processing step name rather than just spinner
- **Error detail viewing**: Show detailed error messages for failed documents with retry option
- **Bulk process button**: Single "Process All" button to queue all unprocessed documents

### PDF Parsing Approach
- **Claude discretion on OCR threshold**: Researcher/planner to determine best practice for when to OCR vs use native text
- **Store all OCR results**: Keep extracted text regardless of confidence level, store confidence scores
- **Extract visible portions from redacted pages**: Get text from non-redacted areas, flag pages with high redaction coverage
- **Structured JSON output**: Page, paragraph, line-level structure with coordinates preserved

### Web Interface Layout
- **Card grid layout**: Visual cards showing document preview + key metadata (not table view)
- **Essential metadata only**: Display document ID, source URL, release date, processing status
- **Claude discretion on navigation**: Planner to choose between detail page, side panel, or modal pattern
- **Native browser PDF viewer**: Link opens browser's built-in PDF viewer rather than embedded viewer

### Document Metadata Structure
- **SHA-256 hash as primary identifier**: Content-based deduplication key
- **Claude discretion on source tracking**: Researcher/planner to determine appropriate provenance fields
- **Minimal processing metadata**: Store current status and basic timestamps, not full pipeline history
- **Claude discretion on content metadata**: Planner to determine what content stats are needed for Phase 1

### Claude's Discretion
- OCR triggering threshold and detection logic
- Progress indicator design and animation
- Navigation pattern between list and detail views
- Source tracking provenance fields
- Content metadata fields beyond basic stats
- Phase 1 database schema design
- PDF viewer integration approach

</decisions>

<specifics>
## Specific Ideas

- Downloads are manual/triggered locally, not automated streaming
- Duplicate download prevention with force-override capability
- Detailed processing pipeline visibility for transparency
- Native browser PDF viewing (simpler than embedded viewer)
- Content-based deduplication using SHA-256 hash
- Card-based document grid for visual browsing

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 1 scope. All decisions relate to document ingestion and basic viewing infrastructure.

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2025-02-03*
