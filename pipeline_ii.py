import fitz
import json
import os

# ==========================
# CONFIG
# ==========================

PDF_PATH = "visualizing-data.pdf"
TOC_PATH = "toc.json"
OUTPUT_PATH = "structured_book.json"
IMAGE_DIR = "images"

PDF_CONTENT_START = 14
CHUNK_SIZE = 800
OVERLAP = 150


# ==========================
# IMAGE EXTRACTION
# ==========================

def extract_images_from_page(doc, page_index):
    page = doc[page_index]
    image_list = page.get_images(full=True)

    extracted_images = []

    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]

        image_filename = f"page_{page_index+1}_img_{img_index}.{image_ext}"
        image_path = os.path.join(IMAGE_DIR, image_filename)

        with open(image_path, "wb") as f:
            f.write(image_bytes)

        extracted_images.append({
            "image_path": image_path,
            "page_number": page_index + 1
        })

    return extracted_images


# ==========================
# PAGE EXTRACTION
# ==========================

def extract_pages(doc):
    pages = []

    for i in range(PDF_CONTENT_START, len(doc)):
        page = doc[i]

        pages.append({
            "page_number": i + 1,
            "text": page.get_text("text"),
            "images": extract_images_from_page(doc, i)
        })

    return pages


# ==========================
# CHUNKING
# ==========================

def chunk_page(page_data, chapter_number=None, section_title=None):
    text = page_data["text"]
    images = page_data["images"]

    chunks = []
    start = 0
    chunk_id_counter = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end]

        chunk_id = f"page_{page_data['page_number']}_chunk_{chunk_id_counter}"

        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_text,
            "images": images,
            "page_number": page_data["page_number"],
            "chapter_number": chapter_number,
            "section_title": section_title
        })

        start = end - OVERLAP
        chunk_id_counter += 1

    return chunks


# ==========================
# MAIN PIPELINE
# ==========================

def main():

    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    doc = fitz.open(PDF_PATH)

    with open(TOC_PATH, "r", encoding="utf-8") as f:
        toc = json.load(f)

    pages = extract_pages(doc)

    global_chunks = []
    chapters = []

    # SIMPLE CHAPTER MAPPING (can refine later)
    for chapter_info in toc:

        if "chapter" not in chapter_info:
            continue

        chapter_number = chapter_info["chapter"]
        chapter_title = chapter_info["title"]

        chapter_obj = {
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "chapter_content": "",
            "sections": [],
            "chapter_multimodal_chunks": []
        }

        for page in pages:
            page_chunks = chunk_page(page, chapter_number)

            for chunk in page_chunks:
                global_chunks.append(chunk)
                chapter_obj["chapter_multimodal_chunks"].append(chunk["chunk_id"])

        chapters.append(chapter_obj)

    final_book = {
        "metadata": {
            "source_pdf": PDF_PATH
        },
        "chapters": chapters,
        "global_chunks": global_chunks
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_book, f, indent=2, ensure_ascii=False)

    print("✅ Unified Multimodal Book JSON Created")


if __name__ == "__main__":
    main()
