#!/usr/bin/env python3
"""
Quick test download of first 5 Epstein PDFs
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright

async def test_download():
    """Test download first 5 PDFs."""
    
    # Load manifest
    with open("reference/epstein_manifest.json") as f:
        manifest = json.load(f)
    
    pdfs = manifest.get("pdfs", [])[:5]  # Just first 5
    
    output_dir = "reference/epstein_files"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🧪 Testing download of {len(pdfs)} PDFs...\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for i, pdf_info in enumerate(pdfs, 1):
            url = pdf_info["url"]
            filename = url.split("/")[-1].replace("%20", "_")
            output_path = os.path.join(output_dir, filename)
            
            print(f"  [{i}/{len(pdfs)}] {filename}")
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            try:
                # Navigate and handle age verification
                await page.goto("https://www.justice.gov/epstein/doj-disclosures", 
                              wait_until="networkidle", timeout=30000)
                
                try:
                    await page.goto(url, timeout=30000)
                except:
                    pass
                
                # Check for age verification
                try:
                    yes_btn = await page.wait_for_selector('button:has-text("Yes")', timeout=3000)
                    if yes_btn:
                        await yes_btn.click()
                        await asyncio.sleep(2)
                        print("            ✅ Age verification passed")
                except:
                    print("            ℹ️  No age verification needed")
                
                # Try to download
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
                        print(f"            ✅ Downloaded: {len(data):,} bytes")
                    else:
                        print(f"            ❌ Not a PDF")
                else:
                    error = response.get("error", "Unknown") if isinstance(response, dict) else "Invalid"
                    print(f"            ❌ Error: {error}")
                    
            except Exception as e:
                print(f"            ❌ Failed: {str(e)[:50]}")
            
            await context.close()
        
        await browser.close()
    
    print(f"\n✅ Test complete!")
    print(f"📁 Check {output_dir}/ for downloaded files")

if __name__ == "__main__":
    asyncio.run(test_download())
