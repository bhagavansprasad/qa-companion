"""OCR processor for image text extraction using Tesseract."""

import os
from pathlib import Path
from typing import Dict, List
from pytesseract import image_to_data, Output
from PIL import Image


class OCRProcessor:
    """OCR processor for extracting text from images using Tesseract."""
    
    def __init__(self, min_confidence: int = 50):
        """
        Initialize OCR processor.
        
        Args:
            min_confidence: Minimum confidence threshold for OCR text
        """
        self.min_confidence = min_confidence
    
    def process_image(self, image_path: str) -> Dict:
        """
        Process a single image with OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing OCR results
        """
        try:
            image_path_obj = Path(image_path)
            
            if not image_path_obj.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Run OCR with detailed output
            data = image_to_data(Image.open(image_path), output_type=Output.DICT)
            
            # Extract words with confidence above threshold
            valid_words = []
            word_details = []
            
            for i, (word, conf) in enumerate(zip(data["text"], data["conf"])):
                if int(conf) > self.min_confidence and word.strip():
                    clean_word = word.strip()
                    valid_words.append(clean_word)
                    word_details.append({
                        'word': clean_word,
                        'confidence': int(conf),
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })
            
            extracted_text = " ".join(valid_words)
            
            return {
                'image_path': str(image_path),
                'extracted_text': extracted_text,
                'word_count': len(valid_words),
                'char_count': len(extracted_text),
                'word_details': word_details,
                'has_text': len(valid_words) > 0,
                'average_confidence': sum(w['confidence'] for w in word_details) / len(word_details) if word_details else 0
            }
            
        except Exception as e:
            return {
                'image_path': str(image_path),
                'extracted_text': "",
                'word_count': 0,
                'char_count': 0,
                'word_details': [],
                'has_text': False,
                'average_confidence': 0,
                'error': str(e)
            }
    
    def process_images(self, image_paths: List[str]) -> List[Dict]:
        """
        Process multiple images with OCR.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of OCR result dictionaries
        """
        results = []
        
        for image_path in image_paths:
            print(f"  - Processing OCR for: {Path(image_path).name}")
            result = self.process_image(image_path)
            results.append(result)
        
        return results
    
    def filter_useful_images(self, ocr_results: List[Dict], 
                           min_words: int = 3, min_chars: int = 10) -> List[Dict]:
        """
        Filter OCR results to keep only images with meaningful text.
        
        Args:
            ocr_results: List of OCR result dictionaries
            min_words: Minimum number of words required
            min_chars: Minimum number of characters required
            
        Returns:
            Filtered list of useful OCR results
        """
        useful_results = []
        
        for result in ocr_results:
            if (result['has_text'] and 
                result['word_count'] >= min_words and 
                result['char_count'] >= min_chars):
                useful_results.append(result)
            else:
                # Remove image file if it doesn't contain useful text
                image_path = Path(result['image_path'])
                if image_path.exists():
                    try:
                        image_path.unlink()
                        print(f"  - Removed image with no useful text: {image_path.name}")
                    except Exception:
                        pass
        
        return useful_results


def main():
    """Test the OCR processor."""
    from config import Config
    
    processor = OCRProcessor(min_confidence=50)
    
    # Find image files in the images directory
    image_dir = Path(Config.IMAGE_OUTPUT_PATH)
    
    if image_dir.exists():
        image_files = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg"))
        
        if image_files:
            print(f"Testing OCR processor with {len(image_files)} images")
            
            # Process all images
            results = processor.process_images([str(img) for img in image_files])
            
            # Show results
            for result in results:
                print(f"\nImage: {Path(result['image_path']).name}")
                print(f"Words found: {result['word_count']}")
                print(f"Avg confidence: {result['average_confidence']:.1f}")
                if result['extracted_text']:
                    print(f"Text preview: {result['extracted_text'][:100]}...")
                if 'error' in result:
                    print(f"Error: {result['error']}")
            
            # Filter useful images
            useful_results = processor.filter_useful_images(results)
            print(f"\nUseful images with text: {len(useful_results)}/{len(results)}")
            
        else:
            print("No image files found in images directory")
    else:
        print("Images directory not found")


if __name__ == "__main__":
    main()
