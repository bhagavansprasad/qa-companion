"""Configuration settings for Document Knowledge Base system."""


class Config:
    """Configuration class with all system settings."""
    
    # Application settings
    APP_NAME = "Document Knowledge Base"
    DEBUG = False
    LOG_LEVEL = "INFO"
    
    # Data paths (currently focused on PDFs)
    PDF_DATA_PATH = "./data/pdfs"
    IMAGE_OUTPUT_PATH = "./data/images"
    PROCESSED_DATA_PATH = "./data/processed"
    LOG_DIR = "./logs"
    
    # Document processing settings (currently PDF-specific)
    MAX_PAGES_PER_PDF = None  # Process all pages if None
    MIN_IMAGE_WIDTH = 100
    MIN_IMAGE_HEIGHT = 100
    
    # Text processing settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 100
    
    # Embedding settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384
    
    # Vector database settings
    CHROMA_DB_PATH = "./data/chroma_db"
    COLLECTION_NAME = "knowledge_base"
    
    # Retrieval settings
    RETRIEVAL_K = 5
    SIMILARITY_THRESHOLD = 0.7
    
    # LLM settings (VertexAI)
    VERTEX_AI_PROJECT = None  # Set your project ID here
    VERTEX_AI_REGION = "us-central1"
    VERTEX_AI_MODEL = "text-bison"
    