#!/usr/bin/env python3
"""
Epstein File Finder - Uses Playwright to search DOJ site
"""

import asyncio
import sys
from playwright.async_api import async_playwright

async def search_epstein():
    """Search DOJ site for Epstein documents."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print("🔍 Searching DOJ site for Epstein documents...")
        print()
        
        # Try to access the Epstein page directly
        urls_to_try = [
            "https://www.justice.gov/usao-sdny/pr",
            "https://www.justice.gov/criminal-ceos/child-exploitation",
            "https://www.justice.gov/criminal/ceos",
            "https://www.justice.gov/opa",
        ]
        
        for url in urls_to_try:
            print(f"\n📄 Trying: {url}")
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                title = await page.title()
                print(f"   Title: {title}")
                
                # Search for Epstein on the page
                content = await page.content()
                if 'epstein' in content.lower():
                    print("   ✅ Found 'Epstein' mention on this page!")
                    
                    # Get all links
                    links = await page.eval_on_selector_all('a[href]', 
                        'els => els.map(e => ({href: e.href, text: e.innerText})).filter(l => l.href && l.href.includes(".pdf"))'
                    )
                    
                    if links:
                        print(f"   📥 Found {len(links)} PDF links:")
                        for link in links[:5]:
                            print(f"      - {link.get('text', 'PDF')[:50]}: {link['href'][:70]}")
                    
                    # Look for case-related links
                    all_links = await page.eval_on_selector_all('a[href]', 
                        'els => els.map(e => ({href: e.href, text: e.innerText})).filter(l => l.text && l.text.toLowerCase().includes("epstein"))'
                    )
                    
                    if all_links:
                        print(f"   🔗 Found {len(all_links)} Epstein-related links:")
                        for link in all_links[:10]:
                            print(f"      - {link.get('text', 'Link')[:50]}: {link['href'][:70]}")
                else:
                    print("   ❌ No 'Epstein' mention found")
                    
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
        
        await browser.close()
        print("\n🔒 Search complete")

if __name__ == "__main__":
    asyncio.run(search_epstein())
