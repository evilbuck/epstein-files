#!/usr/bin/env python3
"""
Smart Spider Agent

An intelligent crawler that:
1. Uses CLI tools (curl, htmlq) to extract links from pages
2. Presents discovered links to the model
3. Model selects which links to follow based on relevance
4. Recursively crawls until PDFs are found or max depth reached

Usage:
    # Start crawling from a URL
    python3 scripts/spider_agent.py "https://www.justice.gov/usao-sdny"
    
    # The agent will:
    # 1. Crawl the page using CLI tools
    # 2. Show you discovered links
    # 3. Ask which links to follow
    # 4. Recurse until PDFs are found
"""

import subprocess
import json
import re
import os
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, asdict


@dataclass
class PageData:
    """Structured data about a crawled page."""
    url: str
    title: str
    html_size: int
    pdf_links: List[Dict]
    nav_links: List[Dict]
    text_content: str  # First 2000 chars of visible text
    depth: int
    
    def to_summary(self) -> str:
        """Generate human-readable summary for model review."""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"PAGE: {self.url}")
        lines.append(f"TITLE: {self.title}")
        lines.append(f"DEPTH: {self.depth}")
        lines.append(f"SIZE: {self.html_size:,} bytes")
        lines.append(f"{'='*60}")
        
        if self.pdf_links:
            lines.append(f"\n📄 PDFs FOUND: {len(self.pdf_links)}")
            for i, pdf in enumerate(self.pdf_links[:5], 1):
                lines.append(f"  {i}. {pdf.get('text', 'PDF')[:60]}")
                lines.append(f"     URL: {pdf['url'][:70]}...")
            if len(self.pdf_links) > 5:
                lines.append(f"     ... and {len(self.pdf_links) - 5} more")
        
        if self.nav_links:
            lines.append(f"\n🔗 NAVIGATION LINKS: {len(self.nav_links)}")
            for i, link in enumerate(self.nav_links[:10], 1):
                text = link.get('text', '')[:50]
                lines.append(f"  {i}. {text or 'Link'}")
                lines.append(f"     → {link['url'][:70]}...")
            if len(self.nav_links) > 10:
                lines.append(f"     ... and {len(self.nav_links) - 10} more")
        
        lines.append(f"\n📝 PAGE PREVIEW:")
        lines.append(self.text_content[:500])
        lines.append("...")
        
        return '\n'.join(lines)


class SpiderTool:
    """CLI-based spider - no model calls here, just mechanical extraction."""
    
    def __init__(self, start_url: str, max_depth: int = 3):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited: Set[str] = set()
        self.discovered_pdfs: List[Dict] = []
        self.crawl_log: List[PageData] = []
        
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page using curl."""
        try:
            result = subprocess.run(
                [
                    'curl', '-s', '-L', url,
                    '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    '-H', 'Accept-Language: en-US,en;q=0.9',
                    '--max-time', '30',
                    '--retry', '2'
                ],
                capture_output=True,
                text=True
            )
            return result.stdout if result.returncode == 0 else None
        except Exception as e:
            print(f"  ⚠️  Error fetching {url}: {e}")
            return None
    
    def extract_text_content(self, html: str) -> str:
        """Extract readable text from HTML using CLI tools."""
        try:
            # Try using html2text if available
            result = subprocess.run(
                ['html2text', '-b', '0', '--ignore-images', '--ignore-links'],
                input=html,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout[:2000]
        except FileNotFoundError:
            pass
        
        # Fallback: strip tags with sed
        try:
            result = subprocess.run(
                ['sed', 's/<[^>]*>//g'],
                input=html,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                text = result.stdout
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text)
                return text[:2000]
        except:
            pass
        
        # Last resort: simple regex
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text[:2000]
    
    def extract_links_htmlq(self, html: str, base_url: str) -> tuple:
        """Extract links using htmlq. Returns (pdfs, nav_links)."""
        pdfs = []
        nav_links = []
        
        try:
            # Get all hrefs
            result = subprocess.run(
                ['htmlq', '-a', 'href', 'a'],
                input=html,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return self.extract_links_regex(html, base_url)
            
            urls = list(set(result.stdout.strip().split('\n')))
            
            for url in urls:
                url = url.strip()
                if not url or url.startswith('#') or url.startswith('javascript:'):
                    continue
                
                # Make absolute URL
                if url.startswith('/'):
                    parsed_base = urlparse(base_url)
                    url = f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
                elif not url.startswith('http'):
                    url = urljoin(base_url, url)
                
                parsed = urlparse(url)
                
                # Skip non-justice.gov domains
                if not parsed.netloc.endswith('justice.gov'):
                    continue
                
                # Get link text - escape quotes in URL for selector
                safe_url = url.replace('"', '\\"')
                text_result = subprocess.run(
                    ['htmlq', '-t', f'a[href="{safe_url}"]'],
                    input=html,
                    capture_output=True,
                    text=True
                )
                text = text_result.stdout.strip()[:100] if text_result.returncode == 0 else ''
                
                link_data = {'url': url, 'text': text, 'domain': parsed.netloc}
                
                if url.lower().endswith('.pdf'):
                    pdfs.append(link_data)
                else:
                    nav_links.append(link_data)
                    
        except Exception as e:
            print(f"  ⚠️  htmlq extraction failed: {e}")
            return self.extract_links_regex(html, base_url)
        
        return pdfs, nav_links
    
    def extract_links_regex(self, html: str, base_url: str) -> tuple:
        """Fallback link extraction using regex."""
        pdfs = []
        nav_links = []
        
        # Find all hrefs
        pattern = r'href=["\']([^"\']+)["\']'
        matches = re.findall(pattern, html)
        
        seen = set()
        for url in matches:
            url = url.strip()
            if not url or url in seen:
                continue
            seen.add(url)
            
            if url.startswith('#') or url.startswith('javascript:'):
                continue
            
            # Make absolute
            if url.startswith('/'):
                parsed_base = urlparse(base_url)
                url = f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
            elif not url.startswith('http'):
                url = urljoin(base_url, url)
            
            parsed = urlparse(url)
            
            # Only justice.gov domains
            if not parsed.netloc.endswith('justice.gov'):
                continue
            
            link_data = {'url': url, 'text': '', 'domain': parsed.netloc}
            
            if url.lower().endswith('.pdf'):
                pdfs.append(link_data)
            else:
                nav_links.append(link_data)
        
        return pdfs, nav_links
    
    def crawl_page(self, url: str, depth: int = 0) -> Optional[PageData]:
        """Crawl a single page and return structured data."""
        if depth > self.max_depth or url in self.visited:
            return None
        
        self.visited.add(url)
        print(f"\n🔍 Crawling (depth {depth}): {url[:70]}...")
        
        html = self.fetch_page(url)
        if not html:
            return None
        
        # Check for Akamai
        if 'bm-verify' in html or 'akamai' in html.lower():
            print(f"  ⚠️  Akamai challenge detected - requires browser automation")
            return None
        
        # Extract data
        title_match = re.search(r'<title[^>]*>([^<]*)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else 'No title'
        
        pdfs, nav_links = self.extract_links_htmlq(html, url)
        text_content = self.extract_text_content(html)
        
        # Store PDFs
        for pdf in pdfs:
            if pdf['url'] not in [p['url'] for p in self.discovered_pdfs]:
                self.discovered_pdfs.append({
                    **pdf,
                    'source_page': url,
                    'depth': depth
                })
        
        page_data = PageData(
            url=url,
            title=title,
            html_size=len(html),
            pdf_links=pdfs,
            nav_links=nav_links,
            text_content=text_content,
            depth=depth
        )
        
        self.crawl_log.append(page_data)
        
        print(f"  ✓ Found: {len(pdfs)} PDFs, {len(nav_links)} links")
        
        return page_data
    
    def interactive_crawl(self):
        """Interactive crawling - presents results and asks for next steps."""
        print("="*70)
        print("SMART SPIDER AGENT")
        print("="*70)
        print(f"\nStarting from: {self.start_url}")
        print("Max depth:", self.max_depth)
        print("\nThis agent will:")
        print("  1. Crawl pages using CLI tools (curl, htmlq)")
        print("  2. Show you what was discovered")
        print("  3. Let you choose which links to follow")
        print()
        
        # Initial crawl
        current_page = self.crawl_page(self.start_url, depth=0)
        
        if not current_page:
            print("❌ Failed to crawl starting page")
            return
        
        # Show results
        print(current_page.to_summary())
        
        # If PDFs found, ask if we should download
        if self.discovered_pdfs:
            print(f"\n{'='*70}")
            print(f"🎉 FOUND {len(self.discovered_pdfs)} PDF(s)!")
            print(f"{'='*70}")
            
            for i, pdf in enumerate(self.discovered_pdfs[:10], 1):
                print(f"{i}. {pdf['url']}")
                if pdf.get('text'):
                    print(f"   Text: {pdf['text'][:60]}")
            
            print("\n💾 Run this to download:")
            print("   python3 scripts/download_orchestrator.py")
            self.save_state()
            return
        
        # Otherwise, ask which links to follow
        if current_page.nav_links:
            print(f"\n{'='*70}")
            print("SELECT LINKS TO FOLLOW")
            print(f"{'='*70}")
            print("\nEnter the numbers of links to crawl next (comma-separated)")
            print("Or type 'all' to crawl all, 'stop' to end\n")
            
            for i, link in enumerate(current_page.nav_links[:15], 1):
                text = link.get('text', '')[:50] or 'Link'
                print(f"{i}. {text}")
                print(f"   → {link['url'][:65]}...")
                print()
            
            if len(current_page.nav_links) > 15:
                print(f"... and {len(current_page.nav_links) - 15} more links\n")
            
            choice = input("Your selection: ").strip().lower()
            
            if choice == 'stop':
                print("\nStopped.")
                self.save_state()
                return
            
            if choice == 'all':
                selected = current_page.nav_links[:5]  # Limit to prevent explosion
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in choice.split(',')]
                    selected = [current_page.nav_links[i] for i in indices if 0 <= i < len(current_page.nav_links)]
                except (ValueError, IndexError):
                    print("Invalid selection. Stopping.")
                    self.save_state()
                    return
            
            # Recursively crawl selected links
            for link in selected:
                self.crawl_page(link['url'], depth=1)
            
            # Show final summary
            print(f"\n{'='*70}")
            print("CRAWL SUMMARY")
            print(f"{'='*70}")
            print(f"Pages crawled: {len(self.crawl_log)}")
            print(f"Total PDFs found: {len(self.discovered_pdfs)}")
            print(f"URLs visited: {len(self.visited)}")
            
            if self.discovered_pdfs:
                print(f"\n✅ Found {len(self.discovered_pdfs)} PDF(s)!")
                print("\n💾 To download:")
                print("   python3 scripts/download_orchestrator.py")
            
            self.save_state()
    
    def save_state(self, filename: str = 'reference/spider_state.json'):
        """Save spider state."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        state = {
            'start_url': self.start_url,
            'max_depth': self.max_depth,
            'visited': list(self.visited),
            'pdfs': self.discovered_pdfs,
            'pages': [asdict(p) for p in self.crawl_log]
        }
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"\n💾 State saved to {filename}")


def main():
    import sys
    
    start_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.justice.gov/usao-sdny"
    
    spider = SpiderTool(start_url, max_depth=3)
    spider.interactive_crawl()


if __name__ == "__main__":
    main()
