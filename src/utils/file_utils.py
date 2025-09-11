"""File utilities for document discovery and validation."""

import os
from pathlib import Path
from typing import List, Dict


def get_files(directory_path: str, pattern: str = "*.*") -> List[str]:
    """
    Get all files matching a pattern from a directory.
    
    Args:
        directory_path: Path to the directory containing files
        pattern: File pattern to match (default: "*.*")
        
    Returns:
        List of file paths
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Directory does not exist: {directory_path}")
        return []
    
    if not directory.is_dir():
        print(f"Path is not a directory: {directory_path}")
        return []
    
    # Find all files matching the pattern
    files = list(directory.glob(pattern))
    
    # Convert to strings and sort
    file_paths = [str(file_path) for file_path in files]
    file_paths.sort()
    
    return file_paths


def get_file_info(file_path: str, expected_extensions: List[str] = None) -> Dict:
    """
    Get information about a single file.
    
    Args:
        file_path: Path to the file
        expected_extensions: List of expected file extensions (e.g., ['.pdf', '.txt'])
        
    Returns:
        Dictionary with file information or None if invalid
    """
    try:
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            print(f"File does not exist: {file_path}")
            return None
        
        if not file_path_obj.is_file():
            print(f"Path is not a file: {file_path}")
            return None
        
        # Check file extension if expected extensions are provided
        if expected_extensions:
            if file_path_obj.suffix.lower() not in [ext.lower() for ext in expected_extensions]:
                print(f"File extension not in expected types {expected_extensions}: {file_path}")
                return None
        
        # Get file stats
        stat = file_path_obj.stat()
        
        file_info = {
            'path': str(file_path_obj),
            'name': file_path_obj.name,
            'extension': file_path_obj.suffix,
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': stat.st_mtime,
            'is_readable': os.access(file_path, os.R_OK)
        }
        
        return file_info
        
    except Exception as e:
        print(f"Error getting file info for {file_path}: {str(e)}")
        return None


def validate_files(file_paths: List[str], expected_extensions: List[str] = None) -> List[Dict]:
    """
    Validate files and get their info.
    
    Args:
        file_paths: List of file paths
        expected_extensions: List of expected file extensions (e.g., ['.pdf', '.txt'])
        
    Returns:
        List of dictionaries with file information
    """
    validated_files = []
    
    for file_path in file_paths:
        file_info = get_file_info(file_path, expected_extensions)
        if file_info:
            validated_files.append(file_info)
    
    return validated_files


def print_files_summary(files: List[Dict], file_type: str = "document"):
    """
    Print a summary of files found.
    
    Args:
        files: List of file info dictionaries
        file_type: Type of files for display purposes (e.g., "document", "PDF", "text")
    """
    if not files:
        print(f"No {file_type} files found.")
        return
    
    print(f"\nFound {len(files)} {file_type} files:")
    print("-" * 80)
    print(f"{'#':<3} {'Name':<40} {'Size (MB)':<10} {'Status':<10}")
    print("-" * 80)
    
    total_size = 0
    readable_count = 0
    
    for i, file_info in enumerate(files, 1):
        status = "OK" if file_info['is_readable'] else "ERROR"
        if file_info['is_readable']:
            readable_count += 1
            total_size += file_info['size_mb']
        
        print(f"{i:<3} {file_info['name']:<40} {file_info['size_mb']:<10} {status:<10}")
    
    print("-" * 80)
    print(f"Total readable files: {readable_count}/{len(files)}")
    print(f"Total size: {total_size:.2f} MB")
    print()


def list_and_validate_files(directory_path: str, pattern: str = "*.*", 
                           expected_extensions: List[str] = None, 
                           file_type: str = "document") -> List[Dict]:
    """
    Main function to list and validate files matching a pattern.
    
    Args:
        directory_path: Path to the directory
        pattern: File pattern to match (e.g., "*.pdf", "*.txt", "*.*")
        expected_extensions: List of expected file extensions (e.g., ['.pdf', '.txt'])
        file_type: Type of files for display purposes (e.g., "document", "PDF", "text")
        
    Returns:
        List of validated file information
    """
    print(f"Scanning directory: {directory_path}")
    
    # Get all files matching the pattern
    file_paths = get_files(directory_path, pattern)
    
    if not file_paths:
        print(f"No files matching pattern '{pattern}' found in the directory.")
        return []
    
    # Validate files
    validated_files = validate_files(file_paths, expected_extensions)
    
    # Print summary
    print_files_summary(validated_files, file_type)
    
    return validated_files


# Convenience functions for common use cases
def list_and_validate_documents(directory_path: str, pattern: str = "*.pdf") -> List[Dict]:
    """
    Convenience function to list and validate document files (defaults to PDF).
    
    Args:
        directory_path: Path to the document directory
        pattern: File pattern to match (default: "*.pdf")
        
    Returns:
        List of validated document file information
    """
    return list_and_validate_files(
        directory_path=directory_path,
        pattern=pattern,
        expected_extensions=['.pdf'],
        file_type="document"
    )


def list_and_validate_pdfs(directory_path: str) -> List[Dict]:
    """
    Convenience function to list and validate PDF files.
    
    Args:
        directory_path: Path to the PDF directory
        
    Returns:
        List of validated PDF file information
    """
    return list_and_validate_files(
        directory_path=directory_path,
        pattern="*.pdf",
        expected_extensions=['.pdf'],
        file_type="PDF"
    )