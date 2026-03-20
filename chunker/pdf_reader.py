from bookchunker.chunker.image_extractor import extract_images_from_page


IMAGE_EXTRACTION_MODE = "render"

def extract_pages_with_images(doc, start_page, image_dir, image_mode=True):
    pages_data = []

    for i in range(start_page, len(doc)):
        page = doc[i]
        text = page.get_text("text")

        images = []
        if image_mode:
            images = extract_images_from_page(
                                        doc,
                                        i,
                                        image_dir,
                                        mode=IMAGE_EXTRACTION_MODE
                                    )


        pages_data.append({
            "page_number": i + 1,
            "text": text,
            "images": images
        })

    return pages_data

def detect_chapter_start_pages(doc, toc, start_page):
    chapter_start_pages = {}

    for i in range(start_page, len(doc)):
        page_text = doc[i].get_text("text")

        for chapter in toc:
            chapter_title = chapter["title"]

            if chapter_title in page_text:
                # breakpoint()
                chapter_start_pages[chapter["chapter"]] = i

    return chapter_start_pages


def build_chapter_ranges_from_toc(toc, pdf_content_start, total_pages):

    chapter_ranges = {}

    # Keep only actual chapters
    chapters = [c for c in toc if "chapter" in c]

    # Sort by printed book page
    chapters = sorted(chapters, key=lambda x: x["page"])

    for i, chapter in enumerate(chapters):

        chapter_number = chapter["chapter"]
        book_page_start = chapter["page"]

        # Convert printed page → PDF index (0-based)
        pdf_start = pdf_content_start + (book_page_start - 1)

        if i + 1 < len(chapters):
            next_book_page = chapters[i + 1]["page"]
            pdf_end = pdf_content_start + (next_book_page - 1)
        else:
            pdf_end = total_pages

        chapter_ranges[chapter_number] = (pdf_start, pdf_end)
    print(chapter_ranges)

    return chapter_ranges
