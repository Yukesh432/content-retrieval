from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings


class EmbeddingFactory:

    @staticmethod
    def create(model_name: str):

        if model_name == "openai-small":
            return OpenAIEmbeddings(
                model="text-embedding-3-small"
            )

        elif model_name == "openai-large":
            return OpenAIEmbeddings(
                model="text-embedding-3-large"
            )

        elif model_name == "bge-small":
            return HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-en"
            )

        elif model_name == "bge-large":
            return HuggingFaceEmbeddings(
                model_name="BAAI/bge-large-en"
            )

        elif model_name == "e5-large":
            return HuggingFaceEmbeddings(
                model_name="intfloat/e5-large-v2"
            )

        else:
            raise ValueError(f"Unsupported embedding model: {model_name}")
