import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from bookchunker.chunker.config import OUTPUT_DIR

class ChunkResolver:
    """
    Resolves chunk_id -> chunk dict (including images) using OUTPUT_DIR/*.json.
    """
    def __init__(self):
        self._chunk_index: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

    def load_all(self):
        if self._loaded:
            return
        for p in OUTPUT_DIR.glob("*.json"):
            with open(p, "r", encoding="utf-8") as f:
                book = json.load(f)
            for ch in book.get("global_chunks", []):
                cid = ch.get("chunk_id")
                if cid:
                    self._chunk_index[cid] = ch
        self._loaded = True

    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        self.load_all()
        return self._chunk_index.get(chunk_id)

    def extract_image_paths(self, chunk_ids: List[str]) -> List[str]:
        self.load_all()
        paths = []
        for cid in chunk_ids:
            ch = self._chunk_index.get(cid)
            if not ch:
                continue
            for img in ch.get("images", []):
                p = img.get("image_path")
                if p:
                    paths.append(p)
        # unique
        return sorted(set(paths))