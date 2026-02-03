#!/usr/bin/env python3
"""
Download Epstein Data Set ZIPs with Age Verification
Uses Playwright to click through age verification and download zip files
"""

import asyncio
import os
from playwright.async_api import async_playwright

async def download_with_verification():
    """Download all Data Set zips with age verification."""
    
    output_dir = "reference"
    os.makedirs(output_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Need to see browser for verification
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print("="*70)
        print("EPSTEIN DATA SET DOWNLOADER")
        print("="*70)
        print()
        print("This script will:")
        print("1. Navigate to each Data Set zip file")
        print("2. Click through age verification if prompted")
        print("3. Download the zip file")
        print()
        
        for i in range(1, 8):
            url = f"https://www.justice.gov/epstein/files/DataSet%20{i}.zip"
            output_path = os.path.join(output_dir, f"DataSet_{i}.zip")
            
            # Skip if already exists and is valid
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                if size > 100000:  # > 100KB = likely valid zip
                    print(f"✓ Data Set {i} already exists ({size:,} bytes)")
                    continue
            
            print(f"\n{'='*70}")
            print(f"📦 Data Set {i}")
            print(f"{'='*70}")
            print(f"URL: {url}")
            print()
            
            try:
                # Navigate to the zip file URL
                print("🌐 Loading page...")
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                title = await page.title()
                print(f"📄 Page title: {title}")
                
                # Check if there's an age verification button
                # Common patterns: "I am 18+", "Enter", "Continue", "Verify"
                possible_buttons = [
                    'button:has-text("18")',
                    'button:has-text("Enter")',
                    'button:has-text("Continue")',
                    'button:has-text("Verify")',
                    'button:has-text("Yes")',
                    'button:has-text("I agree")',
                    'input[type="submit"]',
                    'button[type="submit"]',
                ]
                
                button_clicked = False
                for selector in possible_buttons:
                    try:
                        button = await page.wait_for_selector(selector, timeout=5000)
                        if button:
                            button_text = await button.text_content()
                            print(f"🖱️  Clicking button: '{button_text}'")
                            await button.click()
                            await asyncio.sleep(3)  # Wait for download/redirect
                            button_clicked = True
                            break
                    except:
                        continue
                
                if not button_clicked:
                    print("⚠️  No verification button found - may have auto-redirected")
                
                # Try to download the file using browser fetch
                print("⬇️  Attempting download...")
                response = await page.evaluate('''async () => {
                    // Get the current URL after any redirects
                    const currentUrl = window.location.href;
                    
                    try {
                        const res = await fetch(currentUrl);
                        if (!res.ok) throw new Error(`HTTP ${res.status}`);
                        
                        // Check content type
                        const contentType = res.headers.get('content-type');
                        
                        const blob = await res.blob();
                        return await new Promise((resolve) => {
                            const reader = new FileReader();
                            reader.onloadend = () => resolve({
                                data: reader.result,
                                contentType: contentType,
                                size: blob.size
                            });
                            reader.readAsDataURL(blob);
                        });
                    } catch (e) {
                        return { error: e.message };
                    }
                }''')
                
                if isinstance(response, dict):
                    if 'error' in response:
                        print(f"  ✗ Download error: {response['error']}")
                        continue
                    
                    if 'data' in response and ',' in response['data']:
                        import base64
                        base64_data = response['data'].split(',')[1]
                        binary_data = base64.b64decode(base64_data)
                        
                        # Check if it's a valid zip
                        if binary_data[:2] == b'PK':
                            with open(output_path, 'wb') as f:
                                f.write(binary_data)
                            print(f"  ✓ Downloaded: {len(binary_data):,} bytes")
                            print(f"  💾 Saved to: {output_path}")
                        else:
                            print(f"  ⚠️  Not a valid zip file")
                            print(f"     Content-Type: {response.get('contentType', 'unknown')}")
                            print(f"     Size: {len(binary_data):,} bytes")
                            
                            # Save for inspection
                            debug_path = output_path.replace('.zip', '_debug.html')
                            with open(debug_path, 'wb') as f:
                                f.write(binary_data)
                            print(f"     Debug saved to: {debug_path}")
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                import traceback
                traceback.print_exc()
        
        await browser.close()
        
        print(f"\n{'='*70}")
        print("DOWNLOAD COMPLETE")
        print(f"{'='*70}")
        print("\nDownloaded files:")
        for i in range(1, 8):
            path = os.path.join(output_dir, f"DataSet_{i}.zip")
            if os.path.exists(path):
                size = os.path.getsize(path)
                is_zip = size > 100000  # Rough check
                status = "✓" if is_zip else "?"
                print(f"  {status} Data Set {i}: {size:,} bytes")

if __name__ == "__main__":
    print("🚀 Starting Epstein Data Set downloader with age verification")
    print("A browser window will open for each Data Set.")
    print("If age verification appears, the script will attempt to click it.")
    print()
    
    try:
        asyncio.run(download_with_verification())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
