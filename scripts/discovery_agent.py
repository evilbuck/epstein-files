#!/usr/bin/env python3
"""
Epstein Files Discovery Agent

Uses CLI tools (not the model) for crawling and extraction.
The model reviews results and decides which links to follow.

Strategy:
1. Crawl pages using curl + htmlq/pup
2. Extract all links and metadata
3. Present to model for review
4. Model selects promising links
5. Recurse until PDFs are found
"""

import subprocess
import json
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class DiscoveredLink:
    url: str
    text: str
    context: str  # surrounding HTML context
    depth: int
    source_page: str


class DiscoveryTool:
    """CLI-based web discovery tool. No model usage here - pure mechanical extraction."""
    
    def __init__(self, base_url: str, max_depth: int = 3):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited = set()
        self.discovered_links: List[DiscoveredLink] = []
        self.discovered_pdfs: List[Dict] = []
        
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content using curl."""
        try:
            # Use curl with browser-like headers
            result = subprocess.run(
                ['curl', '-s', '-L', url, 
                 '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                 '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                 '--max-time', '30'],
                capture_output=True,
                text=True
            )
            return result.stdout if result.returncode == 0 else None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_links_with_htmlq(self, html: str, base_url: str) -> List[Dict]:
        """Use htmlq to extract links efficiently."""
        links = []
        
        try:
            # Get all anchor tags with hrefs
            result = subprocess.run(
                ['htmlq', '-a', 'href', 'a'],
                input=html,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                urls = result.stdout.strip().split('\n')
                for url in urls:
                    url = url.strip()
                    if url and not url.startswith('#') and not url.startswith('javascript:'):
                        # Make absolute URL
                        if url.startswith('/'):
                            parsed = urlparse(base_url)
                            url = f"{parsed.scheme}://{parsed.netloc}{url}"
                        elif not url.startswith('http'):
                            url = urljoin(base_url, url)
                        
                        # Get link text using htmlq
                        text_result = subprocess.run(
                            ['htmlq', '-t', f'a[href="{url}"]'],
                            input=html,
                            capture_output=True,
                            text=True
                        )
                        text = text_result.stdout.strip()[:100]  # First 100 chars
                        
                        links.append({
                            'url': url,
                            'text': text,
                            'is_pdf': url.lower().endswith('.pdf'),
                            'domain': urlparse(url).netloc
                        })
        except Exception as e:
            print(f"Error extracting links with htmlq: {e}")
        
        return links
    
    def extract_links_with_grep(self, html: str, base_url: str) -> List[Dict]:
        """Fallback: Use grep/regex to extract links."""
        links = []
        
        # Find href attributes
        href_pattern = r'href=["\']([^"\']+)["\']'
        matches = re.findall(href_pattern, html)
        
        for url in matches:
            url = url.strip()
            if url and not url.startswith('#') and not url.startswith('javascript:'):
                # Make absolute
                if url.startswith('/'):
                    parsed = urlparse(base_url)
                    url = f"{parsed.scheme}://{parsed.netloc}{url}"
                elif not url.startswith('http'):
                    url = urljoin(base_url, url)
                
                links.append({
                    'url': url,
                    'text': '',  # No text extraction in fallback
                    'is_pdf': url.lower().endswith('.pdf'),
                    'domain': urlparse(url).netloc
                })
        
        return links
    
    def discover_from_page(self, url: str, depth: int = 0) -> Dict:
        """Discover all links from a single page. Returns structured data for model review."""
        if depth > self.max_depth or url in self.visited:
            return {'url': url, 'status': 'skipped', 'reason': 'visited or max depth'}
        
        self.visited.add(url)
        print(f"  [{'+'*depth}] Crawling: {url[:80]}...")
        
        html = self.fetch_page(url)
        if not html:
            return {'url': url, 'status': 'error', 'reason': 'fetch failed'}
        
        # Check if page is Akamai challenge
        if 'bm-verify' in html or 'akamai' in html.lower():
            return {
                'url': url, 
                'status': 'blocked',
                'reason': 'Akamai JavaScript challenge - requires browser automation',
                'html_sample': html[:500]
            }
        
        # Try htmlq first, fall back to grep
        links = self.extract_links_with_htmlq(html, url)
        if not links:
            links = self.extract_links_with_grep(html, url)
        
        # Separate PDFs from navigation links
        pdfs = [l for l in links if l['is_pdf']]
        nav_links = [l for l in links if not l['is_pdf'] and l['domain'].endswith('justice.gov')]
        external_links = [l for l in links if not l['is_pdf'] and not l['domain'].endswith('justice.gov')]
        
        # Store PDFs
        for pdf in pdfs:
            self.discovered_pdfs.append({
                **pdf,
                'source_page': url,
                'depth': depth
            })
        
        # Store navigation links for model review
        for link in nav_links:
            if link['url'] not in [l.url for l in self.discovered_links]:
                self.discovered_links.append(DiscoveredLink(
                    url=link['url'],
                    text=link['text'],
                    context=self._extract_context(html, link['url']),
                    depth=depth,
                    source_page=url
                ))
        
        return {
            'url': url,
            'status': 'success',
            'depth': depth,
            'page_title': self._extract_title(html),
            'pdf_count': len(pdfs),
            'nav_link_count': len(nav_links),
            'external_link_count': len(external_links),
            'pdfs': pdfs[:10],  # First 10 PDFs
            'nav_links': [{'url': l['url'], 'text': l['text']} for l in nav_links[:20]],  # First 20 nav links
            'external_links': [{'url': l['url'], 'text': l['text']} for l in external_links[:10]],
            'html_size': len(html)
        }
    
    def _extract_title(self, html: str) -> str:
        """Extract page title."""
        match = re.search(r'<title[^>]*>([^<]*)</title>', html, re.IGNORECASE)
        return match.group(1).strip() if match else 'No title'
    
    def _extract_context(self, html: str, url: str) -> str:
        """Extract surrounding context for a URL."""
        # Simple regex to find the anchor tag and surrounding text
        pattern = r'.{0,100}href=["\']' + re.escape(url) + r'["\'].{0,100}'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            context = match.group(0)
            # Clean up
            context = re.sub(r'<[^>]+>', ' ', context)
            context = re.sub(r'\s+', ' ', context)
            return context[:200]
        return ''
    
    def generate_discovery_report(self) -> str:
        """Generate a report for the model to review."""
        report = []
        report.append("=" * 70)
        report.append("DISCOVERY REPORT - Epstein Files Search")
        report.append("=" * 70)
        report.append("")
        report.append(f"Base URL: {self.base_url}")
        report.append(f"Pages crawled: {len(self.visited)}")
        report.append(f"Total PDFs found: {len(self.discovered_pdfs)}")
        report.append(f"Navigation links discovered: {len(self.discovered_links)}")
        report.append("")
        
        if self.discovered_pdfs:
            report.append("-" * 70)
            report.append("PDFs DISCOVERED (Ready to Download)")
            report.append("-" * 70)
            for i, pdf in enumerate(self.discovered_pdfs[:30], 1):  # Show first 30
                report.append(f"\n{i}. {pdf['url']}")
                if pdf.get('text'):
                    report.append(f"   Text: {pdf['text'][:80]}")
                report.append(f"   Source: {pdf['source_page']}")
                report.append(f"   Depth: {pdf['depth']}")
        
        if self.discovered_links:
            report.append("")
            report.append("-" * 70)
            report.append("NAVIGATION LINKS (For Model Review)")
            report.append("-" * 70)
            report.append("Review these links and select which to crawl next:\n")
            
            for i, link in enumerate(self.discovered_links[:50], 1):  # Show first 50
                report.append(f"\n{i}. URL: {link.url}")
                if link.text:
                    report.append(f"   Link text: {link.text}")
                if link.context:
                    report.append(f"   Context: {link.context[:150]}")
                report.append(f"   Depth: {link.depth} | Source: {link.source_page}")
        
        report.append("")
        report.append("=" * 70)
        
        return '\n'.join(report)
    
    def save_state(self, filename: str = 'discovery_state.json'):
        """Save discovery state for resumption."""
        state = {
            'base_url': self.base_url,
            'visited': list(self.visited),
            'pdfs': self.discovered_pdfs,
            'links': [asdict(l) for l in self.discovered_links]
        }
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"\n💾 Discovery state saved to {filename}")


def main():
    """CLI entry point for discovery."""
    import sys
    
    # Allow URL override from command line
    start_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.justice.gov/epstein"
    
    print(f"🔍 Starting discovery from: {start_url}")
    print("   (This uses CLI tools - curl, htmlq - not the model)")
    print()
    
    tool = DiscoveryTool(start_url, max_depth=2)
    
    # Initial crawl
    result = tool.discover_from_page(start_url, depth=0)
    
    print(f"\n{'='*70}")
    print("INITIAL CRAWL COMPLETE")
    print(f"{'='*70}")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Page title: {result['page_title']}")
        print(f"PDFs found: {result['pdf_count']}")
        print(f"Nav links: {result['nav_link_count']}")
    elif result['status'] == 'blocked':
        print(f"⚠️  {result['reason']}")
    
    # Generate and display report
    report = tool.generate_discovery_report()
    print("\n" + report)
    
    # Save state
    tool.save_state('reference/discovery_state.json')
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Review the NAVIGATION LINKS above")
    print("2. Select promising links to crawl next")
    print("3. Run: python3 scripts/discovery_agent.py <SELECTED_URL>")
    print("4. Or let the model review and select links")
    print()
    print("To download discovered PDFs:")
    print("   python3 scripts/download_from_discovery.py")


if __name__ == "__main__":
    main()
