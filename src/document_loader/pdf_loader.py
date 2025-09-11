"""PDF document loader with text and image extraction using PyMuPDF and LangChain."""

import os
import fitz  # PyMuPDF
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from pytesseract import image_to_data, Output
from PIL import Image
from pathlib import Path
from typing import List, Dict
from config import Config


class PDFLoader:
    """PDF document loader for text and image extraction."""
    
    def __init__(self):
        self.config = Config
    
    def load_pdf(self, pdf_path: str) -> Dict:
        """
        Load and extract content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted documents and metadata
        """
        print(f"  - Loading PDF: {Path(pdf_path).name}")
        
        # Extract text using LangChain PyPDFLoader
        text_documents = self._load_text_with_pypdf(pdf_path)
        
        print(f"  - Extracted text from {len(text_documents)} pages")
        
        # Extract images and run OCR
        image_documents = self._load_images_with_ocr(pdf_path)
        
        print(f"  - Extracted and processed {len(image_documents)} images with OCR")
        
        # Combine all documents
        all_documents = text_documents + image_documents
        
        return {
            'file_path': pdf_path,
            'file_name': Path(pdf_path).stem,
            'documents': all_documents,
            'text_document_count': len(text_documents),
            'image_document_count': len(image_documents),
            'total_document_count': len(all_documents)
        }
    
    def _load_text_with_pypdf(self, pdf_path: str) -> List[Document]:
        """
        Extract text using LangChain PyPDFLoader.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of LangChain Document objects with text content
        """
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            docs = []
            max_pages = self.config.MAX_PAGES_PER_PDF
            pages_to_process = documents[:max_pages] if max_pages else documents
            
            for i, doc in enumerate(pages_to_process):
                if doc.page_content.strip():  # Only add pages with content
                    docs.append(
                        Document(
                            page_content=doc.page_content,
                            metadata={
                                "source": pdf_path,
                                "page": i + 1,
                                "type": "text",
                                "char_count": len(doc.page_content)
                            }
                        )
                    )
            
            return docs
            
        except Exception as e:
            print(f"    Warning: Failed to extract text from PDF: {str(e)}")
            return []
    
    def _load_images_with_ocr(self, pdf_path: str) -> List[Document]:
        """
        Extract images from PDF and run OCR with Tesseract.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of LangChain Document objects with OCR content
        """
        try:
            # Setup image output directory
            output_folder = Path(self.config.IMAGE_OUTPUT_PATH)
            output_folder.mkdir(parents=True, exist_ok=True)
            
            pdf_name = Path(pdf_path).stem
            doc = fitz.open(pdf_path)
            docs = []
            
            max_pages = self.config.MAX_PAGES_PER_PDF
            num_pages_to_process = min(max_pages, len(doc)) if max_pages else len(doc)
            
            for page_num in range(num_pages_to_process):
                page = doc[page_num]
                images = page.get_images(full=True)
                
                for img_index, img in enumerate(images, start=1):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        # Filter out small images (icons/logos)
                        if (pix.width < self.config.MIN_IMAGE_WIDTH or 
                            pix.height < self.config.MIN_IMAGE_HEIGHT):
                            pix = None
                            continue
                        
                        # Save image
                        img_filename = f"{pdf_name}_page-{page_num+1}_img-{img_index}.png"
                        img_path = output_folder / img_filename
                        
                        if pix.n - pix.alpha < 4:  # RGB or Gray
                            pix.save(str(img_path))
                        else:  # CMYK conversion
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                            pix.save(str(img_path))
                        pix = None
                        
                        # Run OCR with Tesseract
                        ocr_text = self._run_ocr_on_image(img_path)
                        
                        if ocr_text.strip():  # Only add if OCR found text
                            docs.append(
                                Document(
                                    page_content=ocr_text,
                                    metadata={
                                        "source": pdf_path,
                                        "page": page_num + 1,
                                        "image_path": str(img_path),
                                        "type": "image_ocr",
                                        "char_count": len(ocr_text)
                                    }
                                )
                            )
                        else:
                            # Remove image file if no useful OCR text found
                            if img_path.exists():
                                img_path.unlink()
                    
                    except Exception as e:
                        print(f"    Warning: Failed to process image {img_index} on page {page_num + 1}: {str(e)}")
                        continue
            
            doc.close()
            return docs
            
        except Exception as e:
            print(f"    Warning: Failed to extract images from PDF: {str(e)}")
            return []
    
    def _run_ocr_on_image(self, img_path: Path, min_confidence: int = 50) -> str:
        """
        Run OCR on an image using Tesseract.
        
        Args:
            img_path: Path to the image file
            min_confidence: Minimum confidence threshold for OCR text
            
        Returns:
            Extracted text from the image
        """
        try:
            # Run OCR with detailed output
            data = image_to_data(Image.open(img_path), output_type=Output.DICT)
            
            # Filter words by confidence threshold
            words = [
                word.strip()
                for word, conf in zip(data["text"], data["conf"])
                if int(conf) > min_confidence and word.strip()
            ]
            
            return " ".join(words)
            
        except Exception as e:
            print(f"    Warning: OCR failed for image {img_path}: {str(e)}")
            return ""
    
    def get_pdf_info(self, pdf_path: str) -> Dict:
        """
        Get basic information about a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        try:
            doc = fitz.open(pdf_path)
            
            info = {
                'page_count': len(doc),
                'metadata': doc.metadata,
                'is_encrypted': doc.needs_pass,
                'file_size': os.path.getsize(pdf_path)
            }
            
            doc.close()
            return info
            
        except Exception as e:
            print(f"    Warning: Failed to get PDF info: {str(e)}")
            return {}


def main():
    """Test the PDF loader."""
    from config import Config
    
    # Create directories
    Path(Config.IMAGE_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
    
    loader = PDFLoader()
    
    # Test with available PDFs
    pdf_dir = Path(Config.PDF_DATA_PATH)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if pdf_files:
        test_pdf = pdf_files[0]
        print(f"Testing PDF loader with: {test_pdf}")
        
        # Load PDF
        result = loader.load_pdf(str(test_pdf))
        
        # Show results
        print(f"\nResults for {result['file_name']}:")
        print(f"Text documents: {result['text_document_count']}")
        print(f"Image documents: {result['image_document_count']}")
        print(f"Total documents: {result['total_document_count']}")
        
        # Show sample documents
        if result['documents']:
            print(f"\nFirst few documents:")
            for i, doc in enumerate(result['documents'][:3]):
                print(f"\nDocument {i+1}:")
                print(f"  Type: {doc.metadata['type']}")
                print(f"  Page: {doc.metadata['page']}")
                if doc.metadata['type'] == 'image_ocr':
                    print(f"  Image: {doc.metadata['image_path']}")
                print(f"  Content preview: {doc.page_content[:200]}...")
    else:
        print("No PDF files found in data/pdfs directory")


if __name__ == "__main__":
    main()
