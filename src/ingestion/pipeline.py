"""Main ingestion pipeline for processing document files."""

from typing import List, Dict
from pathlib import Path
from config import Config
from src.utils.file_utils import list_and_validate_files
from src.document_loader.pdf_loader import PDFLoader


class IngestionPipeline:
    """Main pipeline for ingesting document files into the knowledge base."""
    
    def __init__(self):
        self.config = Config
        self.processed_files = []
        self.failed_files = []
        # Initialize processors
        self.pdf_loader = PDFLoader()
    
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
            response = input("Do you want to proceed? (Y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                return True
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
                processing_result = self.process_single_file(file_info)
                
                print(f"  ✓ Successfully processed: {file_info['name']}")
                
                # Store both original file info and processing results
                processed_file_data = {
                    'file_info': file_info,
                    'processing_result': processing_result
                }
                self.processed_files.append(processed_file_data)
                
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
        
        if file_extension == '.pdf':
            return self.process_pdf_file(file_info)
        elif file_extension in ['.txt', '.md']:
            return self.process_text_file(file_info)
        elif file_extension in ['.docx', '.doc']:
            return self.process_word_file(file_info)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def process_pdf_file(self, file_info: Dict):
        """Process a PDF file using PDFLoader."""
        try:
            # Load PDF with text and image extraction
            pdf_result = self.pdf_loader.load_pdf(file_info['path'])
            
            # Save the extracted documents info to processed folder
            self.save_processed_data(file_info, pdf_result)
            
            return pdf_result
            
        except Exception as e:
            raise Exception(f"PDF processing failed: {str(e)}")
    
    def process_text_file(self, file_info: Dict):
        """Process a text file."""
        print("  - Reading text content...")
        # TODO: Implement text file processing
        raise NotImplementedError("Text file processing not yet implemented")
    
    def process_word_file(self, file_info: Dict):
        """Process a Word document."""
        print("  - Extracting text from Word document...")
        # TODO: Implement Word document processing
        raise NotImplementedError("Word document processing not yet implemented")
    
    def save_processed_data(self, file_info: Dict, pdf_result: Dict):
        """
        Save processed data to the processed folder.
        This is temporary until we implement vector storage.
        
        Args:
            file_info: Original file information
            pdf_result: Result from PDF processing
        """
        import json
        
        processed_dir = Path(self.config.PROCESSED_DATA_PATH)
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a summary file with processing results
        file_name = file_info['name'].replace('.pdf', '')
        summary_file = processed_dir / f"{file_name}_summary.json"
        
        summary_data = {
            'original_file': file_info['path'],
            'file_name': pdf_result['file_name'],
            'processing_timestamp': str(Path(file_info['path']).stat().st_mtime),
            'text_documents': pdf_result['text_document_count'],
            'image_documents': pdf_result['image_document_count'],
            'total_documents': pdf_result['total_document_count'],
            'documents_preview': []
        }
        
        # Add preview of first few documents
        for i, doc in enumerate(pdf_result['documents'][:5]):
            doc_preview = {
                'document_index': i,
                'type': doc.metadata['type'],
                'page': doc.metadata['page'],
                'char_count': doc.metadata.get('char_count', 0),
                'content_preview': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            }
            if doc.metadata['type'] == 'image_ocr':
                doc_preview['image_path'] = doc.metadata.get('image_path', '')
            
            summary_data['documents_preview'].append(doc_preview)
        
        # Save summary to JSON file
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        print(f"  - Saved processing summary to: {summary_file}")
    
    def show_final_summary(self):
        """Show the final processing summary."""
        print("\n" + "=" * 80)
        print("INGESTION SUMMARY")
        print("=" * 80)
        
        print(f"Successfully processed: {len(self.processed_files)} files")
        print(f"Failed to process: {len(self.failed_files)} files")
        
        if self.processed_files:
            print("\nSuccessfully processed files:")
            for processed_item in self.processed_files:
                # Handle both old format (just file_info) and new format (dict with file_info and processing_result)
                if isinstance(processed_item, dict) and 'file_info' in processed_item:
                    # New format
                    file_info = processed_item['file_info']
                    processing_result = processed_item.get('processing_result', {})
                    
                    if isinstance(processing_result, dict) and 'total_document_count' in processing_result:
                        # PDF processing result
                        doc_count = processing_result['total_document_count']
                        print(f"  ✓ {file_info['name']} ({file_info['size_mb']} MB) - {doc_count} documents extracted")
                    else:
                        # Other file types
                        print(f"  ✓ {file_info['name']} ({file_info['size_mb']} MB)")
                else:
                    # Old format (just file_info dict)
                    file_info = processed_item
                    print(f"  ✓ {file_info['name']} ({file_info['size_mb']} MB)")
        
        if self.failed_files:
            print("\nFailed files:")
            for failed in self.failed_files:
                print(f"  ✗ {failed['file_info']['name']} - {failed['error']}")
        
        # Calculate totals handling both old and new formats
        total_size = 0
        total_documents = 0
        
        for processed_item in self.processed_files:
            if isinstance(processed_item, dict) and 'file_info' in processed_item:
                # New format
                total_size += processed_item['file_info']['size_mb']
                processing_result = processed_item.get('processing_result', {})
                if isinstance(processing_result, dict):
                    total_documents += processing_result.get('total_document_count', 0)
            else:
                # Old format
                total_size += processed_item['size_mb']
        
        print(f"\nTotal processed data: {total_size:.2f} MB")
        if total_documents > 0:
            print(f"Total documents extracted: {total_documents}")
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