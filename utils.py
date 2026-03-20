import json
import re

class AgentRouter:
    """
    Decides which mode the agent should run in.
    For now, only simple mode.
    Later we add:
    - reasoning mode
    - tool mode
    - memory mode
    """

    def detect_mode(self, query: str) -> str:
        query_lower = query.lower()

        # Future expansion logic
        if any(word in query_lower for word in ["calculate", "derive", "prove"]):
            return "reasoning"

        if any(word in query_lower for word in ["search", "find latest", "web"]):
            return "tools"

        if any(word in query_lower for word in ["previous question", "earlier"]):
            return "memory"

        return "simple"


class SyllabusMatcher:
    def __init__(self, syllabus_path: str):
        with open(syllabus_path, "r") as f:
            self.syllabus = json.load(f)
        
        # IMPORTANT FIX HERE
        self.units = self.syllabus["units"]

    def normalize(self, text: str):
        return re.sub(r"[^\w\s]", "", text.lower())

    def match_query(self, query):
        query_norm = self.normalize(query)
        query_tokens = set(query_norm.split())

        best_match = None
        best_score = 0

        for unit in self.units:
            unit_title_norm = self.normalize(unit["title"])
            unit_tokens = set(unit_title_norm.split())

            score = len(query_tokens & unit_tokens)

            if score > best_score:
                best_score = score
                best_match = unit

        if best_match:
            return {
                "unit_number": best_match["unit_number"],
                "unit_title": best_match["title"],
                "topic": None
            }

        return None

def normalize_toc_structure(toc_data):
    """
    Makes TOC compatible with:
    1) List root
    2) Dict root with 'toc' key
    Returns clean list of entries.
    """

    # Case 1 → Already list
    if isinstance(toc_data, list):
        entries = toc_data

    # Case 2 → Dict with 'toc'
    elif isinstance(toc_data, dict) and "toc" in toc_data:
        entries = toc_data["toc"]

    else:
        raise ValueError("Unsupported TOC structure.")

    # Keep only real chapters
    chapters = [entry for entry in entries if "chapter" in entry]

    return chapters

import re

def render_markdown_with_latex(text: str):
    """
    Converts raw LaTeX-like expressions into proper Markdown math blocks.
    """

    # Convert standalone \frac expressions into $$ blocks
    text = re.sub(
        r'(\\frac\{.*?\}\{.*?\})',
        r'$$\1$$',
        text
    )

    # Convert common math patterns with _{...}
    text = re.sub(
        r'([a-zA-Z]_\{.*?\})',
        r'$\1$',
        text
    )

    return text
