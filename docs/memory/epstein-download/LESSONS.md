# Memory: Epstein PDF Download Task

**Date:** 2026-02-03
**Task:** Download all 375 Epstein PDFs from DOJ releases

## What Worked

### 1. Agent Architecture
- Created `epstein-downloader` agent in `~/.config/opencode/agents/epstein-downloader.md`
- Agent pattern was effective for long-running tasks with timeout limits
- Resume capability built into `scripts/download_all.py` was crucial

### 2. Download Script (`scripts/download_all.py`)
- **Resume capability:** Checks file size > 1000 bytes to skip existing downloads
- **Progress reporting:** Shows status every 25 files
- **Age verification bypass:** Uses Playwright to handle justice.gov age gates
- **Success rate:** 100% (375/375 PDFs, 0 failures)
- **Total time:** ~45 minutes total across multiple sessions

### 3. Tool Efficiency
- **jq for JSON processing:** Reduced context usage significantly
  - Used for: counting PDFs, analyzing manifest, comparing lists
  - Command: `cat manifest.json | jq '.pdfs | length'`
  - Saved multiple Read tool calls
- **Bash integration:** Used `comm`, `wc`, `ls` with jq for file comparisons

### 4. Session Management
- Multiple 5-minute sessions were necessary due to tool timeout limits
- Script automatically resumed from where it left off
- Progress tracked across sessions: 67 → 94 → 247 → 251 → 328 → 375

## What Didn't Work

### 1. Single-Session Approach
- Attempted to download all 375 PDFs in one session
- Hit timeout limits consistently (30-60 min download time > 2-5 min timeout)
- **Lesson:** Break long-running tasks into multiple agent sessions

### 2. Manual Progress Checking
- Initially tried using Python to parse JSON
- Added unnecessary context load
- **Solution:** Used jq for JSON processing

### 3. No Chunking by Data Set
- Script downloads sequentially through entire manifest
- Could have been faster downloading smaller chunks
- **Future improvement:** Add `--dataset` flag for targeted downloads

## Key Insights

1. **Resume capability is essential** for long-running downloads with timeout limits
2. **jq > Python** for JSON analysis in this context (reduces token usage)
3. **Progress visibility** every 25 files provided good feedback
4. **Playwright handle** justice.gov age verification reliably
5. **Error recovery** built into script (try/catch, continue on failure)

## Tools Created

1. **`scripts/download_all.py`** - Main download script with resume
2. **`scripts/epstein_download_status.py`** - Status checker and launcher
3. **`~/.config/opencode/agents/epstein-downloader.md`** - Agent for download task
4. **Updated `AGENTS.md`** - Added Prime Directive and jq reference

## Next Steps

1. **Phase 1 Foundation:**
   - [ ] Set up SQLite database for document storage
   - [ ] Create PDF parsing pipeline (PyMuPDF or pdfplumber)
   - [ ] Build basic web interface

2. **Refactoring ideas:**
   - Add `--dataset` flag to download specific data sets
   - Add parallel downloads (with rate limiting)
   - Create verification script to check for corrupted PDFs

## Metrics

| Metric | Value |
|---------|--------|
| Total PDFs | 375 |
| Success Rate | 100% |
| Total Size | 756.63 MB |
| Download Time | ~45 minutes |
| Sessions Required | 5 (due to timeouts) |
| Tools Created | 4 (script, status, agent, docs) |

## Files Modified/Created

- `scripts/download_all.py` - Main download script
- `scripts/epstein_download_status.py` - Status monitoring
- `backlog.md` - Updated with progress
- `AGENTS.md` - Added Prime Directive and jq reference
- `~/.config/opencode/agents/epstein-downloader.md` - New agent
- `docs/memory/epstein-download/LESSONS.md` - This file

## Commands Reference

```bash
# Check download status
python3 scripts/epstein_download_status.py

# Download all PDFs (resumes automatically)
python3 scripts/download_all.py

# Count PDFs with jq
ls *.pdf | wc -l

# Analyze manifest with jq
cat reference/epstein_manifest.json | jq '.pdfs | length'

# Count remaining PDFs
ls reference/epstein_files/*.pdf | xargs -I{} basename {} | sort > /tmp/downloaded.txt
cat reference/epstein_manifest.json | jq -r '.pdfs[].url | split("/") | .[-1] | gsub("%20"; "_")' | sort > /tmp/all.txt
comm -23 /tmp/all.txt /tmp/downloaded.txt | wc -l
```
