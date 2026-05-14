from langchain_community.document_loaders import TextLoader

from langchain_text_splitters import CharacterTextSplitter

from langchain_community.vectorstores import Chroma

from langchain_community.embeddings import HuggingFaceEmbeddings

import os

import os


DATA_PATH = "app/data/grammar"


embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

persist_directory = "app/vectorstore"


def build_vectorstore():

    documents = []

    for file in os.listdir(DATA_PATH):

        if file.endswith(".txt"):

            loader = TextLoader(
                os.path.join(DATA_PATH, file),
                encoding="utf-8"
            )

            documents.extend(loader.load())

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


def get_context(query: str):

    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding
    )

    docs = vectorstore.similarity_search(query, k=3)

    return "\n".join([
        doc.page_content
        for doc in docs
    ])