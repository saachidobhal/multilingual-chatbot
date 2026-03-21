import os
import re
import streamlit as st
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# ── Simple in-memory document store ──
# No FAISS, no embeddings, no model downloads
# Uses keyword matching — reliable on any server

def get_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""]
    )

def load_documents():
    docs = []

    if not os.path.exists("data"):
        os.makedirs("data")

    if os.path.exists("data/sample.txt"):
        try:
            loader = TextLoader("data/sample.txt", encoding="utf-8")
            docs.extend(loader.load())
        except Exception as e:
            print(f"Could not load sample.txt: {e}")

    for file in os.listdir("data"):
        if file.endswith(".pdf"):
            try:
                loader = PyPDFLoader(os.path.join("data", file))
                docs.extend(loader.load())
            except Exception as e:
                print(f"Could not load {file}: {e}")

    if not docs:
        docs = [Document(
            page_content="This is LinguaBot, a multilingual AI assistant. Upload documents to get started.",
            metadata={"source": "default"}
        )]

    return docs

class SimpleDocStore:
    """
    Lightweight document store using keyword search.
    No FAISS, no embeddings, no downloads — works everywhere.
    """

    def __init__(self, chunks):
        self.chunks = chunks

    def _score(self, query, text):
        query_words = set(re.findall(r'\w+', query.lower()))
        text_words  = set(re.findall(r'\w+', text.lower()))
        if not query_words:
            return 0
        overlap = query_words & text_words
        return len(overlap) / len(query_words)

    def similarity_search(self, query, k=3):
        scored = [
            (self._score(query, chunk.page_content), chunk)
            for chunk in self.chunks
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored[:k]]

    def merge_chunks(self, new_chunks):
        self.chunks.extend(new_chunks)


def load_vectorstore():
    documents = load_documents()
    splitter  = get_splitter()
    chunks    = splitter.split_documents(documents)
    print(f"Loaded {len(chunks)} chunks from documents")
    return SimpleDocStore(chunks)


def merge_documents_into_db(db, file_bytes, filename):
    import tempfile

    ext  = filename.lower().split(".")[-1]
    docs = []

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if ext == "pdf":
            loader = PyPDFLoader(tmp_path)
            docs   = loader.load()
        elif ext == "txt":
            loader = TextLoader(tmp_path, encoding="utf-8")
            docs   = loader.load()
        elif ext == "docx":
            from docx import Document as DocxDocument
            docx      = DocxDocument(tmp_path)
            full_text = "\n".join([p.text for p in docx.paragraphs if p.text.strip()])
            docs      = [Document(page_content=full_text, metadata={"source": filename})]
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    finally:
        os.unlink(tmp_path)

    if not docs:
        return db, 0

    for doc in docs:
        doc.metadata["source"] = filename

    splitter = get_splitter()
    chunks   = splitter.split_documents(docs)
    db.merge_chunks(chunks)

    return db, len(chunks)