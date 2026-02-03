#!/usr/bin/env python3
"""
Download Epstein Data Sets using Playwright
Bypasses Akamai protection for actual file downloads
"""

import asyncio
import os
from playwright.async_api import async_playwright

async def download_datasets():
    """Download all Epstein Data Set zip files."""
    
    output_dir = "reference"
    os.makedirs(output_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print("🔍 Accessing DOJ Epstein disclosures page...")
        
        # First navigate to the disclosures page to get cookies/session
        await page.goto("https://www.justice.gov/epstein/doj-disclosures", 
                       wait_until="networkidle", timeout=60000)
        
        print(f"✓ Page loaded: {await page.title()}")
        print()
        
        # Download Data Sets 1-7
        for i in range(1, 8):
            url = f"https://www.justice.gov/epstein/files/DataSet%20{i}.zip"
            output_path = os.path.join(output_dir, f"DataSet_{i}.zip")
            
            # Skip if already exists and is valid
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                if size > 100000:  # > 100KB = likely valid
                    print(f"✓ Data Set {i} already exists ({size:,} bytes)")
                    continue
            
            print(f"⬇️  Downloading Data Set {i}...")
            
            try:
                # Use the browser to download
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
                    print(f"  ✗ Error: {response['error']}")
                    continue
                
                if response and isinstance(response, str) and ',' in response:
                    import base64
                    base64_data = response.split(',')[1]
                    binary_data = base64.b64decode(base64_data)
                    
                    # Check if it's actually a zip (starts with PK)
                    if binary_data[:2] == b'PK':
                        with open(output_path, 'wb') as f:
                            f.write(binary_data)
                        print(f"  ✓ Saved: {len(binary_data):,} bytes")
                    else:
                        print(f"  ⚠️  Not a valid zip file (may be error page)")
                else:
                    print(f"  ✗ Invalid response")
                    
            except Exception as e:
                print(f"  ✗ Failed: {e}")
        
        await browser.close()
        print("\n🔒 Browser closed")
        
        # Show results
        print("\n📦 Download Summary:")
        for i in range(1, 8):
            path = os.path.join(output_dir, f"DataSet_{i}.zip")
            if os.path.exists(path):
                size = os.path.getsize(path)
                status = "✓" if size > 100000 else "?"
                print(f"  {status} Data Set {i}: {size:,} bytes")

if __name__ == "__main__":
    asyncio.run(download_datasets())
