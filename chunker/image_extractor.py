import os


# ===============================
# MODE 1 — SIMPLE (current)
# ===============================

def extract_simple_images(doc, page, page_index, image_dir):

    image_list = page.get_images(full=True)
    extracted_images = []

    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]

        image_filename = f"page_{page_index+1}_img_{img_index}.{image_ext}"
        image_path = os.path.join(image_dir, image_filename)

        with open(image_path, "wb") as f:
            f.write(image_bytes)

        extracted_images.append({
            "image_path": image_path,
            "page_number": page_index + 1,
            "mode": "simple"
        })

    return extracted_images


# ===============================
# MODE 2 — LAYOUT AWARE
# ===============================
def extract_layout_images(doc, page, page_index, image_dir):

    extracted_images = []
    page_dict = page.get_text("dict")

    img_counter = 0

    for block in page_dict["blocks"]:
        if block["type"] == 1:  # image block

            bbox = block["bbox"]
            image_bytes = block["image"]

            image_filename = f"page_{page_index+1}_layout_{img_counter}.png"
            image_path = os.path.join(image_dir, image_filename)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            extracted_images.append({
                "image_path": image_path,
                "page_number": page_index + 1,
                "bbox": bbox,
                "mode": "layout"
            })

            img_counter += 1

    return extracted_images



# ===============================
# MODE 3 — FULL PAGE RENDER
# ===============================

def render_full_page_image(page, page_index, image_dir):

    pix = page.get_pixmap(dpi=300)

    image_filename = f"page_{page_index+1}_render.png"
    image_path = os.path.join(image_dir, image_filename)

    pix.save(image_path)

    return [{
        "image_path": image_path,
        "page_number": page_index + 1,
        "mode": "render"
    }]


# ===============================
# MAIN ROUTER
# ===============================

def extract_images_from_page(doc, page_index, image_dir, mode="simple"):

    page = doc[page_index]

    if mode == "simple":
        return extract_simple_images(doc, page, page_index, image_dir)

    elif mode == "layout":
        return extract_layout_images(doc, page, page_index, image_dir)

    elif mode == "render":
        return render_full_page_image(page, page_index, image_dir)

    else:
        raise ValueError(f"Unknown image extraction mode: {mode}")
