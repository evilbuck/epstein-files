#!/usr/bin/env python3
"""
Agent Orchestrator for Epstein File Discovery

Universal interface that can be used by any AI agent framework.
Provides structured commands for discovery, download, and processing.
"""

import subprocess
import json
import os
import sys
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
    returncode: int = 0


class EpsteinAgent:
    """Agent interface for Epstein discovery workflow."""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = os.path.abspath(project_dir)
        self.tasks: List[Task] = []
        
        # Ensure reference directory exists
        os.makedirs(os.path.join(self.project_dir, "reference"), exist_ok=True)
    
    def _run_task(self, task: Task) -> Task:
        """Execute a task and capture output."""
        task.status = TaskStatus.RUNNING
        
        print(f"🔄 Running: {task.name}", file=sys.stderr)
        
        result = subprocess.run(
            task.command,
            capture_output=True,
            text=True,
            cwd=self.project_dir
        )
        
        task.output = result.stdout
        task.error = result.stderr if result.stderr else None
        task.returncode = result.returncode
        task.status = TaskStatus.COMPLETE if result.returncode == 0 else TaskStatus.FAILED
        
        self.tasks.append(task)
        
        status_icon = "✅" if task.status == TaskStatus.COMPLETE else "❌"
        print(f"{status_icon} {task.name}: {task.status.value}", file=sys.stderr)
        
        return task
    
    def discover(self, url: str = "https://www.justice.gov/usao-sdny") -> Task:
        """Run discovery spider to find Epstein PDFs."""
        task = Task(
            name="discover",
            command=[sys.executable, "scripts/spider_agent.py", url],
            status=TaskStatus.PENDING
        )
        return self._run_task(task)
    
    def batch_discover(self, url: str = "https://www.justice.gov/usao-sdny") -> Task:
        """Run batch discovery (non-interactive)."""
        task = Task(
            name="batch_discover",
            command=[sys.executable, "scripts/discovery_agent.py", url],
            status=TaskStatus.PENDING
        )
        return self._run_task(task)
    
    def download(self) -> Task:
        """Download discovered PDFs using Playwright."""
        task = Task(
            name="download",
            command=[sys.executable, "scripts/download_orchestrator.py"],
            status=TaskStatus.PENDING
        )
        return self._run_task(task)
    
    def process(self) -> Task:
        """Process and organize downloaded files."""
        task = Task(
            name="process",
            command=["bash", "scripts/process.sh"],
            status=TaskStatus.PENDING
        )
        return self._run_task(task)
    
    def get_state(self) -> Dict:
        """Get current discovery state from saved files."""
        state_files = [
            "reference/spider_state.json",
            "reference/discovery_state.json"
        ]
        
        for state_file in state_files:
            path = os.path.join(self.project_dir, state_file)
            try:
                with open(path) as f:
                    return json.load(f)
            except FileNotFoundError:
                continue
        
        return {"status": "no_state", "pdfs": [], "pages": [], "visited": []}
    
    def get_download_manifest(self) -> Dict:
        """Get download manifest if it exists."""
        manifest_path = os.path.join(self.project_dir, "reference/download_manifest.json")
        try:
            with open(manifest_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {"status": "no_manifest", "downloaded": [], "failed": []}
    
    def get_report(self) -> str:
        """Generate comprehensive status report."""
        lines = []
        lines.append("=" * 70)
        lines.append("EPSTEIN DISCOVERY AGENT REPORT")
        lines.append("=" * 70)
        lines.append(f"Project Directory: {self.project_dir}")
        lines.append("")
        
        # Discovery State
        state = self.get_state()
        
        if state.get("status") == "no_state":
            lines.append("⚠️  No discovery state found.")
            lines.append("   Run 'discover' or 'batch_discover' first.")
        else:
            pdfs = state.get("pdfs", [])
            visited = state.get("visited", [])
            
            lines.append(f"📄 PDFs Discovered: {len(pdfs)}")
            lines.append(f"🔗 Pages Crawled: {len(visited)}")
            lines.append(f"🕷️  Max Depth: {state.get('max_depth', 'N/A')}")
            
            if pdfs:
                lines.append("\n📋 Discovered PDFs:")
                for i, pdf in enumerate(pdfs[:10], 1):
                    text = pdf.get('text', '')[:50]
                    url = pdf['url'][:65]
                    lines.append(f"  {i}. {text or 'PDF'}")
                    lines.append(f"     → {url}...")
                if len(pdfs) > 10:
                    lines.append(f"  ... and {len(pdfs) - 10} more")
        
        # Download Status
        manifest = self.get_download_manifest()
        lines.append("")
        lines.append(f"📥 Download Status:")
        lines.append(f"  ✅ Successfully downloaded: {len(manifest.get('downloaded', []))}")
        lines.append(f"  ❌ Failed: {len(manifest.get('failed', []))}")
        
        # Task History
        if self.tasks:
            lines.append("")
            lines.append(f"🔄 Task History:")
            for task in self.tasks:
                icon = "✅" if task.status == TaskStatus.COMPLETE else "❌"
                lines.append(f"  {icon} {task.name}: {task.status.value}")
        
        # Next Steps
        lines.append("")
        lines.append("=" * 70)
        lines.append("NEXT STEPS")
        lines.append("=" * 70)
        
        if state.get("status") == "no_state":
            lines.append("1. Run: discover [URL]")
        elif not manifest.get("downloaded"):
            lines.append("1. Run: download")
            lines.append("2. Run: process")
        else:
            lines.append("1. Run: process (to organize files)")
            lines.append("2. Check: data/epstein_pdfs/")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def run_workflow(self, start_url: str = "https://www.justice.gov/usao-sdny") -> None:
        """Run complete discovery workflow."""
        print("🕷️  Starting Epstein File Discovery Workflow\n", file=sys.stderr)
        
        # Step 1: Discover
        discover_task = self.batch_discover(start_url)
        if discover_task.status == TaskStatus.FAILED:
            print("\n❌ Discovery failed. Check output above.", file=sys.stderr)
            return
        
        print(discover_task.output)
        
        # Check if we found PDFs
        state = self.get_state()
        if not state.get("pdfs"):
            print("\n⚠️  No PDFs discovered. Try a different URL.", file=sys.stderr)
            return
        
        # Step 2: Download
        print("\n" + "=" * 70, file=sys.stderr)
        download_task = self.download()
        print(download_task.output)
        
        if download_task.status == TaskStatus.FAILED:
            print("\n❌ Download failed.", file=sys.stderr)
            return
        
        # Step 3: Process
        print("\n" + "=" * 70, file=sys.stderr)
        process_task = self.process()
        print(process_task.output)
        
        # Final Report
        print("\n" + "=" * 70, file=sys.stderr)
        print(self.get_report())


def main():
    """CLI interface for the agent orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Epstein File Discovery Agent Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full workflow
  %(prog)s workflow
  
  # Run individual steps
  %(prog)s discover --url https://www.justice.gov/usao-sdny
  %(prog)s download
  %(prog)s process
  
  # Get status report
  %(prog)s report
        """
    )
    
    parser.add_argument(
        "action",
        choices=["workflow", "discover", "batch_discover", "download", "process", "report"],
        help="Action to perform"
    )
    parser.add_argument(
        "--url",
        default="https://www.justice.gov/usao-sdny",
        help="Starting URL for discovery (default: SDNY page)"
    )
    parser.add_argument(
        "--dir",
        default=".",
        help="Project directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    agent = EpsteinAgent(args.dir)
    
    if args.action == "workflow":
        agent.run_workflow(args.url)
    
    elif args.action == "discover":
        task = agent.discover(args.url)
        print(task.output)
        if task.error:
            print("\nErrors:", task.error, file=sys.stderr)
    
    elif args.action == "batch_discover":
        task = agent.batch_discover(args.url)
        print(task.output)
        if task.error:
            print("\nErrors:", task.error, file=sys.stderr)
    
    elif args.action == "download":
        task = agent.download()
        print(task.output)
        if task.error:
            print("\nErrors:", task.error, file=sys.stderr)
    
    elif args.action == "process":
        task = agent.process()
        print(task.output)
        if task.error:
            print("\nErrors:", task.error, file=sys.stderr)
    
    elif args.action == "report":
        print(agent.get_report())
    
    # Exit with appropriate code
    if agent.tasks and agent.tasks[-1].status == TaskStatus.FAILED:
        sys.exit(1)


if __name__ == "__main__":
    main()
