import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document

from bookchunker.chunker.config import OUTPUT_DIR
from bookchunker.db.embed_fact import EmbeddingFactory

load_dotenv()

DB_ROOT = Path("vector_db")


def _db_path(embedding_model: str, store_type: str, book_id: str) -> Path:
    """
    store_type: 'titles' or 'chunks'
    """
    return DB_ROOT / embedding_model / store_type / book_id


# ==========================================================
# BUILD TITLE STORE
# ==========================================================

def build_title_store(book_id: str, embedding_model: str = "openai-small"):

    book_path = OUTPUT_DIR / f"{book_id}.json"
    if not book_path.exists():
        raise FileNotFoundError(f"Book not found: {book_path}")

    with open(book_path, "r", encoding="utf-8") as f:
        book = json.load(f)

    chapters = book["chapters"]
    documents = []

    for chapter in chapters:
        documents.append(
            Document(
                page_content=chapter["chapter_title"],
                metadata={
                    "type": "chapter_title",
                    "book_id": book_id,
                    "chapter_number": chapter["chapter_number"],
                    "chapter_title": chapter["chapter_title"],
                },
            )
        )

        for section in chapter.get("sections", []):
            documents.append(
                Document(
                    page_content=section["section_title"],
                    metadata={
                        "type": "section_title",
                        "book_id": book_id,
                        "chapter_number": chapter["chapter_number"],
                        "chapter_title": chapter["chapter_title"],
                        "section_title": section["section_title"],
                    },
                )
            )

    embeddings = EmbeddingFactory.create(embedding_model)

    db_dir = _db_path(embedding_model, "titles", book_id)
    db_dir.mkdir(parents=True, exist_ok=True)

    Chroma.from_documents(
        documents,
        embedding=embeddings,
        persist_directory=str(db_dir),
        collection_name=f"{book_id}_titles",
    )

    print(f"✅ Title store built for {book_id}")


# ==========================================================
# BUILD CHUNK STORE (NEW)
# ==========================================================

def build_chunk_store(book_id: str, embedding_model: str = "openai-small"):

    book_path = OUTPUT_DIR / f"{book_id}.json"
    if not book_path.exists():
        raise FileNotFoundError(f"Book not found: {book_path}")

    with open(book_path, "r", encoding="utf-8") as f:
        book = json.load(f)

    global_chunks = book["global_chunks"]
    documents = []

    for chunk in global_chunks:
        documents.append(
            Document(
                page_content=chunk["text"],
                metadata={
                    "type": "content_chunk",
                    "book_id": book_id,
                    "chunk_id": chunk["chunk_id"],
                    "chapter_number": chunk.get("chapter_number"),
                    "section_title": chunk.get("section_title"),
                },
            )
        )

    embeddings = EmbeddingFactory.create(embedding_model)

    db_dir = _db_path(embedding_model, "chunks", book_id)
    db_dir.mkdir(parents=True, exist_ok=True)

    Chroma.from_documents(
        documents,
        embedding=embeddings,
        persist_directory=str(db_dir),
        collection_name=f"{book_id}_chunks",
    )

    print(f"✅ Chunk store built for {book_id}")