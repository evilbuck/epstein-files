#!/bin/bash

echo "Debug script for justice.gov/epstein"

# Get the initial page
echo "Getting initial page..."
initial_page=$(curl -s -L "https://www.justice.gov/epstein")

# Save the page to a file for inspection
echo "$initial_page" > debug_page.html

echo "Page saved to debug_page.html"

# Try to extract the redirect URL
echo "Extracting redirect URL..."

# Look for the meta refresh tag
echo "Looking for meta refresh tag..."
echo "$initial_page" | grep -i "meta refresh"

# Try different patterns
echo "Trying different patterns..."
echo "$initial_page" | grep -o "URL=[^']*"
echo "$initial_page" | grep -o "URL=[^\"']*"
echo "$initial_page" | grep -o "URL=[^']*bm-verify"

# Try to find any URL with bm-verify
echo "Looking for bm-verify..."
echo "$initial_page" | grep -o "bm-verify=[^\"']*"

echo "Debug complete."