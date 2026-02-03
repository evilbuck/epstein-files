#!/bin/bash

# Epstein File Downloader
# 
# IMPORTANT: This script uses curl which CANNOT execute JavaScript.
# The justice.gov site uses Akamai protection that requires JavaScript.
# 
# For reliable downloads, use the Playwright version instead:
#   python3 scripts/download_playwright.py
#
# This curl-based version is kept for reference but will likely fail
# due to Akamai's anti-bot protection.

# Create reference directory if it doesn't exist
mkdir -p reference

echo "================================================================"
echo "⚠️  WARNING: This script uses curl which cannot bypass Akamai"
echo "   JavaScript protection on justice.gov"
echo ""
echo "   For reliable downloads, use:"
echo "   python3 scripts/download_playwright.py"
echo "================================================================"
echo ""

# Fetch initial page with redirect handling
echo "Fetching initial page from justice.gov/epstein..."
initial_page=$(curl -s -L "https://www.justice.gov/epstein")

# Extract redirect URL using sed with proper escaping
redirect_url=$(echo "$initial_page" | sed -n 's/.*URL=\([^"]*\).*/\1/p')

if [ -z "$redirect_url" ]; then
    echo "Error: Could not extract redirect URL from initial page"
    echo "   This is likely due to Akamai blocking the request."
    exit 1
fi

echo "Redirect URL found: $redirect_url"

# Construct full URL if redirect is relative
if [[ "$redirect_url" == /* ]]; then
    redirect_url="https://www.justice.gov$redirect_url"
    echo "Full redirect URL: $redirect_url"
fi

# Follow redirect to get actual content
echo "Following redirect..."
actual_page=$(curl -s -L "$redirect_url")

# Check if we got Akamai challenge page (contains JavaScript challenge)
if echo "$actual_page" | grep -q "bm-verify\|akamai\|window.location"; then
    echo ""
    echo "❌ ERROR: Akamai JavaScript challenge detected"
    echo ""
    echo "The server is returning a JavaScript challenge that curl cannot solve."
    echo ""
    echo "👉 SOLUTION: Use the Playwright-based downloader instead:"
    echo "   python3 scripts/download_playwright.py"
    echo ""
    echo "Playwright runs a real browser that can execute JavaScript and"
    echo "bypass Akamai's protection automatically."
    echo ""
    exit 1
fi

# Extract PDF links using htmlq (install with: brew install htmlq)
pdf_links=$(echo "$actual_page" | htmlq -a href 'a' | grep -i '\.pdf$' | sort -u)

# Check if page content is empty (Akamai blocking)
if [ -z "$actual_page" ] || [ "${#actual_page}" -lt 100 ]; then
    echo ""
    echo "❌ ERROR: Empty response from server"
    echo ""
    echo "The server returned empty content, likely due to:"
    echo "  1. Akamai blocking curl-based requests"
    echo "  2. JavaScript challenge that requires a real browser"
    echo ""
    echo "👉 SOLUTION: Use the Playwright-based downloader:"
    echo "   python3 scripts/download_playwright.py"
    echo ""
    exit 1
fi

if [ -z "$pdf_links" ]; then
    echo "Error: No PDF links found in the page content"
    # Save page content for debugging
    echo "$actual_page" > reference/debug_page.html
    echo "Debug: Saved page content to reference/debug_page.html"
    echo "   (Size: ${#actual_page} bytes)"
    exit 1
fi

echo "Found $(echo "$pdf_links" | wc -l) PDF links"

# Download each PDF
while IFS= read -r link; do
    filename=$(basename "$link")
    echo "Downloading: $filename"
    curl -s -L -o "reference/$filename" "$link"
    
    if [ $? -eq 0 ]; then
        echo "✓ Successfully downloaded: $filename"
    else
        echo "✗ Failed to download: $filename"
    fi
done < <(echo "$pdf_links")

# Clean up temporary files
rm -f pdf_links.txt

echo "Download complete. Files stored in reference/ directory"
