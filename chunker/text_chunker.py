def chunk_page_text(page_data, chunk_size=800, overlap=150):
    text = page_data["text"]
    images = page_data["images"]

    chunks = []
    start = 0
    chunk_id = 0

    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]

        chunks.append({
            "chunk_id": f"page_{page_data['page_number']}_chunk_{chunk_id}",
            "text": chunk_text,
            "images": images   # attach page images
        })

        start = end - overlap
        chunk_id += 1

    return chunks
