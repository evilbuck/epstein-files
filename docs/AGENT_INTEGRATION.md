# Agent Integration Guide

How to integrate the Epstein file discovery tools into various AI agent frameworks.

## Overview

The scripts can be integrated as:
1. **Tools** (CLI commands agents can call)
2. **Agents** (full autonomous capabilities with decision loops)
3. **Hybrid** (agent orchestrates, tools do the work)

---

## Option 1: OpenCode Agent Integration

### Create Agent Definition

Create file: `~/.config/opencode/agents/epstein-discovery.md`

```markdown
# Epstein File Discovery Agent

Discover and download Epstein-related documents from justice.gov

## Usage

/epstein-discover [URL]

## Examples

/epstein-discover
/epstein-discover https://www.justice.gov/usao-sdny

## Description

Uses browser automation and intelligent crawling to find and download 
Epstein-related PDFs from the DOJ website. Handles Akamai protection 
automatically via Playwright.

## Workflow

1. Starts spider from given URL (or default SDNY page)
2. Crawls and extracts links using CLI tools
3. Reviews discovered pages for Epstein-related content
4. Downloads PDFs using browser automation
5. Organizes files into data/epstein_pdfs/

## Files Modified

- Downloads to: reference/
- Organizes to: data/epstein_pdfs/
- Logs: reference/spider_state.json
```

### Shell Integration Script

Create: `~/.config/opencode/tools/epstein-spider.sh`

```bash
#!/bin/bash
# Epstein spider wrapper for opencode

URL=${1:-"https://www.justice.gov/usao-sdny"}
cd /Users/buckleyrobinson/projects/epstein-files

python3 scripts/spider_agent.py "$URL"
```

### Slash Command Mapping

Add to `~/.config/opencode/config.json`:

```json
{
  "commands": {
    "epstein-discover": {
      "script": "~/.config/opencode/tools/epstein-spider.sh",
      "description": "Discover Epstein files from justice.gov"
    },
    "epstein-download": {
      "script": "cd /Users/buckleyrobinson/projects/epstein-files && python3 scripts/download_orchestrator.py",
      "description": "Download discovered Epstein PDFs"
    }
  }
}
```

---

## Option 2: Claude Code (Claude Desktop) Integration

### MCP (Model Context Protocol) Server

Create: `epstein-mcp-server.py`

```python
#!/usr/bin/env python3
"""MCP server for Epstein file discovery."""

from mcp.server import Server
from mcp.types import TextContent
import subprocess
import json

app = Server("epstein-discovery")

@app.call_tool()
async def epstein_tools(name: str, arguments: dict):
    """MCP tool handlers."""
    
    if name == "spider_discover":
        url = arguments.get("url", "https://www.justice.gov/usao-sdny")
        result = subprocess.run(
            ["python3", "scripts/spider_agent.py", url],
            capture_output=True,
            text=True,
            cwd="/Users/buckleyrobinson/projects/epstein-files"
        )
        return [TextContent(type="text", text=result.stdout + result.stderr)]
    
    elif name == "download_pdfs":
        result = subprocess.run(
            ["python3", "scripts/download_orchestrator.py"],
            capture_output=True,
            text=True,
            cwd="/Users/buckleyrobinson/projects/epstein-files"
        )
        return [TextContent(type="text", text=result.stdout + result.stderr)]
    
    elif name == "process_files":
        result = subprocess.run(
            ["bash", "scripts/process.sh"],
            capture_output=True,
            text=True,
            cwd="/Users/buckleyrobinson/projects/epstein-files"
        )
        return [TextContent(type="text", text=result.stdout + result.stderr)]
    
    elif name == "get_status":
        try:
            with open("reference/spider_state.json") as f:
                state = json.load(f)
            return [TextContent(type="text", text=json.dumps(state, indent=2))]
        except FileNotFoundError:
            return [TextContent(type="text", text="No state file found. Run spider_discover first.")]

if __name__ == "__main__":
    app.run()
```

### Claude Desktop Config

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "epstein-discovery": {
      "command": "python3",
      "args": ["/Users/buckleyrobinson/projects/epstein-files/epstein-mcp-server.py"]
    }
  }
}
```

### Usage in Claude

Once configured, you can ask Claude:
- "Discover Epstein files from justice.gov"
- "Download the PDFs we found"
- "Process and organize the downloaded files"
- "What's our discovery status?"

---

## Option 3: Simple Bash Tool Integration

### For Any Agent System

Create wrapper scripts that any agent can call:

**`tools/epstein-spider`:**
```bash
#!/bin/bash
# Universal spider tool

URL=${1:-"https://www.justice.gov/usao-sdny"}
PROJECT_DIR="/Users/buckleyrobinson/projects/epstein-files"

cd "$PROJECT_DIR" || exit 1
python3 scripts/spider_agent.py "$URL" 2>&1
```

**`tools/epstein-download`:**
```bash
#!/bin/bash
# Universal download tool

PROJECT_DIR="/Users/buckleyrobinson/projects/epstein-files"
cd "$PROJECT_DIR" || exit 1
python3 scripts/download_orchestrator.py 2>&1
```

**`tools/epstein-process`:**
```bash
#!/bin/bash
# Universal process tool

PROJECT_DIR="/Users/buckleyrobinson/projects/epstein-files"
cd "$PROJECT_DIR" || exit 1
bash scripts/process.sh 2>&1
```

### Agent Instructions

Add to your agent's system prompt:

```
You have access to Epstein file discovery tools:

1. epstein-spider [URL] - Crawls justice.gov to find Epstein PDFs
2. epstein-download - Downloads discovered PDFs using browser automation  
3. epstein-process - Organizes downloaded files into categories

Workflow:
1. Run epstein-spider to discover PDFs
2. Review discovered files
3. Run epstein-download to fetch them
4. Run epstein-process to organize

Files are stored in:
- reference/ - Raw downloads
- data/epstein_pdfs/ - Organized PDFs
```

---

## Option 4: GitHub Actions / CI Integration

### Automated Discovery Workflow

Create: `.github/workflows/epstein-discovery.yml`

```yaml
name: Epstein File Discovery

on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  discover:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Playwright
        run: |
          pip install playwright
          playwright install chromium
      
      - name: Install CLI tools
        run: |
          curl -L https://github.com/mgdm/htmlq/releases/latest/download/htmlq-x86_64-linux.tar.gz | tar xz -C /usr/local/bin
      
      - name: Run Discovery
        run: python3 scripts/discovery_agent.py
      
      - name: Upload State
        uses: actions/upload-artifact@v3
        with:
          name: discovery-state
          path: reference/discovery_state.json
```

---

## Option 5: Custom Agent (Most Flexible)

### Create an Agent Orchestrator

Create: `scripts/agent_orchestrator.py`

```python
#!/usr/bin/env python3
"""
Agent Orchestrator for Epstein File Discovery

Can be used by any AI agent framework. Provides structured interface
for discovery, download, and processing.
"""

import subprocess
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class Task:
    name: str
    command: List[str]
    status: TaskStatus
    output: Optional[str] = None
    error: Optional[str] = None

class EpsteinAgent:
    """Agent interface for Epstein discovery workflow."""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = project_dir
        self.tasks: List[Task] = []
    
    def discover(self, url: str = "https://www.justice.gov/usao-sdny") -> Task:
        """Run discovery spider."""
        task = Task(
            name="discover",
            command=["python3", "scripts/spider_agent.py", url],
            status=TaskStatus.PENDING
        )
        return self._run_task(task)
    
    def download(self) -> Task:
        """Download discovered PDFs."""
        task = Task(
            name="download",
            command=["python3", "scripts/download_orchestrator.py"],
            status=TaskStatus.PENDING
        )
        return self._run_task(task)
    
    def process(self) -> Task:
        """Process and organize files."""
        task = Task(
            name="process",
            command=["bash", "scripts/process.sh"],
            status=TaskStatus.PENDING
        )
        return self._run_task(task)
    
    def _run_task(self, task: Task) -> Task:
        """Execute a task."""
        task.status = TaskStatus.RUNNING
        
        result = subprocess.run(
            task.command,
            capture_output=True,
            text=True,
            cwd=self.project_dir
        )
        
        task.output = result.stdout
        task.error = result.stderr if result.stderr else None
        task.status = TaskStatus.COMPLETE if result.returncode == 0 else TaskStatus.FAILED
        
        self.tasks.append(task)
        return task
    
    def get_state(self) -> Dict:
        """Get current discovery state."""
        state_path = os.path.join(self.project_dir, "reference/spider_state.json")
        try:
            with open(state_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {"status": "no_state"}
    
    def get_report(self) -> str:
        """Generate status report."""
        state = self.get_state()
        
        lines = []
        lines.append("=" * 60)
        lines.append("EPSTEIN DISCOVERY AGENT REPORT")
        lines.append("=" * 60)
        
        if state.get("status") == "no_state":
            lines.append("\n⚠️  No discovery state found.")
            lines.append("   Run discover() first.")
        else:
            lines.append(f"\n📄 PDFs Found: {len(state.get('pdfs', []))}")
            lines.append(f"🔗 Pages Crawled: {len(state.get('visited', []))}")
            lines.append(f"🕷️  Max Depth: {state.get('max_depth', 'N/A')}")
            
            if state.get('pdfs'):
                lines.append("\nDiscovered PDFs:")
                for i, pdf in enumerate(state['pdfs'][:5], 1):
                    lines.append(f"  {i}. {pdf['url'][:70]}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

# CLI interface
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Epstein Discovery Agent")
    parser.add_argument("action", choices=["discover", "download", "process", "report"])
    parser.add_argument("--url", default="https://www.justice.gov/usao-sdny")
    parser.add_argument("--dir", default=".")
    
    args = parser.parse_args()
    
    agent = EpsteinAgent(args.dir)
    
    if args.action == "discover":
        task = agent.discover(args.url)
        print(task.output)
    elif args.action == "download":
        task = agent.download()
        print(task.output)
    elif args.action == "process":
        task = agent.process()
        print(task.output)
    elif args.action == "report":
        print(agent.get_report())
```

### Usage

```bash
# As CLI tool
python3 scripts/agent_orchestrator.py discover --url https://www.justice.gov/usao-sdny
python3 scripts/agent_orchestrator.py download
python3 scripts/agent_orchestrator.py report

# As Python module
from scripts.agent_orchestrator import EpsteinAgent

agent = EpsteinAgent()
agent.discover()
agent.download()
print(agent.get_report())
```

---

## Recommended Integration

For **opencode**: Use Option 1 (agent definitions + slash commands)
For **Claude Desktop**: Use Option 2 (MCP server)
For **Claude Code**: Use Option 3 (bash tools)
For **automation**: Use Option 5 (agent orchestrator)

---

## Quick Start

1. **Choose your platform** (opencode/Claude/other)
2. **Copy the integration code** from the relevant section
3. **Configure paths** to match your project location
4. **Test**: Run a discovery command
5. **Iterate**: Adjust based on results

---

## Troubleshooting

### Common Issues

**"python3: command not found"**
- Solution: Use full path to python3 in scripts

**"Playwright not installed"**  
- Solution: Add install step to agent initialization

**"Permission denied"**
- Solution: Make scripts executable: `chmod +x scripts/*.py`

**"State file not found"**
- Solution: Ensure reference/ directory exists and is writable

---

## Files Created

- `docs/AGENT_INTEGRATION.md` (this file)
- `scripts/agent_orchestrator.py` (universal agent interface)
- `epstein-mcp-server.py` (Claude Desktop MCP)

---

**Next Steps:**
1. Pick your platform
2. Copy the relevant config
3. Test with: `python3 scripts/agent_orchestrator.py report`
