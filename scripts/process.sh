#!/bin/bash

# Create reference directory if it doesn't exist
mkdir -p reference

# Create data directory for organized files
mkdir -p data

# Create subdirectories for different file types
mkdir -p data/epstein_pdfs
mkdir -p data/epstein_text
mkdir -p data/epstein_images

# Function to organize files by type
organize_files() {
    local file_type=$1
    local file_path=$2

    case $file_type in
        *.pdf)
            echo "Moving PDF to data/epstein_pdfs/"
            mv "$file_path" data/epstein_pdfs/ || echo "Failed to move PDF: $file_path"
            ;;
        *.txt)
            echo "Moving text file to data/epstein_text/"
            mv "$file_path" data/epstein_text/ || echo "Failed to move text file: $file_path"
            ;;
        *.jpg|*.jpeg|*.png|*.gif)
            echo "Moving image to data/epstein_images/"
            mv "$file_path" data/epstein_images/ || echo "Failed to move image: $file_path"
            ;;
        *)
            echo "Unsupported file type: $file_path"
            ;;
    esac
}

# Process all files in reference directory
if [ -d "reference/" ]; then
    echo "Processing files in reference directory..."
    for file in reference/*; do
        if [ -f "$file" ]; then
            file_type=$(file -b --mime-type "$file")
            case $file_type in
                application/pdf)
                    organize_files "*.pdf" "$file"
                    ;;
                text/plain)
                    organize_files "*.txt" "$file"
                    ;;
                image/*)
                    organize_files "*.jpg" "$file"
                    ;;
                *)
                    echo "Unsupported file type: $file"
                    ;;
            esac
        fi
    done
    echo "File organization complete."
else
    echo "No files found in reference directory."
fi

# Create index file
echo "Creating index of organized files..."
find data -type f > data/index.txt

# Create summary report
echo "Generating summary report..."
find data -type f | wc -l > data/summary.txt

# Create tagging system
echo "Creating tagging system..."
find data -type f | xargs -I {} sh -c 'echo -n "{}" | grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}" | head -1 >> data/tags.txt'

# Create metadata file
echo "Creating metadata file..."
find data -type f | xargs -I {} sh -c 'echo -n "{}" | grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}" | head -1' > data/metadata.txt