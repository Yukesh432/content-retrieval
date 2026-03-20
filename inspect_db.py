from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv


load_dotenv()

DB_DIR = "vector_db"

embeddings = OpenAIEmbeddings()

db = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embeddings,
    collection_name="book_chunks"
)

print("Total stored documents:", db._collection.count())




results = db.similarity_search_with_score("information overload", k=5)

for doc, score in results:
    print("\n---")
    print("Distance:", score)
    print("Chapter:", doc.metadata.get("chapter"))
    print("Section:", doc.metadata.get("section"))
    print("Preview:", doc.page_content[:200])
