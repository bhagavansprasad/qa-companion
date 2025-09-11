"""Command Line Interface for Document Knowledge Base."""

import argparse
from pathlib import Path
from config import Config
from src.ingestion.pipeline import IngestionPipeline
from src.utils.file_utils import list_and_validate_documents


def setup_directories():
    """Setup required directories."""
    directories = [
        Config.PDF_DATA_PATH,
        Config.IMAGE_OUTPUT_PATH,
        Config.PROCESSED_DATA_PATH,
        Config.LOG_DIR,
        Config.CHROMA_DB_PATH
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def cmd_list_documents(args):
    """List document files command."""
    directory = args.directory or Config.PDF_DATA_PATH
    
    print(f"Listing document files in: {directory}")
    print("=" * 60)
    
    doc_files = list_and_validate_documents(directory)
    
    if doc_files:
        readable_count = sum(1 for f in doc_files if f['is_readable'])
        print(f"\nReady to process: {readable_count} files")
    else:
        print("No document files found.")


def cmd_ingest_documents(args):
    """Ingest document files command."""
    directory = args.directory or Config.PDF_DATA_PATH
    
    pipeline = IngestionPipeline()
    pipeline.run_ingestion(directory)


def cmd_show_config(args):
    """Show current configuration."""
    print("DOCUMENT KNOWLEDGE BASE CONFIGURATION")
    print("=" * 40)
    print(f"App Name: {Config.APP_NAME}")
    print(f"Debug Mode: {Config.DEBUG}")
    print(f"Log Level: {Config.LOG_LEVEL}")
    print()
    print("Paths:")
    print(f"  Document Data: {Config.PDF_DATA_PATH}")
    print(f"  Images: {Config.IMAGE_OUTPUT_PATH}")
    print(f"  Processed: {Config.PROCESSED_DATA_PATH}")
    print(f"  Logs: {Config.LOG_DIR}")
    print(f"  ChromaDB: {Config.CHROMA_DB_PATH}")
    print()
    print("Processing Settings (Currently PDF-focused):")
    print(f"  Max Pages: {Config.MAX_PAGES_PER_PDF or 'All'}")
    print(f"  Min Image Size: {Config.MIN_IMAGE_WIDTH}x{Config.MIN_IMAGE_HEIGHT}")
    print(f"  Chunk Size: {Config.CHUNK_SIZE}")
    print(f"  Chunk Overlap: {Config.CHUNK_OVERLAP}")
    print()
    print("Models:")
    print(f"  Embedding Model: {Config.EMBEDDING_MODEL}")
    print(f"  Collection Name: {Config.COLLECTION_NAME}")
    print(f"  Retrieval K: {Config.RETRIEVAL_K}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Document Knowledge Base CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py list                    # List document files (currently PDF)
  python cli.py list -d /path/to/docs   # List documents in specific directory
  python cli.py ingest                  # Run ingestion pipeline
  python cli.py config                  # Show configuration
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List document files')
    list_parser.add_argument(
        '-d', '--directory',
        help=f'Directory to scan (default: {Config.PDF_DATA_PATH})'
    )
    list_parser.set_defaults(func=cmd_list_documents)
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest document files')
    ingest_parser.add_argument(
        '-d', '--directory',
        help=f'Directory to process (default: {Config.PDF_DATA_PATH})'
    )
    ingest_parser.set_defaults(func=cmd_ingest_documents)
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show configuration')
    config_parser.set_defaults(func=cmd_show_config)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup directories
    setup_directories()
    
    # Run the selected command
    args.func(args)


if __name__ == "__main__":
    main()