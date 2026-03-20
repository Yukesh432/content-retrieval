from pathlib import Path
from bookchunker.chunker.config import OUTPUT_DIR
from bookchunker.db.vs_builder import (
    build_title_store,
    build_chunk_store,
)

EMBEDDING_MODEL = "openai-small"


def build_all():
    for file in OUTPUT_DIR.glob("*.json"):
        book_id = file.stem
        print(f"\n🔄 Processing {book_id}")
        build_title_store(book_id, EMBEDDING_MODEL)
        build_chunk_store(book_id, EMBEDDING_MODEL)


if __name__ == "__main__":
    build_all()