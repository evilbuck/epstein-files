# Epstein Files - Agent Guide

AI-powered document cataloging system for DOJ Epstein file releases.

---

## Prime Directive

**Core Mission:** Transform the DOJ Epstein file releases into a searchable, query-able intelligence system that enables researchers to ask questions and receive accurate, sourced answers.

**Operating Principles:**

1. **Build Tools, Don't Brute Force** - When you find yourself running the same commands repeatedly, stop and build a tool. Use the model for strategy, tools for execution. Research the best CLI tools (htmlq, pup, jq) and build focused scripts.

2. **Verify Everything** - Don't trust automated work blindly. Always verify results. Check file counts, validate downloads, inspect outputs. If something failed, analyze why and fix it.

3. **Learn and Remember** - Keep a memory file (`docs/memory/:taskname/`). Record what worked, what didn't, and new insights. Review this before and after processing data.

4. **Iterate Until Solved** - Don't stop at the first error. Try different approaches. Build new tools if existing ones don't work. Document errors and solutions in memory files.

5. **Self-Improvement** - Before manually processing data, ask: "Am I brute forcing this? Would a script or agent help?" Create your own tools and agents when patterns emerge.

6. **Ship Working Software** - Prefer working pipelines over perfect extraction. Iterate quickly. Refactor later. Small iterations beat large features.

---

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
- https://www.justice.gov/epstein/doj-disclosures

**Non-downloadable datasets** (require browser scraping):
- Data Set 8, 9, 10, 11

## Tool Building Principles

### Build Tools, Don't Parse in Context

When you need to extract or process data repeatedly, **build a tool** instead of feeding content into the model:

- **Research first**: Find the best CLI tools for the job (htmlq, pup, jq, ripgrep, etc.)
- **Build MVP scrapers**: Create simple, focused scripts that output structured data
- **Don't parse webpages in context**: Use the model for strategy, tools for execution

### Existing Tools

@include @docs/AGENT_INTEGRATIONS.md

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

### JSON Processing Tools

**Quick reference for jq (JSON processor):**

- **Count items**: `cat file.json | jq '.items | length'`
- **Extract specific field**: `cat file.json | jq '.[].url'`
- **Filter by condition**: `cat file.json | jq '.[] | select(.status == "success")'`
- **Group and count**: `cat file.json | jq 'group_by(.field) | map({key: .[0].field, count: length})'`
- **Compare lists**: Use `comm` with bash: `jq -r '.[].name' file1.json | sort > /tmp/a.txt`

**Why use jq:**
- Reduces context usage - processes JSON without loading into model
- Fast and efficient for large JSON files
- Complex transformations possible with single commands
- Pairs well with bash pipes for multi-step operations

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
- [ ] Document the architecture. How to use and how to develop further.

**Before git committing**
- [ ] !`git diff`
- [ ] verify that secrets are not being leaked in the diff

## Directory Structure

- **docs/** project level. Architecture, decision making, PRD's
- **tmp/** artifacts from processing files. as the name suggests, temporary files. Scratchpad items

## Self-Improvement

Before and after manually processing. I want you to stop and take a moment to think about the data 
you're processing and how you're acquiring it. Are you brute forcing your way to it? Are you constantly 
running the same commands over and over. Would a script or a tool help you process the data more effectively?

Keep track of the types of tasks you run, especially when researching or fetching external data. Use a memory file in docs/memory.md. Review this file after writing to it or after manually running a task from scratch.
Consider if it could be scripted in a way that you can run it and get just the output you need.

For example, if you're fetching webpage data only to get the links. Build a scraper tool that outputs the link data. It's more efficient. Keeps your context lean.

You have the freedom to create your own tools. 

### Update your own memory 

@AGENTS.md (this file). Update this file with tools that you build or instructions that will help.

Create your own opencode and claudecode agents that will enable you to background process.

Update docs/AGENT_INTEGRATIONS.md with any new tools you find useful.

### Available Agents

**Epstein Downloader Agent** (`~/.config/opencode/agents/epstein-downloader.md`)
- Purpose: Download remaining Epstein PDFs with resume capability
- Usage: Spawn this agent when you need to continue downloads
- Status tracking: Automatically updates backlog.md with progress
- Location: `~/.config/opencode/agents/epstein-downloader.md`

### Agents Use

Use agents to do your bidding. Determine if the agent was successful. If it wasn't, consider a different approach. Reason about what else you could do. Should you build a new tool to help yourself solve the problem? Is there an existing tool you built? Don't stop until you solve the problem. Learn from the errors. Write them down. Use a file as memory in the `docs/memory/:taskname/` folder.
You always assess, then you verify the work. Don't trust it. You verify that it works. If it doesn't, think about the problem, the prior results, what you've tried, and how to approach it again.

