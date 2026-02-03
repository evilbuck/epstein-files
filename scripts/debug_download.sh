#!/bin/bash

# Debug script for justice.gov/epstein download issues
echo "=== DEBUGGING EPSTEIN FILE DOWNLOAD ===\n"

# 1. Check curl version
echo "1. Checking curl version..."
curl --version

echo "\n2. Fetching initial page with verbose output..."
initial_page=$(curl -v -L "https://www.justice.gov/epstein" 2>&1)

# Save raw response for analysis
echo "$initial_page" > debug_initial_response.txt
echo "Saved raw response to debug_initial_response.txt"

# Extract redirect URL
echo "\n3. Extracting redirect URL..."
redirect_url=$(echo "$initial_page" | sed -n 's/.*URL=\([^"]*\).*/\1/p')

if [ -n "$redirect_url" ]; then
    echo "Redirect URL found: $redirect_url"
    
    # Follow redirect with verbose output
    echo "\n4. Following redirect with verbose output..."
    actual_page=$(curl -v -L "$redirect_url" 2>&1)
    echo "$actual_page" > debug_redirected_response.txt
    echo "Saved redirected response to debug_redirected_response.txt"
    
    # Look for PDF links in the redirected content
    echo "\n5. Searching for PDF links in redirected content..."
    pdf_links=$(echo "$actual_page" | grep -oE 'https://[^"[:space:]]+\.pdf' | sort -u)
    
    if [ -n "$pdf_links" ]; then
        echo "Found $(echo "$pdf_links" | wc -l) PDF links:"
        echo "$pdf_links"
    else
        echo "No PDF links found in redirected content."
        echo "\n6. Searching for any links containing 'pdf'..."
        grep -i 'pdf' debug_redirected_response.txt | head -20
    fi
else
    echo "No redirect URL found in initial response."
    echo "\n6. Searching for any redirect patterns in initial response..."
    grep -i 'redirect\|url\|refresh' debug_initial_response.txt | head -20
fi

echo "\n7. Checking for JavaScript redirects..."
grep -i 'window.location' debug_initial_response.txt | head -10

echo "\nDebug complete. Check debug_initial_response.txt and debug_redirected_response.txt for details."