import os
import requests
import streamlit as st
from rag import load_vectorstore
from translator import translate_to_english, translate_from_english, detect_language

HF_TOKEN = st.secrets["HF_TOKEN"]
API_URL   = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS   = {"Authorization": f"Bearer {HF_TOKEN}"}

@st.cache_resource
def load_db():
    return load_vectorstore()

db = load_db()

def query_hf(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.3,
            "return_full_text": False,
            "stop": ["User:", "\nUser"]
        }
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
        result   = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"].strip()
        elif isinstance(result, dict) and "error" in result:
            # Model may be loading — retry message
            if "loading" in str(result.get("error", "")).lower():
                return "The AI model is warming up. Please try again in 20 seconds."
            return f"Model error: {result['error']}"
        else:
            return "Sorry, I could not generate a response. Please try again."
    except Exception as e:
        return f"Connection error: {str(e)}"

def build_prompt(context, question, history):
    history_text = ""
    if history:
        for msg in history[-4:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

    return f"""<s>[INST] You are a helpful multilingual assistant.

First try to answer using the context below.
If the context contains the answer, use it.
If not, use your general knowledge to answer helpfully.
Never say "I don't know" — always give a useful response.
Be concise and clear.

Context:
{context}

Conversation so far:
{history_text}
User: {question} [/INST]"""

def chatbot(query, history=None):
    if history is None:
        history = []

    lang          = detect_language(query)
    english_query = translate_to_english(query)

    # Use similarity_search instead of MMR — works with all embedding types
    docs    = db.similarity_search(english_query, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])[:1500]

    prompt   = build_prompt(context, english_query, history)
    response = query_hf(prompt)

    final_answer = translate_from_english(response, lang)
    return final_answer