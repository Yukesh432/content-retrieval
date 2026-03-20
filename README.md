# 📚 BookChunker and Retrieval Streamlit App

An end-to-end pipeline for processing books into semantic chunks, building a vector database, and interactively querying content using a Streamlit 
interface.

---

## 🚀 Pipeline Overview

This project follows a 3-stage pipeline:

```bash
#!/bin/bash
echo "Starting BookChunker pipeline..."

echo "Step 1: Running chunker"
python -m chunker.main

echo "Step 2: Building vector database"
python -m db.build_vector_db

echo "Step 3: Launching Streamlit app"
streamlit run app.py