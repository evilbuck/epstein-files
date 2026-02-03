#!/usr/bin/env python3
"""
Download ALL Epstein Data Set PDFs
Scans all 9 data sets and downloads every PDF file
"""

import asyncio
import json
import os
import subprocess
from playwright.async_api import async_playwright
from urllib.parse import urlparse


async def discover_all_datasets():
    """Discover PDFs from all 9 Data Sets."""
    all_pdfs = []
    
    print("🔍 Discovering PDFs from all Data Sets...\n")
    
    for i in range(1, 10):
        url = f"https://www.justice.gov/epstein/doj-disclosures/data-set-{i}-files"
        print(f"  Data Set {i}...", end=" ")
        
        # Use discovery agent
        result = subprocess.run(
            ["python3", "scripts/discovery_agent.py", url],
            capture_output=True,
            text=True,
            cwd="/Users/buckleyrobinson/projects/epstein-files"
        )
        
        # Load discovery state
        state_path = "reference/discovery_state.json"
        try:
            with open(state_path) as f:
                state = json.load(f)
            pdfs = state.get("pdfs", [])
            all_pdfs.extend(pdfs)
            print(f"✓ Found {len(pdfs)} PDFs")
        except:
            print("✗ Failed")
    
    print(f"\n📊 Total PDFs discovered: {len(all_pdfs)}")
    
    # Save combined manifest
    manifest = {
        "total_pdfs": len(all_pdfs),
        "datasets": list(range(1, 10)),
        "pdfs": all_pdfs
    }
    
    with open("reference/epstein_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print("💾 Manifest saved to reference/epstein_manifest.json")
    
    return all_pdfs


async def download_all_pdfs(pdf_list):
    """Download all discovered PDFs."""
    
    output_dir = "reference"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create subdirectory for Epstein files
    epstein_dir = os.path.join(output_dir, "epstein_files")
    os.makedirs(epstein_dir, exist_ok=True)
    
    downloaded = []
    failed = []
    
    print(f"\n📥 Starting download of {len(pdf_list)} PDFs...\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # Navigate to disclosures page first (for session/cookies)
        await page.goto("https://www.justice.gov/epstein/doj-disclosures",
                       wait_until="networkidle", timeout=60000)
        
        for i, pdf_info in enumerate(pdf_list, 1):
            url = pdf_info["url"]
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            
            # Create organized filename with dataset prefix
            dataset = "unknown"
            if "DataSet%20" in url or "DataSet " in url:
                for d in range(1, 10):
                    if f"DataSet%20{d}" in url or f"DataSet {d}" in url:
                        dataset = f"dataset_{d}"
                        break
            
            output_filename = f"{dataset}_{filename}"
            output_path = os.path.join(epstein_dir, output_filename)
            
            # Skip if already exists
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"  [{i}/{len(pdf_list)}] ⏭️  {output_filename} (exists)")
                downloaded.append({
                    "url": url,
                    "filename": output_filename,
                    "status": "already_exists",
                    "path": output_path
                })
                continue
            
            print(f"  [{i}/{len(pdf_list)}] ⬇️  {output_filename}")
            
            try:
                # Download using browser
                response = await page.evaluate('''async (url) => {
                    try {
                        const res = await fetch(url);
                        if (!res.ok) throw new Error(`HTTP ${res.status}`);
                        const blob = await res.blob();
                        return await new Promise((resolve) => {
                            const reader = new FileReader();
                            reader.onloadend = () => resolve(reader.result);
                            reader.readAsDataURL(blob);
                        });
                    } catch (e) {
                        return { error: e.message };
                    }
                }''', url)
                
                if isinstance(response, dict) and "error" in response:
                    raise Exception(response["error"])
                
                if response and isinstance(response, str) and "," in response:
                    import base64
                    base64_data = response.split(",")[1]
                    binary_data = base64.b64decode(base64_data)
                    
                    # Verify it's a PDF (starts with %PDF)
                    if binary_data[:4] == b"%PDF":
                        with open(output_path, "wb") as f:
                            f.write(binary_data)
                        
                        size = len(binary_data)
                        print(f"            ✓ {size:,} bytes")
                        
                        downloaded.append({
                            "url": url,
                            "filename": output_filename,
                            "status": "downloaded",
                            "size": size,
                            "path": output_path
                        })
                    else:
                        raise Exception("Not a valid PDF file")
                else:
                    raise Exception("Invalid response format")
                    
            except Exception as e:
                print(f"            ✗ Error: {e}")
                failed.append({
                    "url": url,
                    "filename": output_filename,
                    "error": str(e)
                })
            
            # Small delay to be respectful
            await asyncio.sleep(0.3)
        
        await browser.close()
    
    # Save download report
    report = {
        "total": len(pdf_list),
        "downloaded": len(downloaded),
        "failed": len(failed),
        "files": downloaded,
        "errors": failed
    }
    
    with open("reference/download_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*70}")
    print("DOWNLOAD COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Successfully downloaded: {len(downloaded)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📁 Files saved to: {epstein_dir}/")
    print(f"📊 Report saved to: reference/download_report.json")
    
    if downloaded:
        total_size = sum(f.get("size", 0) for f in downloaded if "size" in f)
        print(f"📦 Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    
    return downloaded


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download all Epstein PDFs")
    parser.add_argument("--skip-discovery", action="store_true",
                       help="Skip discovery and use existing manifest")
    
    args = parser.parse_args()
    
    if args.skip_discovery:
        # Load existing manifest
        try:
            with open("reference/epstein_manifest.json") as f:
                manifest = json.load(f)
            pdfs = manifest.get("pdfs", [])
            print(f"📋 Loaded {len(pdfs)} PDFs from existing manifest")
        except FileNotFoundError:
            print("❌ No existing manifest found. Run without --skip-discovery first.")
            return
    else:
        # Discover all PDFs
        pdfs = await discover_all_datasets()
    
    if not pdfs:
        print("❌ No PDFs discovered!")
        return
    
    # Ask for confirmation
    print(f"\nReady to download {len(pdfs)} PDF files.")
    response = input("Continue? [Y/n]: ").strip().lower()
    
    if response not in ("", "y", "yes"):
        print("Cancelled.")
        return
    
    # Download all PDFs
    await download_all_pdfs(pdfs)
    
    print("\n🎉 Done! Next step: Run 'bash scripts/process.sh' to organize files")


if __name__ == "__main__":
    asyncio.run(main())
