import os
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

try:
    from langchain_community.document_loaders import UnstructuredPDFLoader
except ImportError:
    UnstructuredPDFLoader = None

try:
    import pypdf
except ImportError:
    pypdf = None

DATA_PATH = "app/dataset"
CATEGORY_FOLDERS = {
    "grammar": "grammar",
    "vocabulary": "vocabulary",
    "reading": "reading",
    "listening": "listening",
    "speaking": "speaking"
}
SUPPORTED_EXTENSIONS = {".txt", ".pdf"}

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

persist_directory = "app/vectorstore"


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
                        metadata={"source": file_path, "page": page_number}
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
    documents = []

    for root, _, files in os.walk(DATA_PATH):
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

    splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(
        docs,
        embedding,
        persist_directory=persist_directory
    )

    vectorstore.persist()

    return vectorstore


def get_context(query: str, category: str = None):
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding
    )

    search_query = query
    if category:
        category_name = category.lower()
        if category_name in CATEGORY_FOLDERS:
            search_query = f"{category} {query}"

    docs = vectorstore.similarity_search(search_query, k=3)

    return "\n".join([
        doc.page_content
        for doc in docs
    ])
