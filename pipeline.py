import fitz
import json


PDF_PATH = "visualizing-data.pdf"
TOC_PATH = "toc.json"

# You said actual content starts at PDF page 15
PDF_CONTENT_START = 14  # zero-based index


def extract_full_text_from(doc, start_page):
    """
    Extract entire PDF text starting from a page.
    """
    text = ""
    for i in range(start_page, len(doc)):
        text += "\n" + doc[i].get_text()
    return text


def find_all_positions(text, patterns):
    """
    Find positions of patterns in text.
    Returns sorted list of (position, pattern).
    """
    positions = []
    for p in patterns:
        idx = text.find(p)
        if idx != -1:
            positions.append((idx, p))
    positions.sort()
    return positions


def slice_sections(chapter_text, subsection_titles, next_chapter_title=None):
    """
    Slice chapter text using subsection titles.
    """

    subsection_positions = find_all_positions(chapter_text, subsection_titles)

    sections = []

    for i in range(len(subsection_positions)):
        start_pos, title = subsection_positions[i]

        # Determine end position
        if i < len(subsection_positions) - 1:
            end_pos = subsection_positions[i + 1][0]
        elif next_chapter_title:
            next_ch_pos = chapter_text.find(next_chapter_title)
            end_pos = next_ch_pos if next_ch_pos != -1 else len(chapter_text)
        else:
            end_pos = len(chapter_text)

        content = chapter_text[start_pos:end_pos].strip()

        sections.append({
            "section_title": title,
            "content": content
        })

    return sections

def main():
    OUTPUT_PATH = "structured_book.json"

    # ---- Load TOC ----
    with open(TOC_PATH, "r", encoding="utf-8") as f:
        toc = json.load(f)

    # ---- Open PDF ----
    doc = fitz.open(PDF_PATH)

    # ---- Extract full text starting from page 15 ----
    START_PAGE = 15 - 1  # zero-based index
    full_text = ""

    for i in range(START_PAGE, len(doc)):
        page = doc[i]
        full_text += page.get_text("text") + "\n"

    chapters = []

    # ---- Iterate over chapters in TOC ----
    for idx, chapter_info in enumerate(toc):

        if "chapter" not in chapter_info:
            continue  # skip Preface or non-chapter entries

        chapter_title = chapter_info["title"]
        chapter_number = chapter_info["chapter"]

        # ---- Find chapter start ----
        chapter_start = full_text.find(chapter_title)

        if chapter_start == -1:
            print(f"⚠ Could not find chapter title: {chapter_title}")
            continue

        # ---- Determine chapter end ----
        if idx + 1 < len(toc):
            next_chapter_title = toc[idx + 1]["title"]
            chapter_end = full_text.find(next_chapter_title, chapter_start + 1)
            if chapter_end == -1:
                chapter_end = len(full_text)
        else:
            chapter_end = len(full_text)

        chapter_text = full_text[chapter_start:chapter_end].strip()

        # ---- Extract subsection titles ----
        subsection_titles = [
            s["title"] for s in chapter_info.get("subsections", [])
        ]

        # =====================================================
        # STEP 1: Extract chapter intro (before first subsection)
        # =====================================================

        chapter_content = ""

        if subsection_titles:
            first_sub_title = subsection_titles[0]
            first_sub_pos = chapter_text.find(first_sub_title)

            if first_sub_pos != -1:
                chapter_content = chapter_text[:first_sub_pos].strip()
            else:
                chapter_content = ""
        else:
            chapter_content = chapter_text

        # =====================================================
        # STEP 2: Extract subsection content
        # =====================================================

        sections = []

        for i, sub_title in enumerate(subsection_titles):

            sub_start = chapter_text.find(sub_title)

            if sub_start == -1:
                continue

            if i + 1 < len(subsection_titles):
                next_sub_title = subsection_titles[i + 1]
                sub_end = chapter_text.find(next_sub_title, sub_start + 1)
                if sub_end == -1:
                    sub_end = len(chapter_text)
            else:
                sub_end = len(chapter_text)

            section_text = chapter_text[sub_start:sub_end].strip()

            sections.append({
                "section_title": sub_title,
                "content": section_text
            })

        # =====================================================
        # Append chapter
        # =====================================================

        chapters.append({
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "chapter_content": chapter_content,
            "sections": sections
        })

        print(f"✓ Extracted Chapter {chapter_number}")

    # ---- Save Output ----
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(chapters, f, indent=2, ensure_ascii=False)

    print("\n✅ Extraction Complete!")
    print(f"Saved to: {OUTPUT_PATH}")



if __name__ == "__main__":
    main()
