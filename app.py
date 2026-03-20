import streamlit as st
import json
import os

from bookchunker.app.services import (
    get_agent,
    get_router,
    get_matcher,
    get_retriever,
    get_chunk_resolver,
)

from bookchunker.app.context import build_context_from_ranked_chunks
from bookchunker.utils import render_markdown_with_latex
from bookchunker.memory.session_memory import SessionMemory
from bookchunker.memory.chat_store import save_chat

# --------------------------------------------------
# Base Directory
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(page_title="Visualization AI", layout="wide")
st.title("Data Analytics & Visualization")

# --------------------------------------------------
# Initialize Chat Memory
# --------------------------------------------------
if "session_memory" not in st.session_state:
    st.session_state.session_memory = SessionMemory()

# --------------------------------------------------
# Load Syllabus
# --------------------------------------------------
with open("syllabus.json", "r") as f:
    syllabus_data = json.load(f)

units = syllabus_data["units"]

# --------------------------------------------------
# Initialize Services (Cached)
# --------------------------------------------------
matcher = get_matcher("syllabus.json")
router = get_router()
agent = get_agent()

# 🔹 Retrieval Mode Selector
retrieval_mode = st.sidebar.selectbox(
    "Retrieval Mode",
    ["chunk", "title", "hybrid"],
    index=0
)

st.sidebar.divider()

if st.sidebar.button("💾 End Chat Session"):

    history = st.session_state.session_memory.export()

    path = save_chat(history)

    st.sidebar.success(f"Chat saved: {path}")

    # del st.session_state.session_memory
    st.session_state.session_memory = SessionMemory()

retriever = get_retriever(
    embedding_model="openai-small",
    retrieval_mode=retrieval_mode,
)

chunk_resolver = get_chunk_resolver()


# ==================================================
# SIDEBAR — Structured Notes Builder
# ==================================================
st.sidebar.header("📘 Build Notes from Syllabus")

selected_topics = []

for unit in units:
    with st.sidebar.expander(f"Unit {unit['unit_number']}: {unit['title']}"):
        for topic in unit["topics"]:
            if st.checkbox(topic, key=f"{unit['unit_number']}_{topic}"):
                selected_topics.append({
                    "unit_title": unit["title"],
                    "topic": topic
                })

if st.sidebar.button("📝 Create Notes"):
    if selected_topics:
        st.session_state["selected_topics"] = selected_topics
    else:
        st.sidebar.warning("Select at least one topic.")

# ==================================================
# MAIN AREA — Chat Interface
# ==================================================
st.header("💬 Chat Assistant")

# --------------------------------------------------
# Render Chat History
# --------------------------------------------------
history = st.session_state.session_memory.get_recent()

for msg in history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# user_query = st.text_input("Ask your question:")
user_query = st.chat_input("Ask your question")

if user_query:

    # --------------------------------------------
    # Display user message
    # --------------------------------------------
    with st.chat_message("user"):
        st.markdown(user_query)

    history = st.session_state.session_memory.get_recent()

    # --------------------------------------------
    # Router Decision
    # --------------------------------------------
    decision = router.route(
        user_query,
        history=history
    )

    with st.expander("🧭 Router Decision"):
        st.json(decision.model_dump())

    st.session_state.session_memory.add_user(user_query)

    # --------------------------------------------
    # Retrieval
    # --------------------------------------------
    retrieved = None
    ranked = []
    book_ids = []

    if decision.use_book_retrieval:

        with st.spinner("🔎 Retrieving textbook content..."):
            retrieved = retriever.retrieve(user_query)

        ranked = (retrieved or {}).get("ranked_chunks", [])

        if ranked:
            _, _, book_ids = build_context_from_ranked_chunks(
                ranked,
                max_chunks=6,
                max_chars=8000
            )

    # --------------------------------------------
    # Conversation Context
    # --------------------------------------------
    conversation = None

    if decision.needs_conversation_context:
        conversation = history

    # --------------------------------------------
    # Generate Answer
    # --------------------------------------------
    if decision.use_book_retrieval and not ranked:

        answer = "I couldn't find relevant material in the textbooks."

    else:

        answer = agent.run(
            user_query=user_query,
            retrieved_chunks=ranked,
            conversation_history=conversation,
            book_id=", ".join(book_ids) if book_ids else None
        )

    # --------------------------------------------
    # Display assistant response
    # --------------------------------------------
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.session_memory.add_assistant(answer)

# ==================================================
# NOTES GENERATION SECTION
# ==================================================
if "selected_topics" in st.session_state:

    st.divider()
    st.header("📚 Generated Notes")

    for item in st.session_state["selected_topics"]:

        st.subheader(f"{item['unit_title']} → {item['topic']}")

        topic_query = f"{item['unit_title']} - {item['topic']}"

        # ------------------------------------------
        # STEP 1: Retrieve
        # ------------------------------------------
        with st.spinner(f"🔎 Retrieving textbook content for {item['topic']}..."):
            retrieved = retriever.retrieve(topic_query)

        ranked = (retrieved or {}).get("ranked_chunks", [])

        if not ranked:
            st.warning("No relevant content found in textbook.")
            continue

        # ------------------------------------------
        # STEP 2: Retrieval Debug Panel
        # ------------------------------------------
        with st.expander("🔍 Retrieval Debug (Ranked Results)"):
            for idx, entry in enumerate(ranked):
                st.markdown(f"### Rank {idx+1}")
                st.write("Score:", entry.get("score"))
                st.write("Book:", entry.get("book_id"))
                st.write("Metadata:", entry.get("metadata"))
                st.markdown("**Text Preview:**")
                st.code(entry.get("text", "")[:600])
                st.divider()

        # ------------------------------------------
        # STEP 3: Build Context
        # ------------------------------------------
        context_text, chunk_ids, book_ids = build_context_from_ranked_chunks(
            ranked,
            max_chunks=6,
            max_chars=8000
        )

        # ------------------------------------------
        # STEP 4: Extract Images from Chunks
        # ------------------------------------------
        image_paths = chunk_resolver.extract_image_paths(chunk_ids)

        with st.expander("🖼 Image Debug Panel"):

            if not image_paths:
                st.warning("No images found for this topic.")
            else:
                for path in image_paths[:3]:

                    full_path = os.path.join(BASE_DIR, path)

                    st.write("Relative:", path)
                    st.write("Full:", full_path)

                    if os.path.exists(full_path):
                        st.image(full_path, use_column_width=True)
                    else:
                        st.error(f"❌ Image not found: {full_path}")

        # ------------------------------------------
        # STEP 5: Generate Notes
        # ------------------------------------------
        with st.spinner(f"✍️ Generating notes for {item['topic']}..."):
            notes = agent.generate_notes(
                topic=item["topic"],
                unit=item["unit_title"],
                text_context=context_text,
                image_paths=image_paths,
                book_id=", ".join(book_ids) if book_ids else None
            )

        formatted_notes = render_markdown_with_latex(notes)
        st.markdown(formatted_notes, unsafe_allow_html=True)

        st.divider()