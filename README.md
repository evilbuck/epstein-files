# Epstein File Downloader & Organizer

An intelligent agent-based system for discovering and downloading Epstein-related documents from justice.gov.

## Overview

This project uses a **smart agent architecture** that separates:
- **Mechanical work** (CLI tools: curl, htmlq) - crawling and extraction
- **Cognitive work** (Human/AI review) - deciding which links to follow
- **Automation** (Playwright) - browser-based downloads

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  CLI Tools       │────→│  Human/AI Review │────→│  Playwright     │
│  (curl, htmlq)  │     │  Select links    │     │  Download PDFs  │
│                 │     │                  │     │                 │
│ • Extract links │     │ • Relevance      │     │ • Handle Akamai │
│ • Crawl pages   │     │ • Priority       │     │ • Fetch files   │
│ • Get content   │     │ • Depth          │     │ • Save to disk  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Quick Start

### Option 1: Agent Orchestrator (Recommended)

Run the complete workflow with a single command:

```bash
# Full workflow: discover → download → process
python3 scripts/agent_orchestrator.py workflow

# Or step-by-step:
python3 scripts/agent_orchestrator.py discover  # Find PDFs
python3 scripts/agent_orchestrator.py download  # Download them
python3 scripts/agent_orchestrator.py process   # Organize files

# Check status:
python3 scripts/agent_orchestrator.py report
```

### Option 2: Interactive Spider

For hands-on discovery with human review:

```bash
python3 scripts/spider_agent.py "https://www.justice.gov/usao-sdny"
```

The spider will:
1. Crawl the page using CLI tools
2. Show you discovered PDFs and links
3. Ask which links to follow next
4. Recurse until PDFs are found

### Option 3: Batch Discovery

Non-interactive discovery for automation:

```bash
python3 scripts/discovery_agent.py "https://www.justice.gov/usao-sdny"
python3 scripts/download_orchestrator.py  # Downloads discovered PDFs
bash scripts/process.sh                     # Organizes files
```

## Installation

### Prerequisites

```bash
# Install CLI tools
brew install htmlq

# Install Python dependencies
pip3 install playwright
python3 -m playwright install chromium

# Make scripts executable
chmod +x scripts/*.py scripts/*.sh
```

### Verification

```bash
# Test syntax
bash -n scripts/download.sh
python3 -m py_compile scripts/agent_orchestrator.py

# Test agent
python3 scripts/agent_orchestrator.py report
```

## File Structure

```
epstein-files/
├── scripts/
│   ├── agent_orchestrator.py      # Universal agent interface ⭐
│   ├── spider_agent.py            # Interactive crawler
│   ├── discovery_agent.py         # Batch discovery tool
│   ├── download_orchestrator.py   # PDF download manager
│   ├── download_playwright.py     # URL-based downloader
│   ├── download.sh                # Bash/curl downloader (legacy)
│   ├── process.sh                 # File organization
│   └── debug_*.sh                 # Debug utilities
├── reference/                     # Downloaded files (gitignored)
├── data/
│   ├── epstein_pdfs/             # Organized PDFs
│   ├── epstein_text/             # Text files
│   └── epstein_images/           # Images
└── docs/
    ├── EXECUTION_SUMMARY.md      # Project status
    └── AGENT_INTEGRATION.md      # AI agent integration guide
```

## Usage Examples

### As CLI Tool

```bash
# Discover from SDNY page
python3 scripts/agent_orchestrator.py discover --url https://www.justice.gov/usao-sdny

# Download all discovered PDFs
python3 scripts/agent_orchestrator.py download

# Organize files
python3 scripts/agent_orchestrator.py process

# Full workflow
python3 scripts/agent_orchestrator.py workflow
```

### As Python Module

```python
from scripts.agent_orchestrator import EpsteinAgent

# Create agent
agent = EpsteinAgent("/path/to/project")

# Run discovery
result = agent.discover("https://www.justice.gov/usao-sdny")
print(result.output)

# Check status
print(agent.get_report())

# Download and process
agent.download()
agent.process()
```

### As AI Agent Tool

The system is designed to be called by AI agents. See `docs/AGENT_INTEGRATION.md` for:

- OpenCode slash commands
- Claude Desktop MCP server
- Claude Code tool integration
- GitHub Actions automation
- Custom agent frameworks

## Agent Commands

| Command | Description | Model Calls? |
|---------|-------------|--------------|
| `discover` | Interactive spider crawler | Yes - link selection |
| `batch_discover` | Non-interactive discovery | No |
| `download` | Download discovered PDFs | No |
| `process` | Organize files | No |
| `report` | Show status | No |
| `workflow` | Full pipeline | Optional |

## Troubleshooting

### "Akamai JavaScript challenge detected"

**Solution:** The bash/curl scripts cannot bypass Akamai. Use the Playwright-based tools:

```bash
# Use this instead:
python3 scripts/agent_orchestrator.py workflow
```

### "No PDF links found"

**Solution:** The justice.gov/epstein URL may have changed. Try:

```bash
# Southern District NY (handled the case)
python3 scripts/agent_orchestrator.py discover --url https://www.justice.gov/usao-sdny

# Or search the main DOJ site
python3 scripts/spider_agent.py "https://www.justice.gov"
```

### "Playwright not installed"

```bash
pip3 install playwright
python3 -m playwright install chromium
```

### "htmlq: command not found"

```bash
brew install htmlq
# Or use regex fallback (scripts work without htmlq)
```

## Status

**Current State:** All syntax errors fixed, agent architecture complete

- ✅ All scripts pass syntax validation
- ✅ Agent orchestrator ready
- ✅ Spider agent with interactive mode
- ✅ Playwright integration for Akamai bypass
- ✅ File processing pipeline fixed

**Known Issues:**
- The justice.gov/epstein URL redirects to main DOJ homepage
- Use SDNY page (usao-sdny) or spider to find current location

## Documentation

- `docs/EXECUTION_SUMMARY.md` - Project status and completion notes
- `docs/AGENT_INTEGRATION.md` - Integration with AI agent frameworks
- `docs/in_progress.kilo.md` - Original work-in-progress summary

## License

This is a research tool for accessing public DOJ documents.

---

**Last Updated:** 2026-02-03
