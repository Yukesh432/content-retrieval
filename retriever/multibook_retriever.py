from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma

from bookchunker.db.embed_fact import EmbeddingFactory

load_dotenv()

DB_ROOT = Path("vector_db")


from pathlib import Path
from typing import List, Optional, Dict, Union
from dotenv import load_dotenv
from langchain_chroma import Chroma

from bookchunker.db.embed_fact import EmbeddingFactory

load_dotenv()

DB_ROOT = Path("vector_db")


class MultiBookRetriever:
    """
    Unified retriever supporting:

        mode="title"
        mode="chunk"
        mode="hybrid"

    Supports:
        - single book (book_ids=["bookA"])
        - subset of books
        - all books (book_ids=None)
    """

    VALID_MODES = {"title", "chunk", "hybrid"}

    def __init__(
        self,
        embedding_model: str = "openai-small",
        mode: str = "chunk",
        book_ids: Optional[List[str]] = None,
    ):
        if mode not in self.VALID_MODES:
            raise ValueError(f"mode must be one of {self.VALID_MODES}")

        self.embedding_model = embedding_model
        self.mode = mode
        self.book_ids = book_ids

        self.embeddings = EmbeddingFactory.create(embedding_model)

        self.base_path = DB_ROOT / embedding_model
        if not self.base_path.exists():
            raise ValueError(f"No vector DB found for embedding '{embedding_model}'")

        self.databases: Dict[str, Union[Chroma, Dict[str, Chroma]]] = {}

        self._load_databases()

    # -------------------------------------------------
    # Loader
    # -------------------------------------------------

    def _load_databases(self):

        if self.mode == "hybrid":
            self._load_hybrid()
        else:
            self._load_single_mode(self.mode)

    def _resolve_target_books(self, store_folder: Path) -> List[str]:
        """
        Determine which books to load.
        """
        if not store_folder.exists():
            raise ValueError(f"Store folder not found: {store_folder}")

        available_books = [
            p.name for p in store_folder.iterdir()
            if p.is_dir()
        ]

        if self.book_ids is None:
            return available_books

        # Filter only requested books that exist
        valid_books = [b for b in self.book_ids if b in available_books]

        if not valid_books:
            raise ValueError("None of the requested book_ids exist in the vector DB.")

        return valid_books

    def _load_single_mode(self, mode: str):
        """
        Loads either title OR chunk stores.
        """
        store_folder = self.base_path / f"{mode}s"
        target_books = self._resolve_target_books(store_folder)

        for book_id in target_books:
            book_dir = store_folder / book_id

            self.databases[book_id] = Chroma(
                persist_directory=str(book_dir),
                embedding_function=self.embeddings,
                collection_name=f"{book_id}_{mode}s"
            )

    def _load_hybrid(self):
        """
        Loads both title and chunk stores.
        """
        titles_path = self.base_path / "titles"
        chunks_path = self.base_path / "chunks"

        if not titles_path.exists() or not chunks_path.exists():
            raise ValueError("Hybrid mode requires both title and chunk stores.")

        target_books = self._resolve_target_books(chunks_path)

        for book_id in target_books:
            self.databases[book_id] = {
                "titles": Chroma(
                    persist_directory=str(titles_path / book_id),
                    embedding_function=self.embeddings,
                    collection_name=f"{book_id}_titles"
                ),
                "chunks": Chroma(
                    persist_directory=str(chunks_path / book_id),
                    embedding_function=self.embeddings,
                    collection_name=f"{book_id}_chunks"
                )
            }

    def retrieve(
        self,
        query: str,
        k_per_book: int = 5,
        final_k: int = 8,
        strategy: str = "global_topk",   # global_topk | balanced_per_book
        per_book_take: int = 1,
        score_threshold: float | None = None
    ):

        combined = []

        # -------------------------------------------------
        # Collect candidates
        # -------------------------------------------------

        for book_id, db_obj in self.databases.items():

            # Hybrid mode: search chunks only (title search optional)
            if self.mode == "hybrid":
                db = db_obj["chunks"]
            else:
                db = db_obj

            results = db.similarity_search_with_score(query, k=k_per_book)

            for doc, score in results:

                # Optional score filter
                if score_threshold is not None and score > score_threshold:
                    continue

                combined.append({
                    "book_id": book_id,
                    "score": float(score),
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                })

        if not combined:
            return {"ranked_chunks": []}

        # -------------------------------------------------
        # Sorting (Chroma: lower score = more similar)
        # -------------------------------------------------

        combined.sort(key=lambda x: x["score"])

        # -------------------------------------------------
        # Selection strategy
        # -------------------------------------------------

        if strategy == "global_topk":
            selected = combined[:final_k]

        elif strategy == "balanced_per_book":
            from collections import defaultdict

            by_book = defaultdict(list)
            for r in combined:
                by_book[r["book_id"]].append(r)

            pool = []
            for book_id, rows in by_book.items():
                pool.extend(rows[:per_book_take])

            pool.sort(key=lambda x: x["score"])
            selected = pool[:final_k]

        else:
            raise ValueError("Unsupported strategy")

        return {
            "query": query,
            "strategy": strategy,
            "ranked_chunks": selected
        }