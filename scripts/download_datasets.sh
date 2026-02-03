#!/bin/bash
# Download all Epstein Data Sets

cd reference || exit 1

echo "📥 Downloading Epstein Data Sets from justice.gov..."
echo ""

# Download Data Sets 1-7 (zip files)
for i in {1..7}; do
    url="https://www.justice.gov/epstein/files/DataSet%20${i}.zip"
    output="DataSet_${i}.zip"
    
    if [ -f "$output" ]; then
        echo "✓ Data Set $i already exists ($(stat -f%z "$output" | awk '{print $1/1024/1024 " MB"}'))"
    else
        echo "⬇️  Downloading Data Set $i..."
        curl -L -o "$output" "$url" --progress-bar
        size=$(stat -f%z "$output" 2>/dev/null || echo "0")
        if [ "$size" -gt 1000 ]; then
            echo "  ✓ Downloaded ($(echo "$size" | awk '{print $1/1024/1024 " MB"}'))"
        else
            echo "  ⚠️  File may be empty or failed"
        fi
    fi
    echo ""
done

echo "📦 Download complete!"
echo ""
ls -lh DataSet_*.zip 2>/dev/null || echo "No files found"
