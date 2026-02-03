#!/usr/bin/env python3
"""
Download ALL 375 Epstein PDFs with Age Verification Bypass
"""

import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

async def download_all():
    """Download all Epstein PDFs."""
    
    # Load manifest
    with open("reference/epstein_manifest.json") as f:
        manifest = json.load(f)
    
    pdfs = manifest.get("pdfs", [])
    
    output_dir = "reference/epstein_files"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📥 Downloading {len(pdfs)} PDFs with age verification bypass...\n")
    
    downloaded = 0
    failed = 0
    total_size = 0
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for i, pdf_info in enumerate(pdfs, 1):
            url = pdf_info["url"]
            filename = url.split("/")[-1].replace("%20", "_")
            output_path = os.path.join(output_dir, filename)
            
            # Skip if already exists and is valid
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                size = os.path.getsize(output_path)
                total_size += size
                downloaded += 1
                if i % 10 == 0:
                    print(f"  [{i}/{len(pdfs)}] ⏭️  {filename} ({size:,} bytes) - exists")
                continue
            
            print(f"  [{i}/{len(pdfs)}] {filename}")
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            try:
                # Navigate to disclosures first
                await page.goto("https://www.justice.gov/epstein/doj-disclosures", 
                              wait_until="networkidle", timeout=30000)
                
                # Navigate to PDF
                try:
                    await page.goto(url, timeout=30000)
                except:
                    pass
                
                # Handle age verification
                try:
                    yes_btn = await page.wait_for_selector('button:has-text("Yes")', timeout=3000)
                    if yes_btn:
                        await yes_btn.click()
                        await asyncio.sleep(2)
                except:
                    pass
                
                # Download
                response = await page.evaluate('''async (url) => {
                    try {
                        const res = await fetch(url);
                        if (!res.ok) return { error: `HTTP ${res.status}` };
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
                
                if isinstance(response, str) and "," in response:
                    import base64
                    data = base64.b64decode(response.split(",")[1])
                    
                    if data[:4] == b"%PDF":
                        with open(output_path, "wb") as f:
                            f.write(data)
                        total_size += len(data)
                        downloaded += 1
                        print(f"            ✅ {len(data):,} bytes")
                    else:
                        failed += 1
                        print(f"            ❌ Not a PDF")
                else:
                    failed += 1
                    error = response.get("error", "Unknown") if isinstance(response, dict) else "Invalid"
                    print(f"            ❌ {error}")
                    
            except Exception as e:
                failed += 1
                print(f"            ❌ {str(e)[:50]}")
            
            await context.close()
            
            # Progress every 25 files
            if i % 25 == 0:
                print(f"\n📊 Progress: {i}/{len(pdfs)} (✅ {downloaded}, ❌ {failed})\n")
        
        await browser.close()
    
    # Summary
    print(f"\n{'='*70}")
    print("DOWNLOAD COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Downloaded: {downloaded}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success rate: {downloaded/len(pdfs)*100:.1f}%")
    print(f"📦 Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    print(f"📁 Location: {output_dir}/")

if __name__ == "__main__":
    print("🚀 Starting download of all 375 Epstein PDFs\n")
    asyncio.run(download_all())
    print("\n✨ Complete!")
