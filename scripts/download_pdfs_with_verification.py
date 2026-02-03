#!/usr/bin/env python3
"""
Download Epstein PDFs with Age Verification Bypass
Uses Playwright to navigate through age verification for each file
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright

async def download_with_age_verification():
    """Download all Epstein PDFs, handling age verification."""
    
    # Load manifest
    manifest_path = "reference/epstein_manifest.json"
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        pdfs = manifest.get("pdfs", [])
    except FileNotFoundError:
        print("❌ Manifest not found. Run discovery first.")
        return
    
    if not pdfs:
        print("❌ No PDFs in manifest.")
        return
    
    output_dir = "reference/epstein_files"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📥 Downloading {len(pdfs)} PDFs with age verification bypass...")
    print()
    
    downloaded = []
    failed = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for i, pdf_info in enumerate(pdfs, 1):
            url = pdf_info["url"]
            filename = url.split("/")[-1].replace("%20", "_")
            output_path = os.path.join(output_dir, filename)
            
            # Skip if already exists
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"  [{i}/{len(pdfs)}] ⏭️  {filename} (exists)")
                downloaded.append({"url": url, "filename": filename, "status": "exists"})
                continue
            
            print(f"  [{i}/{len(pdfs)}] ⬇️  {filename}")
            
            # Create fresh context for each download to handle age verification
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            
            try:
                # Step 1: Go to disclosures page to establish session
                await page.goto("https://www.justice.gov/epstein/doj-disclosures", 
                              wait_until="networkidle", timeout=30000)
                
                # Step 2: Navigate to the PDF URL
                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                except Exception as e:
                    # Check if it's a download starting
                    if "Download is starting" in str(e):
                        pass  # This is expected
                    else:
                        raise
                
                # Step 3: Check for age verification
                try:
                    # Look for age verification buttons
                    yes_button = await page.wait_for_selector('button:has-text("Yes")', timeout=5000)
                    if yes_button:
                        print("            🖱️  Clicking age verification...")
                        await yes_button.click()
                        await asyncio.sleep(3)
                except:
                    pass  # No age verification or already passed
                
                # Step 4: Download the file
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
                    
                    # Verify it's a PDF
                    if binary_data[:4] == b"%PDF":
                        with open(output_path, "wb") as f:
                            f.write(binary_data)
                        size = len(binary_data)
                        print(f"            ✓ {size:,} bytes")
                        downloaded.append({"url": url, "filename": filename, "size": size})
                    else:
                        raise Exception("Not a valid PDF")
                else:
                    raise Exception("Invalid response")
                    
            except Exception as e:
                print(f"            ✗ Error: {str(e)[:50]}")
                failed.append({"url": url, "filename": filename, "error": str(e)})
            
            finally:
                await context.close()
            
            # Progress update every 10 files
            if i % 10 == 0:
                print(f"\n📊 Progress: {i}/{len(pdfs)} (✓ {len(downloaded)}, ✗ {len(failed)})\n")
        
        await browser.close()
    
    # Save report
    report = {
        "total": len(pdfs),
        "downloaded": len(downloaded),
        "failed": len(failed),
        "success_rate": f"{len(downloaded)/len(pdfs)*100:.1f}%"
    }
    
    with open("reference/download_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*70}")
    print("DOWNLOAD COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Downloaded: {len(downloaded)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📊 Success rate: {len(downloaded)/len(pdfs)*100:.1f}%")
    print(f"📁 Files in: {output_dir}/")
    
    if downloaded:
        total_size = sum(d.get("size", 0) for d in downloaded if "size" in d)
        print(f"📦 Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")

if __name__ == "__main__":
    print("🚀 Starting Epstein PDF download with age verification bypass\n")
    asyncio.run(download_with_age_verification())
    print("\n✨ Done! Check reference/epstein_files/ for downloaded PDFs.")
