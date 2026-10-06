"""
RAG Pipeline — ChromaDB retrieval with BGE embeddings.
"""
from typing import List, Any

# pyrefly: ignore [missing-import]
from langchain_chroma import Chroma
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings


class RAGPipeline:
    def __init__(self, persist_directory: str = settings.CHROMA_PERSIST_DIR):
        self.persist_directory = persist_directory

        model_name = "BAAI/bge-small-en-v1.5"
        model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": True}

        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )

        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )

    def index_documents(
        self, chunks: List[Any], collection_name: str = "tara_knowledge"
    ) -> None:
        vs = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=collection_name,
        )
        vs.persist()
        self.vector_store = vs

    def query(
        self,
        query: str,
        collection_name: str = "tara_knowledge",
        k: int = 5,
    ) -> List[Any]:
        vs = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=collection_name,
        )
        return vs.similarity_search(query, k=k)
