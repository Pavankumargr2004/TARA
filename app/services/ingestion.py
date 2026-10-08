"""
Document ingestion service.
Loads PDF, TXT, and DBC files; splits into chunks for vector indexing.
"""
import os
from typing import List, Any
# pyrefly: ignore [missing-import]
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
# pyrefly: ignore [missing-import]
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # pyrefly: ignore [missing-import]
    from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentIngestor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

    def load_and_split(self, file_path: str) -> List[Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[-1].lower()
        if ext == ".pdf":
            loader = PyMuPDFLoader(file_path)
        elif ext in (".txt", ".dbc", ".json", ".csv", ".arxml", ".xml"):
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        return chunks

    def process_directory(self, dir_path: str) -> List[Any]:
        all_chunks: List[Any] = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    chunks = self.load_and_split(file_path)
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"[Ingestion] Skipped {file_path}: {e}")
        return all_chunks
