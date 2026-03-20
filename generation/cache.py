from langchain_core.caches import InMemoryCache
from langchain_core.globals import set_llm_cache

def init_cache():
    cache = InMemoryCache()
    set_llm_cache(cache)
    return cache