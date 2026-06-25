"""
RAG service for SMARTTOEFL AI.

Builds and queries a Chroma vector store created from the knowledge dataset
(.txt / .pdf files in app/dataset). The retrieved context is used to ground:
  - AI-generated questions (AI / Hybrid modes)
  - AI Tutor answer explanations

The embedding model and vector store are loaded lazily and cached, so importing
this module is cheap and the heavy model is only loaded the first time RAG is
actually used (or warmed up in the background at startup).
"""

import os
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    from langchain_community.document_loaders import UnstructuredPDFLoader
except ImportError:
    UnstructuredPDFLoader = None


# Absolute paths so RAG works regardless of the current working directory.
_BASE_DIR = Path(__file__).resolve().parent.parent          # .../app
DATASET_DIR = str(_BASE_DIR / "dataset")
PERSIST_DIR = str(_BASE_DIR / "vectorstore")

SUPPORTED_EXTENSIONS = {".txt", ".pdf"}
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Cached singletons (loaded on first use).
_embedding = None
_vectorstore = None


def _get_embedding():
    """Lazily build and cache the HuggingFace embedding model."""
    global _embedding
    if _embedding is None:
        from langchain_community.embeddings import HuggingFaceEmbeddings

        _embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embedding


def _get_vectorstore():
    """Lazily open and cache the persisted Chroma vector store (or None)."""
    global _vectorstore
    if _vectorstore is None:
        from langchain_community.vectorstores import Chroma

        if not os.path.exists(PERSIST_DIR):
            return None

        _vectorstore = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=_get_embedding(),
        )
    return _vectorstore


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def get_context(query: str, category: str = None, k: int = 3) -> str:
    """Return concatenated reference passages for a query, or "" on any failure.

    Never raises: if the vector store is missing or the model fails to load,
    it returns an empty string so the caller can continue without RAG.
    """
    try:
        vectorstore = _get_vectorstore()
        if vectorstore is None:
            return ""

        search_query = f"{category} {query}".strip() if category else query
        docs = vectorstore.similarity_search(search_query, k=k)

        return "\n\n".join(doc.page_content for doc in docs).strip()

    except Exception as error:
        print("RAG get_context error:", error)
        return ""


def is_ready() -> bool:
    """True if the vector store is already loaded into memory."""
    return _vectorstore is not None


def warm_up() -> bool:
    """Pre-load the embedding model, vector store, and query path (used at startup)."""
    try:
        vectorstore = _get_vectorstore()
        if vectorstore is None:
            return False
        # A tiny query warms the full retrieval path so the first real call is fast.
        vectorstore.similarity_search("toefl", k=1)
        return True
    except Exception as error:
        print("RAG warm-up error:", error)
        return False


# ---------------------------------------------------------------------------
# Index building (used by build_rag.py)
# ---------------------------------------------------------------------------

def load_pdf_documents(file_path):
    if pypdf:
        documents = []
        reader = pypdf.PdfReader(file_path)
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={"source": file_path, "page": page_number},
                    )
                )
        return documents

    if UnstructuredPDFLoader:
        return UnstructuredPDFLoader(file_path).load()

    print(f"WARNING: PDF loader not available, skipping {file_path}")
    return []


def load_document(file_path):
    ext = Path(file_path).suffix.lower()

    if ext == ".txt":
        return TextLoader(file_path, encoding="utf-8").load()

    if ext == ".pdf":
        return load_pdf_documents(file_path)

    return []


def build_vectorstore():
    """Rebuild the Chroma vector store from the knowledge dataset."""
    global _vectorstore
    from langchain_community.vectorstores import Chroma

    documents = []

    for root, _, files in os.walk(DATASET_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            ext = Path(file_path).suffix.lower()

            if ext not in SUPPORTED_EXTENSIONS:
                continue

            try:
                docs = load_document(file_path)
                for doc in docs:
                    if not doc.metadata:
                        doc.metadata = {}
                    doc.metadata["source"] = file_path
                    documents.append(doc)
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    docs = splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(
        docs,
        _get_embedding(),
        persist_directory=PERSIST_DIR,
    )

    vectorstore.persist()
    _vectorstore = vectorstore

    return vectorstore
