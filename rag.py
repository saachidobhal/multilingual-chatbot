import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
FAISS_INDEX_PATH = "faiss_index"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def get_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""]
    )

def load_documents():
    docs = []

    if os.path.exists("data/sample.txt"):
        loader = TextLoader("data/sample.txt")
        docs.extend(loader.load())

    for file in os.listdir("data"):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join("data", file))
            docs.extend(loader.load())

    return docs

def create_vectorstore():
    documents = load_documents()
    splitter = get_splitter()
    docs = splitter.split_documents(documents)
    embeddings = get_embeddings()
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(FAISS_INDEX_PATH)
    print(f"Vectorstore created and saved to '{FAISS_INDEX_PATH}'")
    return db

def load_vectorstore():
    embeddings = get_embeddings()
    if os.path.exists(FAISS_INDEX_PATH):
        print(f"Loading vectorstore from disk: '{FAISS_INDEX_PATH}'")
        db = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        return db
    else:
        print("No saved index found. Building from documents...")
        return create_vectorstore()

def merge_documents_into_db(db, file_bytes, filename):
    """
    Takes raw file bytes + filename, extracts text,
    chunks it, embeds it and merges into the existing FAISS db.
    Supports PDF, TXT, DOCX.
    Returns (updated_db, num_chunks_added)
    """
    import tempfile

    ext = filename.lower().split(".")[-1]
    docs = []

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if ext == "pdf":
            loader = PyPDFLoader(tmp_path)
            docs = loader.load()

        elif ext == "txt":
            loader = TextLoader(tmp_path, encoding="utf-8")
            docs = loader.load()

        elif ext == "docx":
            from docx import Document as DocxDocument
            docx = DocxDocument(tmp_path)
            full_text = "\n".join([p.text for p in docx.paragraphs if p.text.strip()])
            docs = [Document(page_content=full_text, metadata={"source": filename})]

        else:
            raise ValueError(f"Unsupported file type: {ext}")

    finally:
        os.unlink(tmp_path)

    if not docs:
        return db, 0

    # Add filename as metadata source
    for doc in docs:
        doc.metadata["source"] = filename

    splitter = get_splitter()
    chunks = splitter.split_documents(docs)

    embeddings = get_embeddings()
    new_db = FAISS.from_documents(chunks, embeddings)

    # Merge into existing db
    db.merge_from(new_db)
    db.save_local(FAISS_INDEX_PATH)

    return db, len(chunks)