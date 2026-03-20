# PDF_PATH = "/home/olive/Desktop/data_analysis_visualization/data-visualization-principles-and-practice.pdf"
# TOC_PATH = "/home/olive/Desktop/data_analysis_visualization/tocs/toc_ii.json"
# OUTPUT_JSON = "structured_book.json"
# IMAGE_DIR = "extracted_images"

# PDF_CONTENT_START = 14  # zero-based
# CHUNK_SIZE = 800
# OVERLAP = 150
# ENABLE_IMAGE_TEXT_MODE = True
# IMAGE_EXTRACTION_MODE = "layout"  # simple | layout | render
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

BOOKS_DIR = BASE_DIR / "books"
TOCS_DIR = BASE_DIR / "tocs"
OUTPUT_DIR = BASE_DIR / "structured_outputs"
IMAGE_ROOT_DIR = BASE_DIR / "extracted_images"

PDF_CONTENT_START = 14
CHUNK_SIZE = 800
OVERLAP = 150

ENABLE_IMAGE_TEXT_MODE = True
IMAGE_EXTRACTION_MODE = "layout"

print(BASE_DIR)