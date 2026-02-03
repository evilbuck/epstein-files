#!/usr/bin/env python3
"""
Download Orchestrator

Takes discovery results and downloads PDFs using Playwright.
Separates the mechanical download work from the discovery intelligence.
"""

import asyncio
import json
import os
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from typing import List, Dict


class DownloadOrchestrator:
    """Orchestrates PDF downloads from discovered URLs."""
    
    def __init__(self, output_dir: str = "reference"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.downloaded: List[Dict] = []
        self.failed: List[Dict] = []
    
    async def download_pdfs(self, pdf_list: List[Dict], browser_page=None):
        """Download a list of PDFs. Can reuse existing browser page."""
        
        if not browser_page:
            # Launch browser if not provided
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
        else:
            page = browser_page
            playwright = None
            browser = None
        
        try:
            print(f"\n📥 Downloading {len(pdf_list)} PDF(s)...\n")
            
            for i, pdf_info in enumerate(pdf_list, 1):
                url = pdf_info.get('url', pdf_info)
                parsed = urlparse(url)
                filename = os.path.basename(parsed.path)
                
                if not filename or not filename.endswith('.pdf'):
                    filename = f"epstein_doc_{i}.pdf"
                
                output_path = os.path.join(self.output_dir, filename)
                
                # Skip if already exists
                if os.path.exists(output_path):
                    print(f"   [{i}/{len(pdf_list)}] ⏭️  Skipping (exists): {filename}")
                    self.downloaded.append({
                        'url': url,
                        'filename': filename,
                        'status': 'already_exists',
                        'path': output_path
                    })
                    continue
                
                print(f"   [{i}/{len(pdf_list)}] Downloading: {filename}")
                
                try:
                    # Use browser to download
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
                    
                    if isinstance(response, dict) and 'error' in response:
                        raise Exception(response['error'])
                    
                    # response is now a string (base64 data URL)
                    if response and isinstance(response, str) and ',' in response:
                        import base64
                        base64_data = response.split(',')[1]
                        binary_data = base64.b64decode(base64_data)
                        
                        with open(output_path, 'wb') as f:
                            f.write(binary_data)
                        
                        size = len(binary_data)
                        print(f"            ✓ Saved: {size:,} bytes")
                        
                        self.downloaded.append({
                            'url': url,
                            'filename': filename,
                            'status': 'downloaded',
                            'size': size,
                            'path': output_path
                        })
                    else:
                        raise Exception("Invalid response format")
                    
                except Exception as e:
                    print(f"            ✗ Failed: {e}")
                    self.failed.append({
                        'url': url,
                        'filename': filename,
                        'error': str(e)
                    })
                
                # Small delay between downloads
                await asyncio.sleep(0.5)
            
        finally:
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()
    
    def generate_report(self) -> str:
        """Generate download report."""
        lines = []
        lines.append("\n" + "="*70)
        lines.append("DOWNLOAD REPORT")
        lines.append("="*70)
        lines.append(f"\n✅ Successfully downloaded: {len(self.downloaded)}")
        lines.append(f"❌ Failed: {len(self.failed)}")
        
        if self.downloaded:
            total_size = sum(d.get('size', 0) for d in self.downloaded)
            lines.append(f"📦 Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
            lines.append(f"\nDownloaded files:")
            for d in self.downloaded:
                size_str = f"{d.get('size', 0):,} bytes" if 'size' in d else "(exists)"
                lines.append(f"  • {d['filename']} - {size_str}")
        
        if self.failed:
            lines.append(f"\nFailed downloads:")
            for f in self.failed:
                lines.append(f"  • {f['filename']}: {f['error']}")
        
        lines.append(f"\nOutput directory: {self.output_dir}/")
        lines.append("="*70)
        
        return '\n'.join(lines)
    
    def save_manifest(self, filename: str = 'reference/download_manifest.json'):
        """Save download manifest."""
        manifest = {
            'downloaded': self.downloaded,
            'failed': self.failed,
            'total_count': len(self.downloaded) + len(self.failed),
            'success_count': len(self.downloaded)
        }
        with open(filename, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"\n💾 Manifest saved to {filename}")


def load_discovery_state(path: str = 'reference/discovery_state.json') -> List[Dict]:
    """Load PDFs from discovery state."""
    try:
        with open(path, 'r') as f:
            state = json.load(f)
        return state.get('pdfs', [])
    except FileNotFoundError:
        print(f"❌ Discovery state not found: {path}")
        print("   Run: python3 scripts/discovery_agent.py")
        return []


async def main():
    """CLI entry point."""
    import sys
    
    # Check for discovery state
    pdfs = load_discovery_state()
    
    if not pdfs:
        print("\n⚠️  No PDFs found in discovery state.")
        print("   Run discovery first:")
        print("   python3 scripts/discovery_agent.py")
        return
    
    print(f"\n📋 Found {len(pdfs)} PDF(s) in discovery state")
    print("\nDiscovered PDFs:")
    for i, pdf in enumerate(pdfs[:10], 1):
        print(f"  {i}. {pdf['url'][:80]}...")
    if len(pdfs) > 10:
        print(f"  ... and {len(pdfs) - 10} more")
    
    # Ask for confirmation
    print("\n" + "="*70)
    response = input("Download all discovered PDFs? [Y/n]: ").strip().lower()
    
    if response not in ('', 'y', 'yes'):
        print("Cancelled.")
        return
    
    # Download
    orchestrator = DownloadOrchestrator()
    await orchestrator.download_pdfs(pdfs)
    
    # Report
    print(orchestrator.generate_report())
    orchestrator.save_manifest()
    
    # Next steps
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Process downloaded files:")
    print("   bash scripts/process.sh")
    print("\n2. View organized files:")
    print("   ls -la data/epstein_pdfs/")


if __name__ == "__main__":
    asyncio.run(main())
