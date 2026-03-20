from bookchunker.retriever.multibook_retriever import MultiBookRetriever

class RetrieverFactory:

    def __init__(
        self,
        embedding_model="openai-small",
        retrieval_mode="chunk",
        book_ids=None
    ):
        self.retriever = MultiBookRetriever(
            embedding_model=embedding_model,
            mode=retrieval_mode,
            book_ids=book_ids
        )

    def retrieve(self, query: str):
        return self.retriever.retrieve(query)