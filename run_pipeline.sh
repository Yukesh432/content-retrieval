#!/bin/bash

echo "Starting BookChunker pipeline..."

echo "Step 1: Running chunker"
python -m chunker.main

echo "Step 2: Building vector database"
python -m db.build_vector_db

echo "Step 3: Launching Streamlit app"
streamlit run app.py