from typing import List, Dict, Any, Tuple

def build_context_from_ranked_chunks(
    ranked_chunks: List[Dict[str, Any]],
    max_chunks: int = 6,
    max_chars: int = 8000
) -> Tuple[str, List[str], List[str]]:
    """
    Returns:
      context_text, chunk_ids, book_ids
    """
    parts = []
    chunk_ids = []
    book_ids = []

    for r in ranked_chunks[:max_chunks]:
        book_id = r.get("book_id")
        score = r.get("score")
        text = r.get("text", "")
        md = r.get("metadata", {}) or {}
        cid = md.get("chunk_id")

        if book_id:
            book_ids.append(book_id)
        if cid:
            chunk_ids.append(cid)

        parts.append(
            f"[Book: {book_id} | Score: {score:.4f} | Chunk: {cid}]\n{text}"
        )

    context = "\n\n---\n\n".join(parts)
    return context[:max_chars], chunk_ids, sorted(set(book_ids))