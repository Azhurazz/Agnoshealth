import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Config
SAVE_DIR = "rag_model"
EMBEDDING_MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v2"
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load FAISS index once
@st.cache_resource
def load_index():
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        multi_process=True,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True},
    )
    return FAISS.load_local(
        SAVE_DIR,
        embeddings=embedding_model,
        allow_dangerous_deserialization=True
    )

knowledge_index = load_index()

def answer_with_title(question: str, knowledge_index: FAISS) -> str:
    relevant_docs = knowledge_index.similarity_search(question, k=10)
    if not relevant_docs:
        return "please wait doctor answers"
    best_doc = relevant_docs[0]
    title = best_doc.metadata.get("title", "").strip()
    return title if title else "please wait doctor answers"

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("🧑‍⚕️ Medical Symptom Classifier (RAG)")

# Chat state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box
if prompt := st.chat_input("Describe your symptoms..."):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get RAG answer (title)
    answer = answer_with_title(prompt, knowledge_index)

    # Show assistant answer
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
