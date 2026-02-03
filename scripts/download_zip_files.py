#!/usr/bin/env python3
"""
Download Epstein Data Set ZIPs
Properly handles Playwright download events
"""

import asyncio
import os
from playwright.async_api import async_playwright

async def download_datasets():
    """Download all Data Set zips."""
    
    output_dir = "reference"
    os.makedirs(output_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        print("="*70)
        print("EPSTEIN DATA SET DOWNLOADER")
        print("="*70)
        print()
        
        for i in range(1, 8):
            url = f"https://www.justice.gov/epstein/files/DataSet%20{i}.zip"
            output_path = os.path.join(output_dir, f"DataSet_{i}.zip")
            
            # Skip if already exists and is large enough
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                if size > 100000:  # > 100KB
                    print(f"✓ Data Set {i}: Already exists ({size:,} bytes)")
                    continue
            
            print(f"\n📦 Data Set {i}")
            print(f"   URL: {url}")
            
            # Create new context for each download
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            # Enable downloads
            context.set_default_timeout(120000)
            
            page = await context.new_page()
            
            # Handle download event
            download_success = False
            
            async def handle_download(download):
                nonlocal download_success
                try:
                    await download.save_as(output_path)
                    size = os.path.getsize(output_path)
                    print(f"   ✓ Downloaded: {size:,} bytes")
                    download_success = True
                except Exception as e:
                    print(f"   ✗ Download failed: {e}")
            
            page.on("download", lambda d: asyncio.create_task(handle_download(d)))
            
            try:
                # Navigate to the disclosures page first
                await page.goto("https://www.justice.gov/epstein/doj-disclosures",
                              wait_until="networkidle", timeout=30000)
                
                # Now trigger the download by clicking the link or navigating
                # Try direct navigation which should trigger download
                try:
                    await page.goto(url, timeout=60000)
                except Exception as e:
                    # Expected error when download starts
                    if "Download is starting" in str(e):
                        pass  # This is expected
                    else:
                        raise
                
                # Wait a bit for download to complete
                await asyncio.sleep(5)
                
                if not download_success:
                    print("   ⚠️  Download may not have completed")
                
            except Exception as e:
                print(f"   ✗ Error: {e}")
            
            finally:
                await context.close()
        
        await browser.close()
        
        print(f"\n{'='*70}")
        print("DOWNLOAD COMPLETE")
        print(f"{'='*70}")
        print("\nDownloaded files:")
        total_size = 0
        for i in range(1, 8):
            path = os.path.join(output_dir, f"DataSet_{i}.zip")
            if os.path.exists(path):
                size = os.path.getsize(path)
                total_size += size
                is_zip = size > 100000
                status = "✓" if is_zip else "?"
                print(f"  {status} Data Set {i}: {size:,} bytes")
        
        print(f"\nTotal: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")

if __name__ == "__main__":
    print("🚀 Starting Epstein Data Set downloader\n")
    asyncio.run(download_datasets())
