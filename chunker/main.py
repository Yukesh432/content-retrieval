import fitz
import json
from pathlib import Path

from bookchunker.chunker.config import (
    BOOKS_DIR,
    TOCS_DIR,
    OUTPUT_DIR,
    IMAGE_ROOT_DIR,
    PDF_CONTENT_START,
    CHUNK_SIZE,
    OVERLAP,
    ENABLE_IMAGE_TEXT_MODE
)

from bookchunker.chunker.pdf_reader import (
    extract_pages_with_images,
    build_chapter_ranges_from_toc
)

from bookchunker.chunker.json_builder import build_book_json
from bookchunker.utils import normalize_toc_structure


def process_book(pdf_path: Path):
    book_name = pdf_path.stem
    toc_path = TOCS_DIR / f"{book_name}_toc.json"

    if not toc_path.exists():
        print(f"⚠ No TOC found for {book_name}, skipping.")
        return

    print(f"\n📘 Processing: {book_name}")

    # Create book-specific image directory
    image_dir = IMAGE_ROOT_DIR / book_name
    image_dir.mkdir(parents=True, exist_ok=True)

    # Open PDF
    doc = fitz.open(pdf_path)

    # Load TOC
    with open(toc_path, "r", encoding="utf-8") as f:
        toc_raw = json.load(f)
        toc = normalize_toc_structure(toc_raw)

    # Extract pages + images
    pages_data = extract_pages_with_images(
        doc,
        PDF_CONTENT_START,
        str(image_dir),   # IMPORTANT: pass dynamic image dir
        ENABLE_IMAGE_TEXT_MODE
    )

    # Build chapter ranges
    chapter_ranges = build_chapter_ranges_from_toc(
        toc,
        PDF_CONTENT_START,
        len(doc)
    )

    # Build structured JSON
    structured_data = build_book_json(
        pages_data,
        toc,
        chapter_ranges,
        CHUNK_SIZE,
        OVERLAP
    )

    # Save per-book output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{book_name}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Finished {book_name}")
    print(f"📂 Saved to: {output_path}")


def main():
    pdf_files = BOOKS_DIR.glob("*.pdf")

    for pdf_path in pdf_files:
        process_book(pdf_path)

    print("\n🎉 All books processed successfully!")


if __name__ == "__main__":
    main()
