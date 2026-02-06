#!/usr/bin/env python3
"""
Epstein PDF Download Status and Launcher

Usage:
    python3 scripts/epstein_download_status.py     # Show current status
    python3 scripts/epstein_download_status.py --download  # Start download
"""

import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
REFERENCE_DIR = PROJECT_DIR / "reference" / "epstein_files"
MANIFEST_FILE = PROJECT_DIR / "reference" / "epstein_manifest.json"

def get_download_status():
    """Get current download progress."""
    
    # Count downloaded files
    if REFERENCE_DIR.exists():
        downloaded = len(list(REFERENCE_DIR.glob("*.pdf")))
    else:
        downloaded = 0
    
    # Get total from manifest
    if MANIFEST_FILE.exists():
        with open(MANIFEST_FILE) as f:
            manifest = json.load(f)
            total = manifest.get("total_pdfs", 375)
    else:
        total = 375
    
    remaining = total - downloaded
    percentage = (downloaded / total * 100) if total > 0 else 0
    
    return {
        "downloaded": downloaded,
        "total": total,
        "remaining": remaining,
        "percentage": percentage
    }

def show_status():
    """Display current download status."""
    status = get_download_status()
    
    print("=" * 60)
    print("EPSTEIN PDF DOWNLOAD STATUS")
    print("=" * 60)
    print()
    print(f"📊 Progress: {status['downloaded']}/{status['total']} PDFs")
    print(f"📈 Complete: {status['percentage']:.1f}%")
    print(f"📥 Remaining: {status['remaining']} PDFs")
    print()
    print(f"📁 Downloaded files: {REFERENCE_DIR}")
    print(f"📝 Manifest: {MANIFEST_FILE}")
    print()
    
    if status['downloaded'] > 0:
        # Show recent files
        print("Recent downloads:")
        files = sorted(REFERENCE_DIR.glob("*.pdf"), key=os.path.getmtime, reverse=True)
        for f in files[:5]:
            size = f.stat().st_size
            print(f"  - {f.name} ({size:,} bytes)")
        print()
    
    if status['remaining'] > 0:
        print("To continue downloading, run:")
        print(f"  python3 {PROJECT_DIR}/scripts/download_all.py")
        print()
        print("Or spawn the Epstein downloader agent in opencode")
    else:
        print("✅ All PDFs downloaded!")
    
    print("=" * 60)
    return status

def start_download():
    """Launch the download process."""
    import subprocess
    
    status = get_download_status()
    
    if status['remaining'] == 0:
        print("✅ All PDFs already downloaded!")
        return 0
    
    print(f"🚀 Starting download of {status['remaining']} remaining PDFs...")
    print(f"   Already have: {status['downloaded']}/{status['total']}")
    print()
    
    # Run the download script
    download_script = PROJECT_DIR / "scripts" / "download_all.py"
    
    try:
        result = subprocess.run(
            ["python3", str(download_script)],
            cwd=str(PROJECT_DIR),
            check=False
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\n\n⚠️ Download interrupted by user.")
        print("Progress has been saved. Re-run to continue.")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--download":
        sys.exit(start_download())
    else:
        show_status()
