# Backlog

## Current Status: Phase 1 Foundation - Document Download ✅ COMPLETE

**Progress:** 375/375 PDFs downloaded (100% complete)
**Total Size:** 756.63 MB
**Success Rate:** 100% (0 failed downloads)
**Completed:** 2026-02-03

## Completed Tasks

- [x] Create download script for justice.gov/epstein
- [x] Create processing script for organizing files
- [x] Set up project structure (app/, scripts/, reference/, data/)
- [x] Create README.md with usage instructions
- [x] Create agent-based download system (spider, discovery, orchestrator agents)
- [x] Fix download script to properly extract PDF links (375 PDFs discovered!)
- [x] Download all 375 Epstein PDFs with 100% success rate
- [x] Create epstein-downloader agent for opencode
- [x] Create download status and monitoring scripts
- [x] Add jq reference and Prime Directive to AGENTS.md

## In Progress

- [ ] Set up SQLite database for document storage
- [ ] Create PDF parsing pipeline with OCR
- [ ] Build basic web interface
- [ ] Implement full-text search (Phase 2)

## Next Steps

- [ ] Complete PDF download (310 remaining)
- [ ] Set up SQLite database for document storage
- [ ] Create PDF parsing pipeline with OCR
- [ ] Build basic web interface
- [ ] Implement full-text search (Phase 2)

## Notes

- Zip files have double protection (age verification + 401 auth) - using individual PDFs
- Data Sets 8-11 require Playwright for browser automation
- Manifest stored at: `reference/epstein_manifest.json`
- Downloaded files: `reference/epstein_files/`
