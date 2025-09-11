"""Main ingestion pipeline for processing document files."""

import time
from typing import List, Dict
from config import Config
from src.utils.file_utils import list_and_validate_files


class IngestionPipeline:
    """Main pipeline for ingesting document files into the knowledge base."""
    
    def __init__(self):
        self.config = Config
        self.processed_files = []
        self.failed_files = []
    
    def run_ingestion(self, directory_path: str = None, pattern: str = "*.pdf", 
                     expected_extensions: List[str] = None, file_type: str = "document"):
        """
        Run the complete ingestion pipeline.
        
        Args:
            directory_path: Path to document directory (uses config default if None)
            pattern: File pattern to match (default: "*.pdf")
            expected_extensions: List of expected file extensions (default: ['.pdf'])
            file_type: Type of files for display purposes (default: "document")
        """
        directory = directory_path or self.config.PDF_DATA_PATH
        extensions = expected_extensions or ['.pdf']
        
        print("=" * 80)
        print(f"{file_type.upper()} KNOWLEDGE BASE INGESTION PIPELINE")
        print("=" * 80)
        
        # Step 1: List and validate document files
        document_files = self.list_document_files(directory, pattern, extensions, file_type)
        
        if not document_files:
            print(f"No valid {file_type} files found. Exiting.")
            return
        
        # Step 2: Confirm processing
        if not self.confirm_processing(document_files, file_type):
            print("Processing cancelled by user.")
            return
        
        # Step 3: Process each document file
        self.process_document_files(document_files, file_type)
        
        # Step 4: Show final summary
        self.show_final_summary()
    
    def list_document_files(self, directory_path: str, pattern: str, 
                           expected_extensions: List[str], file_type: str) -> List[Dict]:
        """
        List and validate all document files matching the pattern.
        
        Args:
            directory_path: Path to the document directory
            pattern: File pattern to match
            expected_extensions: List of expected file extensions
            file_type: Type of files for display purposes
            
        Returns:
            List of validated document file information
        """
        print(f"Step 1: Discovering {file_type} files...")
        print()
        
        document_files = list_and_validate_files(
            directory_path=directory_path,
            pattern=pattern,
            expected_extensions=expected_extensions,
            file_type=file_type
        )
        
        return document_files
    
    def confirm_processing(self, doc_files: List[Dict], file_type: str) -> bool:
        """
        Ask user for confirmation before processing.
        
        Args:
            doc_files: List of document file information
            file_type: Type of files for display purposes
            
        Returns:
            True if user confirms, False otherwise
        """
        readable_files = [f for f in doc_files if f['is_readable']]
        
        if not readable_files:
            print(f"No readable {file_type} files found.")
            return False
        
        print("Step 2: Processing confirmation")
        print(f"Ready to process {len(readable_files)} {file_type} files.")
        
        while True:
            response = input("Do you want to proceed? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    def process_document_files(self, doc_files: List[Dict], file_type: str):
        """
        Process each document file.
        
        Args:
            doc_files: List of document file information
            file_type: Type of files for display purposes
        """
        print(f"\nStep 3: Processing {file_type} files...")
        print("-" * 50)
        
        readable_files = [f for f in doc_files if f['is_readable']]
        
        for i, file_info in enumerate(readable_files, 1):
            print(f"\nProcessing {i}/{len(readable_files)}: {file_info['name']}")
            
            try:
                # Process based on file type/extension
                self.process_single_file(file_info)
                
                print(f"  ✓ Successfully processed: {file_info['name']}")
                self.processed_files.append(file_info)
                
            except Exception as e:
                print(f"  ✗ Failed to process: {file_info['name']}")
                print(f"    Error: {str(e)}")
                self.failed_files.append({
                    'file_info': file_info,
                    'error': str(e)
                })
    
    def process_single_file(self, file_info: Dict):
        """
        Process a single file based on its type.
        
        Args:
            file_info: Dictionary containing file information
        """
        file_extension = file_info.get('extension', '').lower()
        
        print("  - Loading document...")
        time.sleep(0.5)  # Remove this in actual implementation
        
        if file_extension == '.pdf':
            self.process_pdf_file(file_info)
        elif file_extension in ['.txt', '.md']:
            self.process_text_file(file_info)
        elif file_extension in ['.docx', '.doc']:
            self.process_word_file(file_info)
        else:
            print(f"  - Unsupported file type: {file_extension}")
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def process_pdf_file(self, file_info: Dict):
        """Process a PDF file."""
        print("  - Extracting text and images from PDF...")
        time.sleep(0.5)  # Remove this in actual implementation
        
        print("  - Processing with OCR...")
        time.sleep(0.5)  # Remove this in actual implementation
        
        self.common_processing_steps()
    
    def process_text_file(self, file_info: Dict):
        """Process a text file."""
        print("  - Reading text content...")
        time.sleep(0.3)  # Remove this in actual implementation
        
        self.common_processing_steps()
    
    def process_word_file(self, file_info: Dict):
        """Process a Word document."""
        print("  - Extracting text from Word document...")
        time.sleep(0.4)  # Remove this in actual implementation
        
        self.common_processing_steps()
    
    def common_processing_steps(self):
        """Common processing steps for all file types."""
        print("  - Chunking text...")
        time.sleep(0.3)  # Remove this in actual implementation
        
        print("  - Generating embeddings...")
        time.sleep(0.7)  # Remove this in actual implementation
        
        print("  - Storing in vector database...")
        time.sleep(0.3)  # Remove this in actual implementation
    
    def show_final_summary(self):
        """Show the final processing summary."""
        print("\n" + "=" * 80)
        print("INGESTION SUMMARY")
        print("=" * 80)
        
        print(f"Successfully processed: {len(self.processed_files)} files")
        print(f"Failed to process: {len(self.failed_files)} files")
        
        if self.processed_files:
            print("\nSuccessfully processed files:")
            for file_info in self.processed_files:
                print(f"  ✓ {file_info['name']} ({file_info['size_mb']} MB)")
        
        if self.failed_files:
            print("\nFailed files:")
            for failed in self.failed_files:
                print(f"  ✗ {failed['file_info']['name']} - {failed['error']}")
        
        total_size = sum(f['size_mb'] for f in self.processed_files)
        print(f"\nTotal processed data: {total_size:.2f} MB")
        print("Ingestion pipeline completed.")


# Convenience functions for common use cases
def run_pdf_ingestion(directory_path: str = None):
    """Convenience function to run PDF ingestion."""
    pipeline = IngestionPipeline()
    pipeline.run_ingestion(
        directory_path=directory_path,
        pattern="*.pdf",
        expected_extensions=['.pdf'],
        file_type="PDF"
    )


def run_text_ingestion(directory_path: str = None):
    """Convenience function to run text file ingestion."""
    pipeline = IngestionPipeline()
    pipeline.run_ingestion(
        directory_path=directory_path,
        pattern="*.txt",
        expected_extensions=['.txt', '.md'],
        file_type="text"
    )


def run_document_ingestion(directory_path: str = None):
    """Convenience function to run mixed document ingestion."""
    pipeline = IngestionPipeline()
    pipeline.run_ingestion(
        directory_path=directory_path,
        pattern="*.*",
        expected_extensions=['.pdf', '.txt', '.md', '.docx', '.doc'],
        file_type="document"
    )


def main():
    """Main entry point for the ingestion pipeline."""
    # Default to PDF ingestion for backward compatibility
    run_pdf_ingestion()


if __name__ == "__main__":
    main()