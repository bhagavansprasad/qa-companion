"""Main entry point for PDF Knowledge Base system."""

import sys
from pathlib import Path
from config import Config
from src.ingestion.pipeline import IngestionPipeline
from src.utils.file_utils import list_and_validate_pdfs


def create_directories():
    """Create required directories if they don't exist."""
    directories = [
        Config.PDF_DATA_PATH,
        Config.IMAGE_OUTPUT_PATH,
        Config.PROCESSED_DATA_PATH,
        Config.LOG_DIR,
        Config.CHROMA_DB_PATH
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def list_pdfs_only():
    """List PDF files without processing them."""
    print("PDF KNOWLEDGE BASE - FILE LISTING")
    print("=" * 50)
    
    pdf_files = list_and_validate_pdfs(Config.PDF_DATA_PATH)
    
    if pdf_files:
        readable_count = sum(1 for f in pdf_files if f['is_readable'])
        print(f"Summary: Found {readable_count} readable PDF files out of {len(pdf_files)} total files.")
    
    return pdf_files


def run_ingestion():
    """Run the full ingestion pipeline."""
    pipeline = IngestionPipeline()
    pipeline.run_ingestion()


def show_help():
    """Show help information."""
    help_text = """
PDF Knowledge Base System

Usage:
    python main.py [command]

Commands:
    list        List all PDF files in the data/pdfs directory
    ingest      Run the full ingestion pipeline
    help        Show this help message

Examples:
    python main.py list     # List PDF files only
    python main.py ingest   # Process all PDF files
    python main.py          # Same as 'list' (default)
    """
    print(help_text)


def main():
    """Main function."""
    # Ensure directories exist
    create_directories()
    
    # Get command line argument
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "list"
    
    if command == "list":
        list_documents_only()
    elif command == "ingest":
        run_ingestion()
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python main.py help' for usage information.")


if __name__ == "__main__":
    main()