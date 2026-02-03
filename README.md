# Epstein File Downloader & Organizer

## Installation
1. Install required tools:
   `brew install htmlq`

## Usage
1. Make scripts executable:
   `chmod +x scripts/*.sh`

2. Run the download script:
   `bash scripts/download.sh`
   - This will download all PDFs from justice.gov/epstein to reference/

3. Run the processing script:
   `bash scripts/process.sh`
   - This will organize files into data/epstein_pdfs/, data/epstein_text/, and data/epstein_images/

4. View organized files:
   - PDFs: data/epstein_pdfs/
   - Text files: data/epstein_text/
   - Images: data/epstein_images/

5. View index and summary:
   - data/index.txt (list of all files)
   - data/summary.txt (file count)

6. View tags and metadata:
   - data/tags.txt (extracted dates)
   - data/metadata.txt (file dates)