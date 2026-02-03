#!/usr/bin/env python3
"""
Epstein File Downloader using Playwright

This script uses browser automation to download PDFs from the DOJ website.
It can search for Epstein-related content or use a specific URL if known.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python3 scripts/download_playwright.py [URL]
    
Examples:
    python3 scripts/download_playwright.py
    python3 scripts/download_playwright.py "https://www.justice.gov/usao-sdny/pr/federal-bureau-prisons-director-indicted-conspiracy-sexual-abuse-and-fraud-case"
"""

import asyncio
import sys
import os
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright


async def download_pdfs_from_page(url, output_dir="reference"):
    """Download all PDFs from a given page."""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🔍 Launching browser to access: {url}")
    print("   (This may take a moment to load the page)")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        pdf_links = set()
        
        # Track all responses to catch PDFs
        def handle_response(response):
            response_url = response.url
            if '.pdf' in response_url.lower():
                pdf_links.add(response_url)
        
        page.on("response", handle_response)
        
        try:
            print(f"\n🌐 Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)  # Wait for dynamic content
            
            title = await page.title()
            print(f"\n✓ Page loaded: {title}")
            
            # Get all PDF links from the page
            print("\n🔍 Scanning for PDF links...")
            links = await page.eval_on_selector_all('a[href]', 
                '''elements => elements.map(el => el.href).filter(href => href && href.includes('.pdf'))'''
            )
            
            for link in links:
                if link:
                    absolute_url = urljoin(url, link)
                    pdf_links.add(absolute_url)
            
            # Download PDFs
            if pdf_links:
                print(f"\n📥 Found {len(pdf_links)} PDF(s):\n")
                
                for pdf_url in sorted(pdf_links):
                    parsed = urlparse(pdf_url)
                    filename = os.path.basename(parsed.path) or f"doc_{len(os.listdir(output_dir))}.pdf"
                    output_path = os.path.join(output_dir, filename)
                    
                    print(f"   Downloading: {filename}")
                    
                    try:
                        response = await page.evaluate('''async (url) => {
                            const res = await fetch(url);
                            const blob = await res.blob();
                            return await new Promise((resolve) => {
                                const reader = new FileReader();
                                reader.onloadend = () => resolve(reader.result);
                                reader.readAsDataURL(blob);
                            });
                        }''', pdf_url)
                        
                        if response and ',' in response:
                            import base64
                            base64_data = response.split(',')[1]
                            binary_data = base64.b64decode(base64_data)
                            
                            with open(output_path, 'wb') as f:
                                f.write(binary_data)
                            
                            print(f"   ✓ Saved: {filename} ({len(binary_data):,} bytes)")
                        
                    except Exception as e:
                        print(f"   ✗ Error: {e}")
                
                pdf_count = len([f for f in os.listdir(output_dir) if f.endswith('.pdf')])
                print(f"\n✅ Complete! Total PDFs in {output_dir}/: {pdf_count}")
                
            else:
                print("\n⚠️  No PDF links found")
                html = await page.content()
                debug_path = os.path.join(output_dir, "page_debug.html")
                with open(debug_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"   Debug saved: {debug_path}")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()
            print("\n🔒 Browser closed")


if __name__ == "__main__":
    # Default URL or use command line argument
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.justice.gov/epstein"
    
    try:
        import playwright
    except ImportError:
        print("❌ Playwright not installed!")
        print("\nInstall with:")
        print("   pip install playwright")
        print("   playwright install chromium")
        sys.exit(1)
    
    asyncio.run(download_pdfs_from_page(url))
