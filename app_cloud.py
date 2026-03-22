import streamlit as st
from chatbot_engine_cloud import chatbot, load_store

st.set_page_config(
    page_title="LinguaBot — Multilingual Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

LANG_INFO = {
    "en": ("🇬🇧", "English"),
    "hi": ("🇮🇳", "Hindi"),
    "ta": ("🇮🇳", "Tamil"),
    "bn": ("🇧🇩", "Bengali"),
    "mr": ("🇮🇳", "Marathi"),
    "te": ("🇮🇳", "Telugu"),
    "ur": ("🇵🇰", "Urdu"),
    "gu": ("🇮🇳", "Gujarati"),
    "pa": ("🇮🇳", "Punjabi"),
    "kn": ("🇮🇳", "Kannada"),
    "ml": ("🇮🇳", "Malayalam"),
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp { background: #0f1117; }
section[data-testid="stSidebar"] { background: #141820; border-right: 1px solid #1e2530; padding: 0; }
section[data-testid="stSidebar"] > div { padding: 0; }
.sidebar-header { background: #C2185B; padding: 20px 20px 16px; }
.sidebar-header h2 { color: white; font-size: 15px; font-weight: 600; margin: 0 0 2px 0; }
.sidebar-header p  { color: #FFCDD2; font-size: 11px; margin: 0; }
.cloud-badge { background: #0f2a1a; border: 1px solid #166534; border-radius: 6px; padding: 6px 12px; color: #22c55e; font-size: 11px; margin: 10px 16px 0; text-align: center; }
.sidebar-section { padding: 14px 16px 10px; border-bottom: 1px solid #1e2530; }
.sidebar-section h3 { color: #9ca3af; font-size: 10px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; margin: 0 0 10px 0; }
.lang-chips { display: flex; flex-wrap: wrap; gap: 6px; padding: 2px 0 4px; }
.chip { background: #1a1f2e; border: 1px solid #1e2530; border-radius: 20px; padding: 3px 10px; font-size: 11px; color: #9ca3af; display: inline-block; }
.doc-pill { display: flex; align-items: center; gap: 8px; background: #1a1f2e; border: 1px solid #1e2530; border-radius: 8px; padding: 7px 10px; margin-bottom: 6px; font-size: 12px; color: #d1d5db; }
.doc-pill .doc-icon { color: #4f8ef7; font-size: 14px; }
.doc-pill .doc-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.doc-pill .doc-chunks { color: #6b7280; font-size: 10px; white-space: nowrap; }
.success-banner { background: #0f2a1a; border: 1px solid #166534; border-radius: 8px; padding: 8px 12px; color: #22c55e; font-size: 12px; margin-top: 8px; }
.error-banner { background: #2a0f0f; border: 1px solid #991b1b; border-radius: 8px; padding: 8px 12px; color: #f87171; font-size: 12px; margin-top: 8px; }
.kb-stat { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 12px; color: #6b7280; border-bottom: 1px solid #1a1f2e; }
.kb-stat span:last-child { color: #d1d5db; font-weight: 500; }
.header-bar { background: #141820; border-bottom: 1px solid #1e2530; padding: 14px 32px; display: flex; align-items: center; justify-content: space-between; }
.header-logo { font-size: 18px; font-weight: 600; color: #e8eaf0; letter-spacing: -0.3px; }
.header-logo span { color: #4f8ef7; }
.header-status { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #6b7280; }
.status-dot { width: 8px; height: 8px; background: #22c55e; border-radius: 50%; animation: pulse 2s infinite; display: inline-block; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
.chat-wrapper { max-width: 800px; margin: 0 auto; padding: 28px 20px 130px; }
.msg-row { display: flex; margin-bottom: 18px; gap: 10px; animation: fadeUp 0.3s ease; }
@keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.msg-row.user { flex-direction: row-reverse; }
.avatar { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; margin-top: 2px; font-weight: 600; }
.avatar.bot  { background: #1e2d4a; color: #4f8ef7; }
.avatar.user { background: #1a2a1a; color: #22c55e; }
.bubble-wrap { display: flex; flex-direction: column; max-width: 74%; }
.msg-row.user .bubble-wrap { align-items: flex-end; }
.bubble { padding: 11px 15px; border-radius: 12px; font-size: 14px; line-height: 1.65; word-break: break-word; }
.bubble.bot  { background: #141820; border: 1px solid #1e2530; color: #d1d5db; border-radius: 4px 12px 12px 12px; }
.bubble.user { background: #1a3a5c; border: 1px solid #1e4a7a; color: #e2eeff; border-radius: 12px 4px 12px 12px; }
.lang-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 10px; color: #6b7280; margin-top: 4px; padding: 2px 8px; background: #1a1f2e; border-radius: 20px; border: 1px solid #1e2530; }
.typing-indicator { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; animation: fadeUp 0.3s ease; }
.typing-dots { display: flex; gap: 5px; padding: 13px 16px; background: #141820; border: 1px solid #1e2530; border-radius: 4px 12px 12px 12px; }
.typing-dots span { width: 6px; height: 6px; background: #4f8ef7; border-radius: 50%; animation: bounce 1.2s infinite; }
.typing-dots span:nth-child(2){animation-delay:.2s} .typing-dots span:nth-child(3){animation-delay:.4s}
@keyframes bounce { 0%,60%,100%{transform:translateY(0);opacity:.4} 30%{transform:translateY(-6px);opacity:1} }
.welcome-card { background: #141820; border: 1px solid #1e2530; border-radius: 16px; padding: 36px; text-align: center; margin: 50px auto; max-width: 460px; }
.welcome-card h2 { font-size: 20px; font-weight: 600; color: #e8eaf0; margin-bottom: 8px; }
.welcome-card p  { font-size: 13px; color: #6b7280; line-height: 1.6; margin: 0; }
.input-area { position: fixed; bottom: 0; left: 0; right: 0; background: #0f1117; border-top: 1px solid #1e2530; padding: 14px 20px 18px; z-index: 99; }
.stTextInput > div > div > input { background: #141820 !important; border: 1px solid #1e2530 !important; border-radius: 10px !important; color: #e8eaf0 !important; font-family: 'DM Sans', sans-serif !important; font-size: 14px !important; padding: 11px 15px !important; caret-color: #4f8ef7; }
.stTextInput > div > div > input:focus { border-color: #4f8ef7 !important; box-shadow: 0 0 0 3px rgba(79,142,247,0.12) !important; }
.stTextInput > div > div > input::placeholder { color: #4b5563 !important; }
.stButton > button { background: #4f8ef7 !important; color: white !important; border: none !important; border-radius: 10px !important; padding: 11px 20px !important; font-family: 'DM Sans', sans-serif !important; font-size: 13px !important; font-weight: 500 !important; transition: background 0.2s !important; }
.stButton > button:hover { background: #3b7af0 !important; }
div[data-testid="stSpinner"] { display: none; }
[data-testid="stFileUploader"] { background: #1a1f2e !important; border: 1px dashed #1e4a7a !important; border-radius: 10px !important; padding: 8px !important; }
[data-testid="stFileUploader"] label { color: #9ca3af !important; font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──
if "messages"      not in st.session_state: st.session_state.messages = []
if "thinking"      not in st.session_state: st.session_state.thinking = False
if "uploaded_docs" not in st.session_state: st.session_state.uploaded_docs = []
if "upload_msg"    not in st.session_state: st.session_state.upload_msg = None
if "upload_ok"     not in st.session_state: st.session_state.upload_ok = True
if "input_key"     not in st.session_state: st.session_state.input_key = 0

# Load doc store once
store = load_store()

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2>LinguaBot</h2>
        <p>Multilingual AI Assistant</p>
    </div>
    <div class="cloud-badge">Powered by HuggingFace — Cloud Version</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
        <h3>Supported Languages</h3>
        <div class="lang-chips">
            <span class="chip">🇮🇳 Hindi</span>
            <span class="chip">🇮🇳 Tamil</span>
            <span class="chip">🇧🇩 Bengali</span>
            <span class="chip">🇮🇳 Marathi</span>
            <span class="chip">🇮🇳 Telugu</span>
            <span class="chip">🇮🇳 Gujarati</span>
            <span class="chip">🇮🇳 Punjabi</span>
            <span class="chip">🇮🇳 Kannada</span>
            <span class="chip">🇮🇳 Malayalam</span>
            <span class="chip">🇵🇰 Urdu</span>
            <span class="chip">🇬🇧 English</span>
            <span class="chip">🔀 Hinglish</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section"><h3>Add Document</h3>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        label="", type=["pdf", "txt", "docx"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        already = any(d["name"] == uploaded_file.name for d in st.session_state.uploaded_docs)
        if not already:
            if st.button("Add to Knowledge Base", use_container_width=True):
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    try:
                        file_bytes = uploaded_file.read()
                        num_chunks = store.add(file_bytes, uploaded_file.name)
                        st.session_state.uploaded_docs.append({
                            "name":   uploaded_file.name,
                            "chunks": num_chunks,
                            "type":   uploaded_file.name.split(".")[-1].upper()
                        })
                        st.session_state.upload_msg = f"Added {num_chunks} chunks from {uploaded_file.name}"
                        st.session_state.upload_ok  = True
                    except Exception as e:
                        st.session_state.upload_msg = f"Error: {str(e)}"
                        st.session_state.upload_ok  = False
                st.rerun()
        else:
            st.markdown('<div class="error-banner">Already in knowledge base.</div>', unsafe_allow_html=True)

    if st.session_state.upload_msg:
        css_class = "success-banner" if st.session_state.upload_ok else "error-banner"
        st.markdown(f'<div class="{css_class}">{st.session_state.upload_msg}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.uploaded_docs:
        st.markdown('<div class="sidebar-section"><h3>Uploaded Documents</h3>', unsafe_allow_html=True)
        icons = {"PDF": "📄", "TXT": "📝", "DOCX": "📘"}
        for doc in st.session_state.uploaded_docs:
            icon = icons.get(doc["type"], "📎")
            st.markdown(f"""
            <div class="doc-pill">
                <span class="doc-icon">{icon}</span>
                <span class="doc-name">{doc["name"]}</span>
                <span class="doc-chunks">{doc["chunks"]} chunks</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section"><h3>Stats</h3>', unsafe_allow_html=True)
    total_docs   = len(st.session_state.uploaded_docs)
    total_chunks = sum(d["chunks"] for d in st.session_state.uploaded_docs)
    st.markdown(f"""
    <div class="kb-stat"><span>Session uploads</span><span>{total_docs} files</span></div>
    <div class="kb-stat"><span>Chunks added</span><span>{total_chunks}</span></div>
    <div class="kb-stat"><span>Model</span><span>Mistral 7B (HF)</span></div>
    <div class="kb-stat"><span>Search</span><span>Keyword</span></div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thinking = False
        st.session_state.input_key += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# MAIN CHAT
# ══════════════════════════════════════════════
st.markdown("""
<div class="header-bar">
    <div class="header-logo">Lingua<span>Bot</span></div>
    <div class="header-status">
        <div class="status-dot"></div>
        HuggingFace &middot; Cloud
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h2>Multilingual Assistant</h2>
        <p>Ask me anything in your language. Upload documents from the sidebar to expand my knowledge.</p>
    </div>
    """, unsafe_allow_html=True)

from translator import detect_language

for msg in st.session_state.messages:
    if msg["role"] == "user":
        lang_code = detect_language(msg["content"])
        flag, lang_name = LANG_INFO.get(lang_code, ("🌐", lang_code.upper()))
        st.markdown(f"""
        <div class="msg-row user">
            <div class="avatar user">U</div>
            <div class="bubble-wrap">
                <div class="bubble user">{msg["content"]}</div>
                <div class="lang-badge">{flag} {lang_name}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row">
            <div class="avatar bot">AI</div>
            <div class="bubble-wrap">
                <div class="bubble bot">{msg["content"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if st.session_state.thinking:
    st.markdown("""
    <div class="typing-indicator">
        <div class="avatar bot">AI</div>
        <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="input-area">', unsafe_allow_html=True)
col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.text_input(
        label="", placeholder="Type in any language...",
        key=f"input_{st.session_state.input_key}",
        label_visibility="collapsed"
    )
with col2:
    send = st.button("Send", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    st.session_state.thinking  = True
    st.session_state.upload_msg = None
    st.session_state.input_key += 1
    st.rerun()

if st.session_state.thinking:
    history    = st.session_state.messages[:-1]
    last_query = st.session_state.messages[-1]["content"]
    response   = chatbot(last_query, history=history)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.thinking = False
    st.rerun()