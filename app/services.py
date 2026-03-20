import streamlit as st
from bookchunker.generation.llm import VisualizationAgent
from bookchunker.retriever.retriever_fact import RetrieverFactory
from bookchunker.logging_utils import get_logger

from utils import SyllabusMatcher
from bookchunker.generation.route.router_llm import RouterAgent
from bookchunker.app.chunk_resolver import ChunkResolver
from bookchunker.generation.cache import init_cache

logger = get_logger("services.router")

@st.cache_resource
def get_chunk_resolver():
    return ChunkResolver()

@st.cache_resource
def get_agent():
    init_cache()
    return VisualizationAgent(enable_web_search=False)

@st.cache_resource
def get_router():

    logger = get_logger("services.router")
    logger.info("Initializing RouterAgent")

    return RouterAgent()

@st.cache_resource
def get_matcher(syllabus_path: str):
    return SyllabusMatcher(syllabus_path)

@st.cache_resource
def get_retriever(embedding_model="openai-small", retrieval_mode="chunk", book_ids=None):
    # Your factory should accept these args; if not, update it.
    return RetrieverFactory(
        embedding_model=embedding_model,
        retrieval_mode=retrieval_mode,
        book_ids=book_ids
    )