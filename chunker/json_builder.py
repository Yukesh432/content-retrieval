from bookchunker.chunker.text_chunker import chunk_page_text


def build_book_json(pages_data, toc, chapter_ranges, chunk_size, overlap):

    global_chunks = []
    chapters = []

    # Create quick lookup: page_number -> page object
    pages_lookup = {
        page["page_number"] - 1: page
        for page in pages_data
    }

    for chapter_info in toc:

        if "chapter" not in chapter_info:
            continue

        chapter_number = chapter_info["chapter"]
        chapter_title = chapter_info["title"]

        if chapter_number not in chapter_ranges:
            continue

        start_page, end_page = chapter_ranges[chapter_number]

        chapter_obj = {
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "chapter_content": "",
            "sections": [],
            "chapter_multimodal_chunks": []
        }

        # Loop only pages in this chapter range
        for page_index in range(start_page, end_page):

            if page_index not in pages_lookup:
                continue

            page = pages_lookup[page_index]

            page_chunks = chunk_page_text(page, chunk_size, overlap)

            for chunk in page_chunks:
                chunk["chapter_number"] = chapter_number
                global_chunks.append(chunk)
                chapter_obj["chapter_multimodal_chunks"].append(
                    chunk["chunk_id"]
                )

        chapters.append(chapter_obj)

    return {
        "chapters": chapters,
        "global_chunks": global_chunks
    }
