import requests
import streamlit as st
from retriever import DocStore
from translator import translate_to_english, translate_from_english, detect_language

HF_TOKEN = st.secrets["HF_TOKEN"]
API_URL  = "https://router.huggingface.co/novita/v3/openai/chat/completions"
HEADERS  = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type":  "application/json"
}

@st.cache_resource
def load_store():
    return DocStore().build()

def query_hf(prompt):
    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "messages": [
            {
                "role":    "system",
                "content": "You are a helpful multilingual assistant. Answer clearly and concisely."
            },
            {
                "role":    "user",
                "content": prompt
            }
        ],
        "max_tokens":  512,
        "temperature": 0.3
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)

        if response.status_code != 200:
            return f"API error {response.status_code}: {response.text[:200]}"

        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        elif "error" in result:
            return f"Model error: {result['error']}"
        else:
            return f"Unexpected response: {str(result)[:200]}"

    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."
    except Exception as e:
        return f"Connection error: {str(e)}"

def build_prompt(context, question, history):
    history_text = ""
    if history:
        for msg in history[-4:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

    return f"""Answer the question below using the context if relevant. If the context doesn't help, use your general knowledge.

Context:
{context}

{history_text}
User: {question}"""

def chatbot(query, history=None):
    if history is None:
        history = []

    store         = load_store()
    lang          = detect_language(query)
    english_query = translate_to_english(query)

    docs    = store.search(english_query, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])[:1500]

    prompt   = build_prompt(context, english_query, history)
    response = query_hf(prompt)

    return translate_from_english(response, lang)