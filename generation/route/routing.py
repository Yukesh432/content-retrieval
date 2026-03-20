from __future__ import annotations
from typing import Optional, List, Dict

from ..constants import PLAIN_LLM, BOOK_LLM, BOOK_WEB_LLM, WEB_ONLY_LLM


_TRIGGER_KEYWORDS = (
    "explain",
    "define",
    "according to",
    "in the book",
    "from notes",
    "based on",
)


# --------------------------------------------------
# Detect if conversation context should be used
# --------------------------------------------------
def needs_context(query: str) -> bool:
    q = query.lower()
    return any(k in q for k in _TRIGGER_KEYWORDS)


# --------------------------------------------------
# Decide if web search should run
# --------------------------------------------------
def should_web_search(
    *,
    enable_web_search: bool,
    user_query: str,
    retrieved_chunks: Optional[List[Dict]],
    force_web_search: bool,
) -> bool:

    if not enable_web_search:
        return False

    if force_web_search:
        return True

    # If nothing retrieved from book
    if not retrieved_chunks:
        return True

    # Measure total text retrieved
    total_chars = sum(len(chunk.get("text", "")) for chunk in retrieved_chunks)

    # Too little book context → web can help
    if total_chars < 400:
        return True

    # Explanatory queries benefit from web context
    if needs_context(user_query):
        return True

    return False


# --------------------------------------------------
# Decide LLM style (chat)
# --------------------------------------------------
def classify_style_chat(*, used_book: bool, used_notes: bool, used_web: bool) -> str:

    if not (used_book or used_notes or used_web):
        return PLAIN_LLM

    if used_book and used_web:
        return BOOK_WEB_LLM

    # notes-only still counts as context usage
    return BOOK_LLM


# --------------------------------------------------
# Decide LLM style (notes generation)
# --------------------------------------------------
def classify_style_notes(*, used_book: bool, used_web: bool) -> str:

    if used_web and not used_book:
        return WEB_ONLY_LLM

    if used_book and used_web:
        return BOOK_WEB_LLM

    return BOOK_LLM