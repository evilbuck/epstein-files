# Epstein Files - Agent Guide

AI-powered document cataloging system for DOJ Epstein file releases.

## Purpose

Build a searchable, query-able database of the Epstein files by:
- Downloading and organizing released documents
- Extracting entities (names, dates, locations, events)
- Creating relationships between facts
- Enabling AI-powered research queries

## Technology Stack

**Preferred (in order):**
- Python (data processing, NLP, AI integration)
- TypeScript/JavaScript (web interface, APIs)
- Bash (automation scripts)
- Go (performance-critical tools)

**Database:** SQLite for MVP, PostgreSQL for scale

### Core Dependencies (when added)
- Document parsing: `pypdf`, `pdfplumber`
- NLP/AI: `openai`, `anthropic`, `spacy`
- Web: FastAPI or Flask (Python), or Next.js (TS)

## Development Commands

**Since no framework is initialized yet, follow these conventions:**

### Python Projects
```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests (when added)
pytest                    # all tests
pytest tests/test_file.py::test_name  # single test
pytest -k "pattern"       # filter by name
pytest -x                 # stop on first failure

# Lint/Format
ruff check .              # linting
ruff format .             # formatting
mypy .                    # type checking (if configured)
```

### JavaScript/TypeScript Projects
```bash
# Setup
npm install

# Run tests
npm test                  # all tests
npm test -- --grep "test name"  # single test (Mocha/Jest)
jest tests/file.test.ts   # specific file

# Lint/Format
npm run lint
npm run format
npm run typecheck         # if configured
```

### Bash Scripts
```bash
# Always run shellcheck before committing
shellcheck scripts/*.sh

# Make executable
chmod +x scripts/*.sh
```

## Code Style Guidelines

### General Principles
- **Simple > Complex**: Prefer straightforward solutions
- **MVP > Perfect**: Iterate quickly, refactor later
- **Small iterations**: 10 small changes > 1 large feature

### Naming Conventions
- **Files**: `snake_case.py`, `kebab-case.ts`, `descriptive-names.sh`
- **Functions/Variables**: `snake_case` (Python/Bash), `camelCase` (JS/TS)
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`

### Imports (Python)
```python
# Standard library first
import os
import json
from pathlib import Path

# Third-party packages
import requests
from openai import OpenAI

# Local modules (absolute imports preferred)
from app.parser import DocumentParser
from config.settings import API_KEY
```

### Imports (TypeScript)
```typescript
// External packages
import { OpenAI } from 'openai';

// Internal modules (use path aliases if configured)
import { parseDocument } from '@/lib/parser';
import type { Document } from '@/types';
```

### Error Handling
```python
# Python - explicit, don't swallow exceptions
try:
    result = process_file(path)
except FileNotFoundError as e:
    logger.error(f"File not found: {path}")
    raise  # or return error context
except Exception as e:
    logger.exception("Unexpected error processing file")
    raise
```

```typescript
// TypeScript - use Result types or explicit error handling
const result = await safeProcessFile(path);
if (result.isErr()) {
    logger.error(`Failed to process: ${result.error.message}`);
    return result;
}
```

### Documentation
- Add docstrings to all public functions/classes
- Include: what it does, args, returns, raises (if applicable)
- Keep comments minimal - code should be self-documenting

## Project Structure

```
epstein-files/
├── app/                  # Main application code
│   ├── __init__.py
│   ├── parser/          # Document parsing modules
│   ├── nlp/             # NLP/AI processing
│   ├── db/              # Database models/queries
│   └── api/             # API endpoints (if applicable)
├── scripts/             # Utility scripts
│   ├── download.sh      # Document downloading
│   └── process.sh       # Batch processing
├── docs/                # Project documentation, PRDs
├── reference/           # Reference materials, research notes
├── tests/               # Test files (mirror app structure)
├── data/                # Downloaded files (gitignored)
├── .venv/              # Python virtual environment
└── AGENTS.md           # This file
```

## Document Processing Workflow

1. **Download**: Scripts in `scripts/` fetch from justice.gov/epstein
2. **Parse**: Extract text from PDFs
3. **Chunk**: Break into processable segments
4. **Extract**: Pull entities (names, dates, relationships)
5. **Store**: Save structured data to database
6. **Query**: Enable AI-powered research interface

## External Resources

**Primary Source:** https://www.justice.gov/epstein

**Non-downloadable datasets** (require browser scraping):
- Data Set 8, 9, 10, 11

## Tool Building Principles

### Build Tools, Don't Parse in Context

When you need to extract or process data repeatedly, **build a tool** instead of feeding content into the model:

- **Research first**: Find the best CLI tools for the job (htmlq, pup, jq, ripgrep, etc.)
- **Build MVP scrapers**: Create simple, focused scripts that output structured data
- **Don't parse webpages in context**: Use the model for strategy, tools for execution

### Web Scraping Workflow

```bash
# 1. Research the best tool for the site structure
#    - htmlq: CSS selectors on HTML (installed: mgdm/htmlq)
#    - pup: Interactive DOM exploration with CSS selectors
#    - jq: JSON processing when APIs are available

# 2. Build a minimal scraper script
#    - Store in scripts/scrape-<source>.sh
#    - Output to stdout or structured files (JSON/CSV)
#    - Handle pagination, retries, rate limiting

# 3. Example: Extract links from justice.gov
# curl -s https://www.justice.gov/epstein | htmlq -a href 'a' | grep -i pdf
```

### When to Build an Agent

If a task requires:
- Complex decision-making during scraping
- Multi-step workflows with state
- Handling dynamic/JavaScript-heavy sites

**Build an agent** instead of a script:
- For **opencode**: Create a reusable agent definition
- For **Claude Code**: Build an agent that can be invoked

Store agent definitions in `agents/` directory with clear naming.

### HTML Parsing Tools

**Quick reference for installed tools:**

- **htmlq**: CSS selectors on HTML. Use `-t` for text, `-a <attr>` for attributes
- **pup**: Interactive exploration. Use `text{}` for content, `json{}` for structured output
- **html2text**: Convert HTML to readable markdown (good for LLM input)

## Backlog

Always check `backlog.md` for current priorities before starting work.

## Agent Checklist

Before submitting changes:
- [ ] Code follows naming conventions
- [ ] Docstrings added for public APIs
- [ ] Error handling is explicit
- [ ] Tests pass (or are added for new functionality)
- [ ] Linting passes (ruff, eslint, shellcheck as appropriate)
- [ ] Backlog updated if needed
