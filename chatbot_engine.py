import streamlit as st
from rag import load_vectorstore
from translator import translate_to_english, translate_from_english, detect_language
from langchain_ollama import OllamaLLM

@st.cache_resource
def load_db():
    return load_vectorstore()

db = load_db()

llm = OllamaLLM(model="llama3")


def build_prompt(context, question, history):
    history_text = ""
    if history:
        for msg in history[-4:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

    return f"""You are a helpful multilingual assistant.

First, try to answer using the context below.
If the context contains the answer, use it and say so.
If the context does NOT contain the answer, use your general knowledge to answer helpfully.
Never say "I don't know" — always try to give a useful response.

Context:
{context}

Conversation so far:
{history_text}
User: {question}
Assistant:"""

def chatbot(query, history=None):
    if history is None:
        history = []

    lang = detect_language(query)
    english_query = translate_to_english(query)

    # MMR retrieval — diverse, non-duplicate chunks
    docs = db.max_marginal_relevance_search(english_query, k=3, fetch_k=10)
    context = "\n\n".join([doc.page_content for doc in docs])[:1500]

    prompt = build_prompt(context, english_query, history)

    response = llm.invoke(prompt)
    response = str(response).strip()

    final_answer = translate_from_english(response, lang)
    return final_answer