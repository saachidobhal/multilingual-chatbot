import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

FAISS_INDEX_PATH = "faiss_index"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

def get_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""]
    )

def load_documents():
    docs = []

    # Make sure data folder exists
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

    # If no documents found, create a minimal placeholder
    if not docs:
        docs = [Document(
            page_content="This is LinguaBot, a multilingual AI assistant. Upload documents to get started.",
            metadata={"source": "default"}
        )]

    return docs

def create_vectorstore():
    documents = load_documents()
    splitter  = get_splitter()
    docs      = splitter.split_documents(documents)
    embeddings = get_embeddings()
    db = FAISS.from_documents(docs, embeddings)

    # Only save locally — on cloud this is temporary storage
    try:
        db.save_local(FAISS_INDEX_PATH)
        print(f"Vectorstore saved to '{FAISS_INDEX_PATH}'")
    except Exception as e:
        print(f"Could not save index (ok on cloud): {e}")

    return db

def load_vectorstore():
    embeddings = get_embeddings()

    # Try loading from disk first (works locally)
    if os.path.exists(FAISS_INDEX_PATH):
        try:
            print(f"Loading vectorstore from disk: '{FAISS_INDEX_PATH}'")
            db = FAISS.load_local(
                FAISS_INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
            return db
        except Exception as e:
            print(f"Could not load saved index, rebuilding: {e}")

    # Build fresh (always happens on cloud first run)
    print("Building vectorstore from documents...")
    return create_vectorstore()

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

    splitter   = get_splitter()
    chunks     = splitter.split_documents(docs)
    embeddings = get_embeddings()
    new_db     = FAISS.from_documents(chunks, embeddings)

    db.merge_from(new_db)

    try:
        db.save_local(FAISS_INDEX_PATH)
    except Exception as e:
        print(f"Could not save after merge (ok on cloud): {e}")

    return db, len(chunks)